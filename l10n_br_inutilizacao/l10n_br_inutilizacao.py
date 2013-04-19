#coding=utf-8
from openerp.osv import osv, fields 
import pysped.nfe
import base64
import re

class l10n_br_account_invoice_invalid_number(osv.Model):
    _inherit = 'l10n_br_account.invoice.invalid.number'
    #TODO Impedir de mudar os valoes após o status done
    _columns = {
            'state': fields.selection(
            [('draft', 'Rascunho'), ('not_authorized', 'Não autorizado'),
            ('done', u'Autorizado Sefaz')], 'Status', required=True),
            'justificative': fields.char('Justificativa', size=255,required=True),
            'status':fields.char('Status', size=10),
            'message':fields.char('Mensagem', size=200),
        }
    def _check_justificative(self, cr,uid, ids):
        for invalid in self.browse(cr, uid, ids):
            if len(invalid.justificative) < 15:return  False
        return True
    
    _constraints = [(_check_justificative,'Justificativa deve ter tamanho minimo de 15 caracteres.', ['justificative'])]
    

    def action_draft_done(self, cr, uid, ids, *args):
        try:
            processo = self.send_request_to_sefaz(cr, uid, ids , args)
            
            if processo.resposta.infInut.cStat.valor == '102':
                self.write(cr, uid, ids, {'state': 'done', 'status':'102', 'message':processo.resposta.infInut.xMotivo.valor})
            else:
                self.write(cr, uid, ids, {'state':'not_authorized', 'status':processo.resposta.infInut.cStat.valor,
                        'message':processo.resposta.infInut.xMotivo.valor})
                
        except Exception,e:        
            self.write(cr, uid, ids, {'justificative': e.message})
        return True
    
    def send_request_to_sefaz(self, cr, uid, ids, *args):
        cr.sql_log = True
        record = self.browse(cr, uid, ids[0])
        company_pool = self.pool.get('res.company')        
        company = company_pool.browse(cr, uid, record.company_id.id)
                
        p = pysped.nfe.ProcessadorNFe()
        p.versao = '2.00' if (company.nfe_version == '200') else '1.10'
        p.estado = company.partner_id.l10n_br_city_id.state_id.code
        
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
        cnpj_partner = re.sub('[^0-9]','', company.partner_id.cnpj_cpf)
        serie = record.document_serie_id.code

        processo = p.inutilizar_nota(
            cnpj=cnpj_partner,
            serie=serie,
            numero_inicial=record.number_start,
            numero_final=record.number_end,
            justificativa=record.justificative)
                
        cr.sql_log = False            
        return processo
        