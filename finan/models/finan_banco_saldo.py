# -*- coding: utf-8 -*-
#
# Copyright 2017 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

from odoo import api, fields, models
from odoo.addons.l10n_br_base.models.sped_base import SpedBase
from ..constantes import *


SQL_FINAN_BANCO_SALDO_FUNCTION = '''
drop function if exists finan_banco_saldo_function(integer);
create or replace function finan_banco_saldo_function(_banco_id integer)
    returns table(
        data date,
        entrada numeric,
        saida numeric,
        saldo numeric
    ) as
    $BODY$
        declare
            ultima_data date := '2000-01-01';

        begin
            saldo := 0;

            --
            -- Primeiro, trazemos os saldos que já estão salvos
            --
            for
                data,
                entrada,
                saida,
                saldo

            in
            select
                fbs.data,
                fbs.entrada,
                fbs.saida,
                fbs.saldo

            from
                finan_banco_saldo fbs

            where
                fbs.banco_id = _banco_id

            order by
                fbs.data

            loop
                ultima_data := data;
                return next;
            end loop;

            --
            -- Agora recalculamos da última data em diante
            --
            for
                data,
                entrada,
                saida

            in
            select
                fbe.data,
                sum(fbe.entrada) as entrada,
                sum(fbe.saida) as saida

            from
                finan_banco_extrato fbe

            where
                fbe.banco_id = _banco_id
                and fbe.data > ultima_data

            group by
                fbe.data

            order by
                fbe.data

            loop
                saldo := coalesce(saldo, 0) + entrada - saida;
                return next;
            end loop;
        end
    $BODY$
LANGUAGE plpgsql VOLATILE;
'''

SQL_INDICES = '''
create index if not exists finan_banco_saldo_banco_id_data_index
    on finan_banco_saldo (banco_id, data);
'''


class FinanBancoSaldo(SpedBase, models.Model):
    _name = b'finan.banco.saldo'
    _description = 'Saldos de Contas Bancárias'
    #_rec_name = 'nome'
    _order = 'banco_id, data'

    banco_id = fields.Many2one(
        comodel_name='finan.banco',
        string='Banco/caixa',
        index=True,
        ondelete='restrict',
    )
    tipo = fields.Selection(
        selection=FINAN_TIPO_CONTA_BANCARIA,
        string='Tipo',
        related='banco_id.tipo',
    )
    data = fields.Date(
        string='Data',
        index=True,
    )
    entrada = fields.Monetary(
        string='Entrada',
    )
    saida = fields.Monetary(
        string='Saída',
    )
    saldo = fields.Monetary(
        string='Saldo',
    )

    @api.model_cr
    def init(self):
        self.env.cr.execute(SQL_FINAN_BANCO_SALDO_FUNCTION)
        self.env.cr.execute(SQL_INDICES)

    def ajusta_saldo(self, banco_id, data):
        sql = '''
        delete from finan_banco_saldo fbs
        where
            fbs.banco_id = %(banco_id)s
            and fbs.data >= %(data)s;

        insert into finan_banco_saldo (
            banco_id,
            data,
            entrada,
            saida,
            saldo
        )
        select
            %(banco_id)s as banco_id,
            fbsf.data,
            fbsf.entrada,
            fbsf.saida,
            fbsf.saldo
        from
            finan_banco_saldo_function(%(banco_id)s) fbsf
        where
            fbsf.data >= %(data)s;
        '''
        filtros = {
            'banco_id': banco_id,
            'data': data,
        }
        self.env.cr.execute(sql, filtros)
