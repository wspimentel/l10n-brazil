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

class CNABPayeeInfo(osv.osv):
    _name = 'cnab.bradesco.payee_info'
    
    _columns = {
                'codigo_empresa': fields.char('Código da Empresa', size=20, required=True),
                'codigo_carteira': fields.char('Código da Carteira', size=3, required=True),
                'codigo_agencia': fields.char('Código da Agência', size=5, required=True),
                'numero_conta': fields.char('Número', size=7, required=True),
                'digito_conta': fields.char('Dígito', size=1, required=True),
                'emissao_papeleta': fields.selection((('1', 'Emissão pelo Banco'),
                                                      ('2', 'Apenas processamento')),
                                                     'Emissão de papeleta de cobrança', required=True),
                'registro_debito_automatico': fields.selection((('N', 'Rejeitar na cobrança (não emitir papeleta)'),
                                                                ('S', 'Registrar na cobrança (emitir papeleta)')),
                                                               'Dados de débito incorretos', required=True),
                'rateio_credito': fields.boolean('Participar no Rateio de Crédito'),
                'aviso_debito_automatico': fields.selection((('2', 'Não emitir'),
                                                             ('1', 'Emitir para endereço no Arquivo-Rememessa'),
                                                             ('3', 'Emitir para endereço no cadastro do banco')),
                                                            'Automatic Debit Alert', required=True),
                'sequencia_registro': fields.integer('Sequencia de Arquivos-Remessa', required=True),
               }
    
    _defaults = {
                 'codigo_empresa': '0',
                 'codigo_carteira': '0',
                 'codigo_agencia': '0',
                 'numero_conta': '0',
                 'digito_conta': '0',
                 'emissao_papeleta': '1',
                 'registro_debito_automatico': 'N',
                 'rateio_credito': True,
                 'aviso_debito_automatico': '1',
                 'sequencia_registro': 0,
                }
