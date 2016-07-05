__author__ = 'sadamo'

from openerp import models, fields, api
# from openerp.addons import decimal_precision as dp
# from openerp.tools.float_utils import float_compare
# from openerp.addons.l10n_br_pos.models.pos_config import \
#     SIMPLIFIED_INVOICE_TYPE
# from openerp.tools.translate import _

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.multi
    def create_returns(self):
        ctx = dict(self._context)

        if ctx.get('pos_devolution'):
            ctx.update(
                {
                      # '': ,
                      # '': ,
                      # '': ,
                }
            )
            res = super(StockReturnPicking, self).create_returns()

            # TODO automatizar a transferencia do picking de devolucao e
            # preparar as informações da invoice (parceiro, tipo de operacao,
            #  nfe/documentos relacionados)


            return res

        return super(StockReturnPicking, self).create_returns()