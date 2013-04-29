# -*- coding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2011  Vinicius Dittgen - PROGE, Leonardo Santagada - PROGE      #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU General Public License for more details.                                   #
#                                                                               #
#You should have received a copy of the GNU General Public License              #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from osv import osv, fields
from pyboleto.bank.real import BoletoReal
from pyboleto.bank.bradesco import BoletoBradesco
from pyboleto.bank.caixa import BoletoCaixa
from pyboleto.bank.bancodobrasil import BoletoBB
from pyboleto.pdf import BoletoPDF
from datetime import datetime, date

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class boleto_create(osv.osv_memory):
    """ Generate Brazilian Boletos """

    _name = 'boleto.boleto_create'

    def _get_company_config_ids(self, cr, uid, context=None):
        ret = []
        if context is None:
            context = {}
        if context.has_key("active_ids"):
            active_ids = context.get('active_ids', [])[0]
            invoice = self.pool.get('account.invoice').browse(cr, uid, active_ids, context=context)
            company = self.pool.get('res.company').browse(cr, uid, [invoice.company_id.id])[0]
            for bol_conf_id in company.boleto_company_config_ids:
                bc = bol_conf_id.id, bol_conf_id.name
                ret.append(bc)

        return ret

    _columns = {
        'boleto_company_config_ids': fields.selection(_get_company_config_ids, u'Configuração dos Boletos', required=True),
        'file': fields.binary('Arquivo', readonly=True),
        'state': fields.selection([('init', 'init'),
                               ('done', 'done')], 'state', readonly=True),
        }

    _defaults = {
        'state': 'init',
        }

    def create_boleto(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        bol_conf_id = data['boleto_company_config_ids']
        inv_obj = self.pool.get('account.invoice')
        boleto_obj = self.pool.get('boleto.boleto')
        active_ids = context.get('active_ids', [])
        boleto_ids = []

        for invoice in inv_obj.browse(cr, uid, active_ids, context=context):
            company = self.pool.get('res.company').browse(cr, uid, [invoice.company_id.id])[0]
            partner = self.pool.get('res.partner').browse(cr, uid, [invoice.partner_id.id])[0]
            bol_conf = self.pool.get('boleto.company_config').browse(cr, uid, [bol_conf_id])[0]

            if invoice.state in ['proforma2', 'open', 'sefaz_export']:
                rec_ids = invoice._get_receivable_lines(active_ids, False)
                for move_line in self.pool.get('account.move.line').browse(cr, uid, rec_ids[invoice.id]):
                    boleto = {
                    'name': invoice.number + '-' + str(move_line.id),
                    'carteira': partner.boleto_partner_config.carteira,
                    'cedente': company.id,
                    'sacado': partner.id,
#                    'juros': partner.boleto_partner_config.juros,
#                    'multa': partner.boleto_partner_config.multa,
                    'instrucoes': partner.boleto_partner_config.instrucoes,
                    'banco': bol_conf.banco,
                    'agencia_cedente': bol_conf.agencia_cedente,
                    'conta_cedente': bol_conf.conta_cedente,
                    'convenio': bol_conf.convenio,
                    'nosso_numero': move_line.id,
                    'move_line_id': move_line.id,
                    'data_vencimento': move_line.date_maturity or date.today(),
                    'data_documento': move_line.date_created,
                    'valor': move_line.debit,
                    'numero_documento': move_line.id,
                    'endereco': invoice.address_invoice_id.id
                    }
                    boleto_id = boleto_obj.create(cr, uid, boleto, context)
                    boleto_ids.append(boleto_id)
        boleto_file = self.gen_boleto(cr, uid, ids, boleto_ids, context)
        self.write(cr, uid, ids, {'file': boleto_file, 'state': 'done'}, context=context)

        return False

    def gen_boleto(self, cr, uid, ids, boleto_ids, context=None):
        boleto_obj = self.pool.get('boleto.boleto')
        fbuffer = StringIO()
        boleto_pdf = BoletoPDF(fbuffer)

        for bol in boleto_obj.browse(cr, uid, boleto_ids, context=context):
            partner_ad = bol.sacado.address[0]

            if bol.banco == 'bb':
                boleto = BoletoBB(7, 2)
            elif bol.banco == 'bradesco':
                boleto = BoletoBradesco()
            elif bol.banco == 'caixa':
                boleto = BoletoCaixa()
            elif bol.banco == 'real':
                boleto = BoletoReal()

            boleto.cedente = bol.cedente.name
            boleto.carteira = bol.carteira
            boleto.agencia_cedente = bol.agencia_cedente
            boleto.conta_cedente = bol.conta_cedente
            boleto.data_vencimento = datetime.date(datetime.strptime(bol.data_vencimento, '%Y-%m-%d'))
            boleto.data_documento = datetime.date(datetime.strptime(bol.data_documento, '%Y-%m-%d'))
            boleto.data_processamento = date.today()
            boleto.valor_documento = bol.valor
            boleto.nosso_numero = bol.numero_documento
            boleto.numero_documento = bol.numero_documento
            boleto.convenio = bol.convenio
            boleto.instrucoes = bol.instrucoes.split('\n')
            boleto.sacado = [
                "%s" % bol.sacado.legal_name or bol.sacado.name,
                "%s, %s - %s - %s - Cep. %s" % (partner_ad.street, partner_ad.number, partner_ad.district, partner_ad.city, partner_ad.zip),
                ""
                ]

            boleto_pdf.drawBoleto(boleto)
            boleto_pdf.nextPage()

        boleto_pdf.save()
        boleto_file = fbuffer.getvalue().encode("base64")
        fbuffer.close()
        return boleto_file

boleto_create()
