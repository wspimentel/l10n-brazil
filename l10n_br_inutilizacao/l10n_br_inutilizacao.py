#coding=utf-8
from openerp.osv import osv, fields 
import pysped.nfe
import base64

class l10n_br_account_invoice_invalid_number(osv.Model):
    _inherit = 'l10n_br_account.invoice.invalid.number'

    _columns = {
            'justificative': fields.char('Justificativa', size=255,required=True),
        }

    def action_draft_done(self, cr, uid, ids, *args):        
        self.send_request_to_sefaz(cr, uid, ids , args)
        self.write(cr, uid, ids, {'state': 'done'})
        return True
    
    def send_request_to_sefaz(self, cr, uid, ids, *args):
        company_pool = self.pool.get('res.company')
        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, uid, uid)
        company = company_pool.browse(cr, uid, user.company_id.id)
        
        p = pysped.nfe.ProcessadorNFe()
        p.versao = '2.00'
        p.estado = 'SP' 
        
        file_content_decoded = base64.decodestring(company.nfe_a1_file)
        filename = company.nfe_export_folder + 'certificate.pfx'
        fichier = open(filename,'w+')
        fichier.write(file_content_decoded)
        fichier.close()
                   
        p.certificado.arquivo = filename
        p.certificado.senha = company.nfe_a1_password
    
        p.salva_arquivos = True
        p.contingencia_SCAN = False
        p.caminho = company.nfe_export_folder
    
        # O retorno de cada webservice é um objeto
        # com as seguintes propriedades
        # .webservice - o webservice que foi consultado
        # .envio - o objeto da classe XMLNFE enviado
        # .envio.original - o texto do xml (envelope SOAP) enviado ao webservice
        # .resposta - o objeto da classe XMLNFE retornado
        # .resposta.version - version da HTTPResponse
        # .resposta.status - status da HTTPResponse
        # .resposta.reason - reason da HTTPResponse
        # .resposta.msg - msg da HTTPResponse
        # .resposta.original - o texto do xml (SOAP) recebido do webservice
        
        # Inutilizar somente uma nota        
        processo = p.inutilizar_nota(
            cnpj='11111111111111',
            serie='101',
            numero_inicial=18,
            justificativa=u'Testando a inutilização de NF-e')
    
        print processo.resposta.status
        print processo.resposta.reason
        