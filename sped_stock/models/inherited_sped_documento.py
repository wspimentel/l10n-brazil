# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import division, print_function, unicode_literals

from odoo import api, fields, models, _
from odoo.addons.l10n_br_base.constante_tributaria import *


class SpedDocumento(models.Model):
    _inherit = 'sped.documento'

    stock_picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Transferência de Estoque',
        copy=False,
    )

    @api.multi
    def action_view_picking(self):
        action = \
            self.env.ref('stock.action_picking_tree_all').read()[0]

        if self.stock_picking_id:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = self.stock_picking_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

    def _confirma_estoque(self):
        self.ensure_one()
        sql_confirma_estoque = '''
        update stock_picking set state = 'done' where id = %(picking_id)s;
        update stock_move set state = 'done' where picking_id = %(picking_id)s;
        update stock_pack_operation set qty_done = product_qty where picking_id = %(picking_id)s;
        '''
        #
        # Vamos concluir a entrega
        #
        if self.stock_picking_id:
            #
            # Leva o DANFE para o picking
            #
            if self.arquivo_pdf_id:
                pdf_anexo = self.arquivo_pdf_id
                nome_arquivo = pdf_anexo.datas_fname
                pdf = pdf_anexo.datas.decode('base64')
                self.stock_picking_id._grava_anexo(
                    nome_arquivo=nome_arquivo,
                    conteudo=pdf,
                    tipo='application/pdf',
                    model='stock.picking',
                )

            if self.stock_picking_id.state == 'draft':
                self.stock_picking_id.action_confirm()
                self.stock_picking_id.force_assign()

            #
            # Confirmando todas as saídas
            #
            for pack in self.stock_picking_id.pack_operation_ids:
                if pack.product_qty > 0:
                    pack.write({'qty_done': pack.product_qty})
                else:
                    pack.unlink()

            self.stock_picking_id.action_done()
            #self.stock_picking_id.state = 'done'

    def _cancela_estoque(self):
        sql_cancela_estoque = '''
        -- update stock_picking set state = 'cancel' where id = %(picking_id)s;
        delete from stock_pack_operation where picking_id = %(picking_id)s;
        update stock_move set state = 'cancel' where picking_id = %(picking_id)s;
        '''
        sql_cancela_quant = '''
        --
        -- Apaga os stock_quant
        --
        delete from stock_quant where id in
            (select
                sqm.quant_id
            from
                stock_quant_move_rel sqm
            where
                sqm.move_id = %(move_id)s
            );
        '''
        #
        # Vamos cancelar a venda?
        #
        if self.stock_picking_id:
            #
            # Leva o DANFE para o picking
            #
            if self.arquivo_pdf_id:
                pdf_anexo = self.arquivo_pdf_id
                nome_arquivo = pdf_anexo.datas_fname
                pdf = pdf_anexo.datas.decode('base64')
                self.stock_picking_id._grava_anexo(
                    nome_arquivo=nome_arquivo,
                    conteudo=pdf,
                    tipo='application/pdf',
                    model='stock.picking',
                )

            #
            # Para cancelar, precisamos forçar os moves para draft pelo banco,
            # e excluir os stock_quant, pois o core não permite cancelamento
            # depois da confirmação, e não tem recurso para isso
            #
            for move in self.stock_picking_id.move_lines:
                self.env.cr.execute(sql_cancela_quant, {'move_id': move.id})

            self.env.cr.execute(sql_cancela_estoque,
                                {'picking_id': self.stock_picking_id.id})
            self.stock_picking_id.action_cancel()

    def executa_depois_autorizar(self):
        self.ensure_one()
        super(SpedDocumento, self).executa_depois_autorizar()
        self._confirma_estoque()

    def executa_depois_cancelar(self):
        self.ensure_one()
        super(SpedDocumento, self).executa_depois_cancelar()
        self._cancela_estoque()

    def executa_depois_inutilizar(self):
        self.ensure_one()
        super(SpedDocumento, self).executa_depois_inutilizar()
        self._cancela_estoque()

    def executa_depois_denegar(self):
        self.ensure_one()
        super(SpedDocumento, self).executa_depois_denegar()
        self._cancela_estoque()

    def _criar_picking(self):
        stock_obj = self.env['stock.picking']
        for documento in self:
            doc_picking_type = documento.operacao_id.stock_picking_type_id
            move_lines = []
            for line in documento.item_ids:
                vals_produtos = [0, False, {
                    'produto_id': line.produto_id.id,
                    'product_uom': 1,
                    'product_uom_qty': line.quantidade,
                    'name': "[" + line.produto_id.codigo + "] " +
                            line.produto_id.nome,
                    'date_expected': documento.data_hora_entrada_saida,
                    'location_id': doc_picking_type.default_location_src_id.id,
                    'location_dest_id':
                        doc_picking_type.default_location_dest_id.id,
                }]
                move_lines.append(vals_produtos)
            vals = {
                'partner_id': documento.participante_id.partner_id.id,
                'participante_id': documento.participante_id.id,
                'min_date': documento.data_hora_entrada_saida,
                'origin': 'NFe-' + str(documento.numero)[:-2],
                'company_id': documento.empresa_id.company_id.id,
                'empresa_id': documento.empresa_id.id,
                'picking_type_id': doc_picking_type.id,
                'location_id': doc_picking_type.default_location_src_id.id,
                'location_dest_id':
                    doc_picking_type.default_location_dest_id.id,
                'move_lines': move_lines,
            }
            res = stock_obj.create(vals)
            documento.stock_picking_id = res.id
            documento._confirma_estoque()

    def executa_depois_create(self, result, dados):
        result = super(SpedDocumento, self).executa_depois_create(
            result, dados)

        for documento in self:
            if documento.entrada_saida == ENTRADA_SAIDA_ENTRADA:
                documento._criar_picking()

        return result
