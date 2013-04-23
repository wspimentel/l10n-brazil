#coding=utf-8
from openerp.osv import fields,osv
import xmlrpclib
import socket
import os
import time
import base64
from openerp import tools
import zipfile
from ftplib import FTP
from openerp.service.wsgi_server import serve
import zerigodns
import time
import sys

def execute(connector, method, *args):
    res = False
    try:        
        res = getattr(connector,method)(*args)
    except socket.error,e:        
            raise e
    return res

class server_location(osv.Model):
    _description = 'Locais Servidores'
    _name = 'server.location'
    _rec_name = 'description'
    _columns = {
            'description':fields.char(u'Descrição', size=100, required=True),
            'url_server':fields.char('Url Servidor', size=100, required=True),                        
    }

server_location()

class database_template(osv.Model):
    _description = 'Templates de banco'
    _name = 'database.template'
    _rec_name = 'description'
    _columns = {
            'description':fields.char(u'Descrição', size=100, required=True),
            'template':fields.char('Banco de dados de template', size=100, required=True),   
    }

database_template()

class server_subdomain(osv.Model):
    _description = 'Subdominios'
    _name = 'server.subdomain'
    _rec_name = 'subdomain'
    _columns = {        
        'subdomain':fields.char('Empresa',size=30),
        'base_database_id': fields.many2one('database.template', 'Template Banco de dados',
              required=True),
        'base_database': fields.related('base_database_id', 'description', type='char', string='Template'),
        'default_server_id':fields.many2one('server.location', 'Servidor Default', required=True),
        'default_server': fields.related('default_server_id', 'description', type='char', string='Servidor'),
        'partner_id':fields.many2one('res.partner', 'Cliente', required=True),
        'customer': fields.related('partner_id', 'name', type='char', string='Cliente'),                 
    }

    def create_subdomain(self, cr, uid, ids, context=None):
        item = self.browse(cr, uid, ids[0], context)
        configuration = self.pool.get('server.config.settings').default_get()
        api_user = configuration.zerigo_email_api    
        api_key  = configuration.zerigo_dns_key #'8e4868a0acb5ccf6ee160de1b34c9c86'
        
        myzone = zerigodns.NSZone(api_user, api_key)
       
        print "\nLoading a single zone by domain name...\n"
        zone = myzone.find_by_domain(item.default_server_id.url_server)        
        print "  Loaded zone #%i (%s)\n" % (zone.id, zone.domain)        
        # Add a host to the zone.        
        print "\nAdding a host to the zone.\n"        
        vals2 = {
              'hostname': item.subdomain,
              'host_type': 'CNAME',
              'data': item.default_server_id.url_server,
              'ttl': 86400,
        }        
        newhost = zone.create_host(vals2)
        if newhost.has_errors():
            print "  There was an error saving the new host.\n"
            for err in newhost.errors:
                print "    ", err
        else:
            print "  Host %s created successfully with id #%i.\n" % (newhost.hostname, newhost.id)
        return True
    
    def duplicate_database(self, cr, uid, ids, context=None):
        item = self.browse(cr, uid, ids[0], context)
        uri = 'http://localhost:8069' 
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        retorno = execute(conn, 'duplicate_database', 'admin', item.base_database_id.template, item.subdomain)
        print retorno
        return True
    
server_subdomain()


class server_settings(osv.osv_memory):
    _description = 'Configurações gerenciamento servidores'
    _name = 'server.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        'zerigo_email_api':fields.char('Zerigo Email API', size=50, help="Email de acesso a API do Zerigo DNS", required=True),
        'zerigo_dns_key': fields.char('Zerigo DNS Key',size=30, help="Chave de acesso a API do Zerigo DNS Service", required=True),
        'default_database_template_id': fields.many2one('database.template', 'Template Default Banco de dados',
                            required=True), 
        'default_server_id':fields.many2one('server.location', 'Servidor Default', required=True),
    }

server_settings()
