# coding=utf-8
from openerp.osv import osv, fields 
import pika
import json
from datetime import datetime

class point_of_sale(osv.Model):
    _description = 'Ponto de vendas'
    _name = 'point.of.sale'
    _order = 'description asc'
    _columns = {
        'code':fields.integer('Code'),
        'description': fields.char('Description', size=60),
        'pdv_number': fields.char('PDV Number', size=20),
        'last_full_update': fields.datetime('Last update'),
        'execute_full_update':fields.boolean('Execute full update'),
        'point_of_sale_messages': fields.one2many('point.of.sale.messages.integration', 'point_of_sale_id','Integration messages'),
    }
    _defaults = {}
    
    
    def send_changes_to_rabbitmq(self, cr, uid, ids=None, context=None):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='server-to-paf-ecf')
                
        #audit = self.pool.get('audittrail.log')
        ids = self.search(cr, uid, [], context)        
        
        print str(datetime.now()) + ' - Starting full update.'
        
        pdv = self.browse(cr, uid, ids[0], context)
        if pdv.execute_full_update:
            self.send_all_tables_to_rabbitmq(cr, uid, ids, context, channel)               
        
        self.write(cr, uid, pdv.id, {'execute_full_update': False}, context)        
        print str(datetime.now()) + ' - Finished full update.'
#        ids_log = audit.search(cr, uid, [('is_processed','=',False)])            
#        full_logs = audit.browse(cr, uid, ids_log, context)
#        for log in full_logs:     
#            log_message = { 'log_id':log.res_id, 'date':log.timestamp, 'metodo': log.method }       
#            message = json.dumps(log_message)
#            
#            channel.basic_publish(exchange='',
#                      routing_key='paf-ecf',
#                      body='%r - %r' % (log.res_id,message))
#            
#            audit.write(cr, uid, log.res_id, {'is_processed':True}, context)
        
        connection.close()
    
    
    def send_all_tables_to_rabbitmq(self, cr, uid, ids=None, context=None, channel=None):
        self.send_unit_of_measure(cr, uid, ids, context, channel)
        #self.send_uf_and_cities(cr, uid, ids, context, channel)
        self.send_accountant(cr, uid, ids, context, channel)
        self.send_company(cr, uid, ids, context, channel)        
        self.send_customers(cr, uid, ids, context, channel)
    
    def send_unit_of_measure(self, cr, uid, ids=None, context=None, channel=None):
        uom = self.pool.get('product.uom')
        ids = uom.search(cr, uid, [], context)        
        units = uom.browse(cr, uid, ids, context)
        for unit in units:
            objeto = { 'id':unit.id, 'descricao':unit.name }
            message = { 'id':1, 'mensagem': json.dumps(objeto) }            
            channel.basic_publish(exchange='', routing_key='server-to-paf-ecf', body=json.dumps(message))
        
    def send_uf_and_cities(self, cr, uid, ids=None, context=None, channel=None):
        states = self.pool.get('res.country.state')
        companies = self.pool.get('res.company')
        company_ids = companies.search(cr, uid, [], offset=0, limit=1, context=context)
        if len(company_ids) > 0:
            company =  companies.browse(cr, uid, company_ids[0],context)
            ids = states.search(cr, uid, [("country_id" , "=" , company.country_id.id)], context)
            ufs = states.browse(cr, uid, ids, context)
            for uf in ufs:
                objeto = {'uf':uf.code, 'descricao':uf.name }
                message = {'id':2, 'mensagem':json.dumps(objeto) }
                channel.basic_publish(exchange='', routing_key='server-to-paf-ecf', body=json.dumps(message))
                self.send_cities(cr, uid, ids, context, channel, uf.id, uf.code)
    
                
    def send_cities(self, cr, uid, ids=None, context=None,channel=None, state_id=None, uf_code=None):
        cities_pool = self.pool.get('l10n_br_base.city')
        ids = cities_pool.search(cr, uid, [("state_id" , "=" , state_id)], context)
        cities = cities_pool.browse(cr, uid, ids, context)
        for city in cities:
            objeto = {'ibge_code': city.ibge_code, 'descricao':city.name ,'uf':uf_code}
            message = {'id':3, 'mensagem':json.dumps(objeto) }
            channel.basic_publish(exchange='', routing_key='server-to-paf-ecf', body=json.dumps(message))
 
    def send_accountant(self, cr, uid, ids=None, context=None, channel=None):
        accountant_pool = self.pool.get('res.partner')
        accountant_ids = accountant_pool.search(cr, uid, [("is_accountant","=", True)], context)
        accountants = accountant_pool.browse(cr, uid, accountant_ids, context)
        for accountant in accountants:
            objeto = {'id': accountant.id,'nome':accountant.name, 'cpf':accountant.cnpj_cpf,'endereco':accountant.street,
                      'numero': accountant.number ,'cep': accountant.zip ,'bairro':accountant.district,'cidade_id':accountant.l10n_br_city_id.id,
                     'telefone':accountant.phone, 'crc':accountant.inscricao_crc, 'cnpj':accountant.cnpj_empresa,'email':accountant.email}
            message = {'id':4, 'mensagem':json.dumps(objeto) }            
            channel.basic_publish(exchange='', routing_key='server-to-paf-ecf', body=json.dumps(message))
    
    def send_company(self, cr, uid, ids=None, context=None, channel=None):
        companies = self.pool.get('res.company')
        company_ids = companies.search(cr, uid, [], offset=0, limit=1, context=context)
        if len(company_ids) > 0:
            company =  companies.browse(cr, uid, company_ids[0],context)  
            objeto = {'id': company.id,'razao_social':company.partner_id.name, 'cnpj':company.partner_id.cnpj_cpf,'endereco':company.partner_id.street,
                      'numero': company.partner_id.number ,'cep': company.partner_id.zip ,'bairro':company.partner_id.district,'cidade_id':company.partner_id.l10n_br_city_id.id,
                     'telefone':company.partner_id.phone, 'email':company.partner_id.email}
            message = {'id':5, 'mensagem':json.dumps(objeto) }            
            channel.basic_publish(exchange='', routing_key='server-to-paf-ecf', body=json.dumps(message))
        
    def send_customers(self, cr, uid, ids=None, context=None, channel=None):
        customer_pool = self.pool.get('res.partner')
        customer_ids = customer_pool.search(cr, uid, [("customer","=", True)], context)
        customers = customer_pool.browse(cr, uid, customer_ids, context)
        for customer in customers:
            objeto = {'id': customer.id,'nome':customer.name, 'cpf_cnpj':customer.cnpj_cpf,'endereco':customer.street,
                      'numero': customer.number ,'cep': customer.zip ,'bairro':customer.district,'cidade_id':customer.l10n_br_city_id.id, 'telefone':customer.phone}
            message = {'id':6, 'mensagem':json.dumps(objeto) }            
            channel.basic_publish(exchange='', routing_key='server-to-paf-ecf', body=json.dumps(message))
        
    
    def get_changes_from_rabbit(self,cr, uid, ids=None):
        pass
#        ids = [1]
#        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#        channel = connection.channel()
#
#        channel.queue_declare(queue='hello')
#
#        print ' [*] Waiting for messages. To exit press CTRL+C'
#
#        def callback(ch, method, properties, body):            
#            for time in self.browse(cr, uid, ids):
#                if(time!=None):
#                    print time.nome
#            print " [x] Received %r %r %r" % (body,ids,uid,)
#
#        channel.basic_consume(callback,
#                      queue='hello',
#                      no_ack=True)
#
#        channel.start_consuming()
    
    
    
    
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