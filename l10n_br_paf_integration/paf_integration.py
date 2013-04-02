# coding=utf-8
from openerp.osv import osv, fields 
import pika
import json

class point_of_sale(osv.Model):
    _description = 'Ponto de vendas'
    _name = 'point.of.sale'
    _order = 'description asc'
    _columns = {
        'code':fields.integer('Code'),
        'description': fields.char('Description', size=60),
        'pdv_number': fields.char('PDV Number', size=20),
        'point_of_sale_messages': fields.one2many('point.of.sale.messages.integration', 'point_of_sale_id','Integration messages'),
    }
    _defaults = {}
    
    
    def send_changes_to_rabbitmq(self, cr, uid, ids=None, context=None):        
        audit = self.pool.get('audittrail.log')        
            
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        
        ids_log = audit.search(cr, uid, [('is_processed','=',False)])            
        full_logs = audit.browse(cr, uid, ids_log, context)
        for log in full_logs:     
            log_message = { 'log_id':log.res_id, 'date':log.timestamp, 'metodo': log.method }       
            message = json.dumps(log_message)
            
            channel.basic_publish(exchange='',
                      routing_key='hello',
                      body='%r - %r' % (log.res_id,message))
            
            audit.write(cr, uid, log.res_id, {'is_processed':True}, context)
            
        connection.close()
    
    def get_changes_from_rabbit(self,cr, uid, ids=None):
        ids = [1]
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='hello')

        print ' [*] Waiting for messages. To exit press CTRL+C'

        def callback(ch, method, properties, body):            
            for time in self.browse(cr, uid, ids):
                if(time!=None):
                    print time.nome
            print " [x] Received %r %r %r" % (body,ids,uid,)

        channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

        channel.start_consuming()
    
    
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


class audittrail_log(osv.Model):
    _inherit = 'audittrail.log'
    _columns = {
                'is_processed': fields.boolean('Already processed',required=True)
    }
    _defaults = {'is_processed':False }

audittrail_log()