# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2013  Renato Lima - Akretion                                  #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

from openerp.osv import orm, fields
from osv import fields,osv

from .l10n_br_account_product import (
    PRODUCT_FISCAL_TYPE,
    PRODUCT_FISCAL_TYPE_DEFAULT)


class L10n_brAccountFiscalCategory(orm.Model):
    _inherit = 'l10n_br_account.fiscal.category'
    _columns = {
        'fiscal_type': fields.selection(PRODUCT_FISCAL_TYPE,
            'Tipo Fiscal', required=True),
    }
    _defaults = {
        'fiscal_type': PRODUCT_FISCAL_TYPE_DEFAULT,
    }


class L10n_brAccountDocumentSerie(orm.Model):
    _inherit = 'l10n_br_account.document.serie'
    _columns = {
        'fiscal_type': fields.selection(
            PRODUCT_FISCAL_TYPE, 'Tipo Fiscal', required=True),
    }
    _defaults = {
        'fiscal_type': PRODUCT_FISCAL_TYPE_DEFAULT,
    }


class L10n_brAccountPartnerFiscalType(orm.Model):
    _inherit = 'l10n_br_account.partner.fiscal.type'
    _columns = {
        'icms': fields.boolean('Recupera ICMS'),
        'ipi': fields.boolean('RecuperaPRODUCT_FISCAL_TYPE_DEFAULT IPI')
    }
    defaults = {
        'icms': True,
        'ipi': True
    }

class L10n_brAccountMde(osv.osv):
 
    _name = 'l10n_br_account.mde'
    _columns = {
        'chNFe': fields.integer("Chave de Acesso", size=44, readonly=True),
        'nSeqEvento': fields.integer("Série", readonly=True),
        'idLote': fields.integer("Id Lote", readonly=True),
        'xNome': fields.char("Razão Social", readonly=True),
        'partner_id': fields.many2one('res.partner','Partner'),
        'IE': fields.related('partner_id', 'IE', type='char', string='Inscrição Estadual', readonly=True),
        'dEmi': fields.date("Data Emissão", readonly=True),
        'tpNF': fields.integer("Tipo de Operação", readonly=True),
        'vNF': fields.integer("Valor Total da NF-e", readonly=True),
        'cSitNFe': fields.integer("Situação da NF-e", readonly=True),
        'cSitConf': fields.integer("Situação da Manifestação", readonly=True),
        'formInclusao': fields.char("Forma de Inclusão", readonly=True),
        'dataInclusao': fields.date("Data de Inclusão", readonly=True),
        'versao': fields.integer("Versão", readonly=True),
    }
    
                 
    def action_search_nfe(self, cr, uid, ids, context=None):
        print "Acao ! action_search_nfe"
        return True
    
    def action_known_emission(self, cr, uid, ids, context=None):
        print "Acao ! action_known_emission"
        return True
    
    def action_confirm_operation(self, cr, uid, ids, context=None):
        print "Acao ! action_confirm_operation"
        return True
    
    def action_unknown_operation(self, cr, uid, ids, context=None):
        print "Acao ! action_unknown_operation"
        return True
    
    def action_not_operation(self, cr, uid, ids, context=None):
        print "Acao ! action_not_operation"
        return True
    
    def action_download_xml(self, cr, uid, ids, context=None):
        print "Acao ! action_download_xml"
        return True
    
    
    