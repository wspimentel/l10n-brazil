#coding=utf-8
from openerp.osv import osv, fields 


class fiscal_obligation(osv.Model):
    _name = 'fiscal.obligation'
    _description = 'Geracao das obrigacoes fiscais'
    _order = 'description asc'
    _columns = {
        'code':fields.integer('Code'),
        'description': fields.char('Description', size=60),
        'messages': fields.one2many('fiscal.obligation.messages', 'fiscal_obligation_id','Messages'),
    }
    _defaults = {}
    
    def update_invoice(self, cr, uid, ids, context=None):
        pass
    
    def generate_obligation(self, cr, uid, ids=None, context=None):
        pass
    
fiscal_obligation()

class fiscal_obligation_messages(osv.Model):
    _name = 'fiscal.obligation.messages'
    _description = 'Geracao das obrigacoes fiscais'
    _order = 'code asc'
    _columns = {
        'code':fields.integer('Code'),
        'message': fields.char('Message', size=500),
        'fiscal_obligation_id': fields.many2one('fiscal.obligation', 'Obrigação fiscal',
                                    required=True),
    }
    _defaults = {}

fiscal_obligation_messages()

class contador(osv.Model):
    _description = 'Contadores da empresa'
    _inherit = 'res.partner'
    _columns = {
                'is_contador': fields.boolean('Contador', help="Marque esta caixa se este parceiro é um contador."),
                'cnpj_empresa' : fields.char('CNPJ escritório', size=20),
                'inscricao_crc':fields.char('Incrição CRC', size=15),
                }
    _defaults = {}
    
contador()

class account_assets(osv.Model):
    _description = 'Patrimonio imobilizado'
    _inherit = 'account.asset.asset'
    _columns = {
                'tipo_mercadoria':fields.integer('Tipo mercadoria'), #TODO Colocar aqui também a conta analitica de contabilização do item
                }
    _defaults = {}

account_assets()
