# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen - Portugal & Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import netsvc
from tools.translate import _
from osv import osv, fields

from datetime import datetime, date
from decimal import Decimal, Context, Inexact
from itertools import count
import logging
import base64
import re

def counter(start=0):
    try:
        return count(start=start)
    except TypeError:
        c = count()
        c.next()
        return c

if hasattr(Decimal, 'from_float'):
    float_to_decimal = Decimal.from_float
else:
    def float_to_decimal(f):
        "Convert a floating point number to a Decimal with no loss of information"
        n, d = f.as_integer_ratio()
        numerator, denominator = Decimal(n), Decimal(d)
        ctx = Context(prec=60)
        result = ctx.divide(numerator, denominator)
        while ctx.flags[Inexact]:
            ctx.flags[Inexact] = False
            ctx.prec *= 2
            result = ctx.divide(numerator, denominator)
        return result


class CNABExporter(osv.osv_memory):
    _name = 'cnab.wizard.exporter'
    _inherit = 'cnab.wizard.exporter'
    
    def _round(self, v):
        v = float_to_decimal(v)
        return (v * Decimal('100')).quantize(1)
    
    def _only_digits(self, v):
        return re.sub('[^0-9]', '', v)
    
    def _get_address(self, partner):
        parts = []
        if partner.street:
            parts.append(partner.street)
        if partner.street2:
            parts.append(partner.street2)
        return ",".join(parts)
    
    def _header(self, cr, user):
        cnab_info = user.company_id.cnab_info_id
        assert cnab_info != False, "Company must have CNAB information"
        return {
                'IDReg': '0',
                'CodigoEmpresa': cnab_info.codigo_empresa,
                'NomeEmpresa': user.company_id.name,
                'DataGravacaoArquivo': date.today(),
                'NroSequencialArquivo': self.pool.get('ir.sequence').get(cr, user.id, 'cnab.bradesco.remessa.sequence'),
               }
    
    def _invoice(self, user, invoice):
        partner_cnab_info = invoice.partner_id.cnab_info_id
        assert partner_cnab_info != False, "Partner must have CNAB information"
        company_cnab_info = user.company_id.cnab_info_id
        assert company_cnab_info != False, "Company must have CNAB information"
        rateio_credito = ("R" if company_cnab_info.rateio_credito else " ")
        identificacao_inscricao_sacado = ('01' if not invoice.partner_id.is_company else '02')
        return [{
                'IDReg': '1',
                'AgenciaDebito': partner_cnab_info.codigo_agencia,
                'DigitoAgenciaDebito': partner_cnab_info.digito_agencia,
                'RazaoContaCorrenteDebito': partner_cnab_info.razao_conta,
                'ContaCorrenteDebito': partner_cnab_info.numero_conta,
                'DigitoContaCorrenteDebito': partner_cnab_info.digito_conta,
                'Carteira': company_cnab_info.codigo_carteira,
                'AgenciaCedente': company_cnab_info.codigo_agencia,
                'ContaCorrente': company_cnab_info.numero_conta,
                'DigitoContaCorrente': company_cnab_info.digito_conta,
                'NroControleParticipante': invoice.id,
                'Multa': 0, #FIXME
                'PercentagemMulta': 0, #FIXME
                'NossoNumero': 0, #FIXME
                'EmissaoPapeletaCobranca': company_cnab_info.emissao_papeleta,
                'EmissaoPapeletaDebitoAutomatico': company_cnab_info.registro_debito_automatico,
                'IndicadorRateioCredito': rateio_credito,
                'AvisoDebitoAutomatico': company_cnab_info.aviso_debito_automatico,
                'NDocumento': invoice.number,
                'DataVencimentoTitulo': datetime.strptime(invoice.date_due, '%Y-%m-%d'),
                'ValorTitulo': self._round(invoice.amount_total),
                'EspecieTitulo': 1, #FIXME
                'Identificacao': 'N', #FIXME
                'DataEmissaoTitulo': date.today(),
                '1Instrucao': 0, #FIXME
                '2Instrucao': 0, #FIXME
                'MoraDiaria': 0, #FIXME
                'DataLimiteDesconto': date(2013, 05, 15), #FIXME
                'ValorDesconto': 0, #FIXME
                'ValorAbatimento': 0, #FIXME
                'IdentificacaoInscricaoSacado': identificacao_inscricao_sacado,
                'NInscricaoSacado': self._only_digits(invoice.partner_id.cnpj_cpf),
                'NomeSacado': invoice.partner_id.name,
                'EnderecoCompleto': self._get_address(invoice.partner_id),
                '1Mensagem': invoice.comment,
                'Cep': invoice.partner_id.zip,
                'Avalista-2Mensagem': ' ', #FIXME
               }, {
                'IDReg': '2',
                'Mensagem1': ' ', #FIXME
                'Mensagem2': ' ', #FIXME
                'Mensagem3': ' ', #FIXME
                'Mensagem4': ' ', #FIXME
                'Filler': ' ', #?
                'Carteira': company_cnab_info.codigo_carteira,
                'Agencia': company_cnab_info.codigo_agencia,
                'ContaCorrente': company_cnab_info.numero_conta,
                'DigitoCC': company_cnab_info.digito_conta,
                'NossoNumero': 0, #FIXME
               }]
    
    def _trailer(self):
        return {'IDReg': '9'}
    
    def prepare_data(self, cr, uid, format, bank, invoice_ids):
        invoice_pool = self.pool.get('account.invoice')
        [user] = self.pool.get('res.users').browse(cr, uid, [uid])
        
        lines = [self._header(cr, user)]
        for invoice in invoice_pool.browse(cr, uid, invoice_ids):
            lines.extend(self._invoice(user, invoice))
        lines.append(self._trailer())
        
        #add sequence numbers
        for i, line in zip(counter(start=1), lines):
            line['NroSequencialRegistro'] = i
            
        return lines
