#coding=utf-8
from openerp.osv import osv, fields 
from sped_contabil import generate_sped_contabil
from sped_fiscal import generate_sped_fiscal


class fiscal_obligation(osv.Model):
    _name = 'fiscal.obligation'
    _description = 'Geracao das obrigacoes fiscais'
    _order = 'description asc'
    _rec_name = 'description'
    _columns = {
        'code':fields.integer('Código'),
        'description': fields.char('Descrição', size=60),
        'generate':fields.boolean('Gerar obrigação'),
        'executions': fields.one2many('fiscal.obligation.execution', 'fiscal_obligation_id','Execuções'),
    }
    _defaults = {'generate':False,
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'fiscal.obligation.messages.order.sequence'),
       }
    
    def generate_obligation(self, cr, uid, ids=None, context=None):        
        ids = self.search(cr, uid, [('generate','=',True),])
        obligations = self.browse(cr, uid, ids, context)
        for obligation in obligations:
            if obligation.description == 'Sped Fiscal':
                generator = generate_sped_fiscal()
                generator.generate(cr, uid, obligation.id, context, obligation)
                print 'Executou fiscal'
            elif obligation.description == 'Sped Contabil':
                generator = generate_sped_contabil()
                generator.generate(cr, uid, obligation.id, context, obligation)           
                print 'Executou contabil'
        
        return True
        
    
fiscal_obligation()

class fiscal_obligation_execution(osv.Model):
    _name = 'fiscal.obligation.execution'
    _description = 'Execucao da geracao da obrigacao fiscal'
    _order = 'code asc'
    _columns = {
        'code':fields.integer('Código'),
        'date_execution_start': fields.datetime('Inicio execução'),
        'date_execution_end': fields.datetime('Fim execução'),
        'running':fields.boolean('Executando'),
        'fiscal_obligation_id': fields.many2one('fiscal.obligation', 'Obrigação fiscal',
                                    required=True),
        'messages': fields.one2many('fiscal.obligation.messages', 'fiscal_obligation_execution_id','Mensagens'),
    }
    _defaults = {            
                 }

class fiscal_obligation_messages(osv.Model):
    _name = 'fiscal.obligation.messages'
    _description = 'Mensagens ocorridas na geracao da obrigacao'
    _order = 'id asc'
    _columns = {        
        'message': fields.char('Mensagem', size=500),
        'fiscal_obligation_execution_id': fields.many2one('fiscal.obligation.execution', 'Execução obrigação fiscal',
                                    required=True),
    }
    _defaults = { }

fiscal_obligation_messages()

class contador(osv.Model):
    _description = 'Contadores da empresa'
    _inherit = 'res.partner'
    _columns = {
                'is_accountant': fields.boolean('Contador', help="Marque esta caixa se este parceiro é um contador."),
                'cnpj_empresa' : fields.char('CNPJ escritório', size=20),
                'inscricao_crc':fields.char('Incrição CRC', size=15),
                }
    _defaults = {}
    
    
    
contador()

class account_asset(osv.Model):
    _description = 'Patrimonio imobilizado'
    _inherit = 'account.asset.asset'
    _columns = {
                'tipo_mercadoria':fields.integer('Tipo mercadoria'), #TODO Colocar aqui também a conta analitica de contabilização do item
                }
    _defaults = {}

account_asset()