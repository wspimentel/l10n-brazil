#coding=utf-8
'''
Created on 01/05/2013

@author: danimar
'''

from openerp.osv import osv, fields
import pysped.nfe
import base64

class account_invoice(osv.Model):
    _inherit = 'account.invoice'
    _columns = {                               
        'nfe_export_invoice_id': fields.many2one('l10n_br_account.nfe_export_invoice', 'Exportação NFe'),
    }
    
    def action_invoice_send_nfe(self, cr, uid, ids, context=None):
        invoices = self.browse(cr, uid, ids, context)
        for invoice in invoices:
            nfe_export_pool = self.pool.get('l10n_br_account.nfe_export_invoice')
            if not invoice.nfe_export_invoice_id:                                
                nfe_export_id = nfe_export_pool.create(cr, uid, { 'name': 'Envio NFe'}, context)
                self.write(cr, uid, ids, {'nfe_export_invoice_id': nfe_export_id})
                inv = self.browse(cr, uid, invoice.id)
                return inv.nfe_export_invoice_id.open_window()
                            
                        
            result_pool =  self.pool.get('l10n_br_account.nfe_export_invoice_result')
            for result_id in invoice.nfe_export_invoice_id.nfe_export_result:
                result_pool.unlink(cr, uid, result_id.id, context)           
                        
            nfe_export_pool.write(cr, uid, invoice.nfe_export_invoice_id.id, {'state':'init', 'file':'', 'name':''})
            return invoice.nfe_export_invoice_id.open_window()
        
    
account_invoice()

class l10n_br_account_nfe_export_invoice(osv.Model):
    """ Export fiscal eletronic file from invoice"""
    _inherit = 'l10n_br_account.nfe_export_invoice'    
    
    def open_window(self,cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        model_data_ids = mod_obj.search(
            cr, uid, [('model', '=', 'ir.ui.view'),
            ('name', '=', 'l10n_br_account_nfe_export_invoice_form')],
            context=context)
        resource_id = mod_obj.read(
            cr, uid, model_data_ids,
            fields=['res_id'], context=context)[0]['res_id']
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(resource_id, 'form')],
            'target': 'new',
        }