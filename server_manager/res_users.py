#coding=utf-8
'''
Created on 20/04/2013

@author: danimar
'''
import datetime
from openerp.osv import osv, fields
from openerp.osv import orm
from openerp.tools.translate import _


class res_users(osv.Model):
    _inherit = 'res.users'
    _columns = {        
            }
    
    def signup(self, cr, uid, values, token=None, context=None):
        created_user = super(res_users, self).signup(cr, uid, values, token, context)
        #TODO Pegar os valores e modificar o que é necessario
        if not values["licence_key"]:
            raise orm.except_orm(_('Error !'), ("Chave da licença é obrigatório"))
        if not values["company_name"]:
            raise orm.except_orm(_('Error !'), ("Nome da empresa é obrigatório"))
        licence_pool = self.pool.get('licence.software')
        licence_ids = licence_pool.search(cr, uid, [('licence_key','=',values['licence_key'])])
        if len(licence_ids) > 0:            
            user_ids = self.search(cr, uid, ['&',('login','=',created_user[1]),('password','=',created_user[2])])
            if user_ids:
                user = self.browse(cr, uid, user_ids[0], context)
                
                self.write(cr, uid, user_ids, {'customer':1, 'is_new':1}, context)   
                licence_pool.write(cr, uid, licence_ids, {'state':'in_use', 'partner_id':user.partner_id.id,
                    'issued_date':datetime.datetime.today(),'expiry_date': datetime.datetime.today() + datetime.timedelta(days=365) }, context)         
                
                self._setup_environment(cr, uid, values, context)
            else:
                raise orm.except_orm(_('Error !'), ("Erro ao criar o usuário"))
        else:
            raise orm.except_orm(_('Error !'), ("A licença não é válida"))
        return created_user
    
    def _setup_environment(self, cr, uid, values, context=None):
        manager_pool = self.pool.get('server.manager')
        values_insert = {'api_dns_email':'danimaribeiro@gmail.com', 'default_domain':'emissaocte.com.br',
            'empresa':values["company_name"], 'base_database':'google'}        
        id_manager = manager_pool.create(cr, uid, values_insert , context)
        server = manager_pool.browse(cr, uid, id_manager, context)
        server.create_subdomain()
        server.duplicate_database()
    
res_users()


class res_partner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'is_new':fields.boolean("Cliente novo?"),        
    }
    _defaults = {
        'is_new':1,
    }