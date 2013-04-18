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


class server_manager(osv.Model):
    _name = 'server.manager'
    _columns = {
                'api_dns_email':fields.char('Email Api', size=50),
                'api_dns_key':fields.char('Zerigo Key', size=30),
                'default_domain':fields.char('Dominio', size=30),
                'empresa':fields.char('Empresa',size=30),
                'base_database':fields.char('Banco base',size=30)                               
        }

    def create_subdomain(self, cr, uid, ids, context=None):
        item = self.browse(cr, uid, ids[0], context)
        
        api_user = item.api_dns_email    
        api_key  = '8e4868a0acb5ccf6ee160de1b34c9c86'
        
        myzone = zerigodns.NSZone(api_user, api_key)
       
        print "\nLoading a single zone by domain name...\n"
        zone = myzone.find_by_domain(item.default_domain)        
        print "  Loaded zone #%i (%s)\n" % (zone.id, zone.domain)        
        # Add a host to the zone.        
        print "\nAdding a host to the zone.\n"        
        vals2 = {
              'hostname': item.empresa,
              'host_type': 'CNAME',
              'data': item.default_domain,
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
        retorno = execute(conn, 'duplicate_database', 'admin', item.base_database, item.empresa)
        print retorno
        return True
    
server_manager()
