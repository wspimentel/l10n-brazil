from datetime import datetime

class generate_sped_contabil():
    def __init__(self):
        pass
    
    def _create_new_execution(self, cr, uid, ids=None, context=None, obligation=None):
        pool_execution = obligation.pool.get('fiscal.obligation.execution')        
        new_obj = {'code':1,'date_execution_start': datetime.now(), 'date_execution_end':datetime.now(), 'running':True,
                   'fiscal_obligation_id':obligation.id }        
        id = pool_execution.create(cr, uid, new_obj,context)
        return id        
        
    def _set_as_generated(self,cr, uid, ids=None, context=None, obligation=None):
        pool_obligation = obligation.pool.get('fiscal.obligation')
        pool_obligation.write(cr, uid, ids, { 'generate':False, } , context)         
    
    def _create_new_message(self,cr, uid, ids=None, context=None, obligation=None, execution=None, message=None):
        pool_message = obligation.pool.get('fiscal.obligation.messages')
        pool_message.create(cr, uid, { 'message':message, 'fiscal_obligation_execution_id': execution.id }, context)
    
    def generate(self, cr, uid, ids=None, context=None, obligation=None):
        execution = self._create_new_execution(cr, uid, ids, context, obligation)
        self._create_new_message(cr, uid, ids, context, obligation, execution, "Iniciado a gerar o Sped Contabil")
        
                
        self._set_as_generated(cr, uid, ids, context, obligation)        
        self._create_new_message(cr, uid, ids, context, obligation, execution, "Terminado de gerar o Sped Contabil")    