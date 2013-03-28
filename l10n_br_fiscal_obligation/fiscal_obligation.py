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