'''
Created on 16/04/2013

@author: Danimar Ribeiro
'''

from openerp.osv import osv, fields
import pysped.nfe
import base64

class account_invoice(osv.Model):
    _inherit = 'account.invoice'
    
    def action_cancel(self, cr, uid, ids, context=None):
        self.cancel_invoice_online(cr, uid, ids, context)
        #value = super(account_invoice,self).action_cancel(cr, uid, ids, context)
        #if value:            
        return True
        
    def cancel_invoice_online(self, cr, uid, ids,context=None):
        cr.sql_log = True
        record = self.browse(cr, uid, ids[0])
        company_pool = self.pool.get('res.company')        
        company = company_pool.browse(cr, uid, record.company_id.id)
                
        p = pysped.nfe.ProcessadorNFe()
        p.versao = '2.00'
        p.estado = company.partner_id.l10n_br_city_id.state_id.code
        
        file_content_decoded = base64.decodestring(company.nfe_a1_file)
        filename = company.nfe_export_folder + 'certificate.pfx'
        fichier = open(filename,'w+')
        fichier.write(file_content_decoded)
        fichier.close()
                   
        p.certificado.arquivo = filename
        p.certificado.senha = company.nfe_a1_password
    
        p.salva_arquivos = False
        p.contingencia_SCAN = False
        p.caminho = company.nfe_export_folder
        
        processo = p.cancelar_nota_evento(
            chave_nfe = record.nfe_access_key,
            numero_protocolo=record.nfe_status,
            justificativa='Somente um teste de cancelamento' #TODO Colocar a justificativa de cancelamento num wizard de cancelamento.
        )

        print processo        
        print processo.envio.xml
        print processo.envio.original
        print processo.resposta.xml
        print processo.resposta.original
        print processo.resposta.reason
        print processo.resposta.dic_retEvento
        print processo.resposta.dic_procEvento