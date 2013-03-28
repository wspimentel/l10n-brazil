# coding=utf-8
from openerp.osv import osv, fields 

class point_of_sale(osv.Model):
    _description = 'Geracao das obrigacoes fiscais'
    _name = 'point.of.sale'
    _order = 'description asc'
    _columns = {
        'code':fields.integer('Code'),
        'description': fields.char('Description', size=60),
        'pdv_number': fields.char('PDV Number', size=20),
        'point_of_sale_messages': fields.one2many('point.of.sale.messages.integration', 'point_of_sale_id','Integration messages'),
    }
    _defaults = {}
    
point_of_sale()

class point_of_sale_messages_integration(osv.Model):
    _description = 'Mensagens ocorridas durante integração'
    _name = 'point.of.sale.messages.integration'
    _order = 'description asc'
    _columns = {
        'date_raised':fields.integer('Date'),
        'message': fields.char('Message', size=1500),
        'point_of_sale_id': fields.many2one('point.of.sale', 'Point of sale',
                                    required=True),
    }
    _defaults = {}
    
point_of_sale_messages_integration()