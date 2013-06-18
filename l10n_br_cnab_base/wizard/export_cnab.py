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

import logging
import base64
import datetime
#from collections import OrderedDict

from generator import CNABGenerator

class CNABExporter(osv.osv_memory):
    _name = 'cnab.wizard.exporter'
    
    def prepare_data(self, cr, uid, format, bank, invoice_ids):
        #to be overridden by subclasses
        return {}
    
    def load_format(self, cr, uid):
        pool = self.pool.get('cnab.file_format')
        try:
            format_id = pool.search(cr, uid, [('type', '=', 'Arquivo-Remessa')])
            [format] = pool.browse(cr, uid, format_id)
            return format
        except ValueError:
            raise osv.except_osv('Error', 'CNAB File format for Arquivo-Remessa not found')
        return format
    
    def serialize(self, cr, uid, format, data):
#        fake_data = [OrderedDict([(u'IDReg', '0'), (u'IdentificacaoRemessa', 1), (u'LiteralRemessa', 'REMESSA'), (u'CodigoServico', 1), (u'LiteralServico', 'COBRANCA'), (u'CodigoEmpresa', 74017), (u'NomeEmpresa', 'ASSOCIACAO MANTENEDORA ASSISTE'), (u'NumeroBanco', 237), (u'NomeBanco', 'BRADESCO'), (u'DataGravacaoArquivo', datetime.date(2013, 4, 24)), (u'Branco', False), (u'IdentificacaoSistema', 'MX'), (u'NroSequencialArquivo', 9000461), (u'Branco2', False), (u'NroSequencialRegistroH', 1)]), OrderedDict([(u'IDReg', '1'), (u'AgenciaDebito', '00000'), (u'DigitoAgenciaDebito', False), (u'RazaoContaCorrenteDebito', '00000'), (u'ContaCorrenteDebito', '0000000'), (u'DigitoContaCorrenteDebito', '0'), (u'Zero', 0), (u'Carteira', 9), (u'AgenciaCedente', 160), (u'ContaCorrente', 82800), (u'DigitoContaCorrente', 9), (u'NroControleParticipante', False), (u'CodigoBanco', 237), (u'Zeros', 0), (u'NossoNumero', 130001042568L), (u'DescontoBonificacaoDia', 0), (u'EmissaoPapeletaCobranca', 1), (u'EmissaoPapeletaDebitoAutomatico', 'S'), (u'Branco3', False), (u'IndicadorRateioCredito', False), (u'AvisoDebitoAutomatico', False), (u'Branco4', False), (u'IdentificacaoOcorrencia', 1), (u'NDocumento', '0000080631'), (u'DataVencimentoTitulo', datetime.date(2013, 5, 15)), (u'ValorTitulo', 6250), (u'BancoEncarregadoCobranca', 0), (u'AgenciaDepositaria', 0), (u'EspecieTitulo', 1), (u'Identificacao', 'N'), (u'DataEmissaoTitulo', datetime.date(2013, 4, 24)), (u'1Instrucao', 0), (u'2Instrucao', 0), (u'MoraDiaria', 0), (u'DataLimiteDesconto', 150513), (u'ValorDesconto', 0), (u'ValorIOF', 0), (u'ValorAbatimento', 0), (u'IdentificacaoInscricaoSacado', 1), (u'NInscricaoSacado', 20507679865L), (u'NomeSacado', 'SANDRA RIBEIRO DA SILVA ROCHA'), (u'EnderecoCompleto', 'R ESTRELA D OESTE,310'), (u'1Mensagem', False), (u'Cep', '06721010'), (u'Avalista-2Mensagem', False), (u'NroSequencialRegistroD', 2)]), OrderedDict([(u'IDReg', '2'), (u'Mensagem1', 'TAXA CERIMONIA DE FORMATURA                                                    .'), (u'Mensagem2', '941 FELIPE SILVA ROCHA                                                         .'), (u'Mensagem3', '8 PARCELAS                                                                     .'), (u'Mensagem4', 'APOS 60 DIAS PAGAVEL SOMENTE NA TESOURARIA DO COLEGIO                          .'), (u'Filler', False), (u'Carteira', 9), (u'Agencia', 160), (u'ContaCorrente', 82800), (u'DigitoCC', '9'), (u'NossoNumero', '13000104256'), (u'DigitoNN', '8'), (u'sequencia', 3)]), OrderedDict([(u'IDReg', '9'), (u'Branco5', False), (u'NroSequencialRegistroT', 4)])]
        generator = CNABGenerator()
        result = generator.generate_file(format, data).read()
        return result
    
    def export(self, cr, uid, ids, context=None):
        [wizard] = self.browse(cr, uid, ids)
        invoice_ids = context.get('active_ids', [])
        format = self.load_format(cr, uid)
        data = self.prepare_data(cr, uid, format, wizard.bank_id, invoice_ids)
        result = self.serialize(cr, uid, format, data)
        encoded_result = base64.b64encode(result)
        self.write(cr, uid, [wizard.id], {'file': encoded_result, 'state': 'done'})
        
        return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': wizard.id,
                #'views': [(resource_id, 'form')],
                'target': 'new',
               }
        
    _columns = {
                'file': fields.binary('File', readonly=True),
                'filename': fields.char('Filename', size=128),
                'bank_id': fields.many2one('res.bank', 'Bank', domain=[('enable_cnab', '=', True)]),
                #'format': fields.many2one('cnab.file_format', 'Format', required=True),
                'state': fields.selection([('init', 'init'), ('done', 'done')], 'state', readonly=True),
                }
    
    _defaults = {
                 'state': 'init',
                 'filename': 'result.txt',
                 }
