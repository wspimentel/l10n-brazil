# -*- coding: utf-8 -*-

# Copyright (C) 2009  Renato Lima - Akretion                                  #
# Copyright (C) 2012  Raphaël Valyi - Akretion                                #
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # TODO migrate to new API - Não existe mais este método
    def _prepare_invoice(self, cr, uid, picking, partner,
                         inv_type, journal_id, context=None):
        result = super(StockPicking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context)

        fp_comment = []
        fc_comment = []
        fp_ids = []
        fc_ids = []

        if picking.fiscal_position and \
                picking.fiscal_position.inv_copy_note and \
                picking.fiscal_position.note:
            fp_comment.append(picking.fiscal_position.note)

        for move in picking.move_lines:
            if move.sale_line_id:
                line = move.sale_line_id
                if line.fiscal_position and \
                        line.fiscal_position.inv_copy_note and \
                        line.fiscal_position.note:
                    if line.fiscal_position.id not in fp_ids:
                        fp_comment.append(line.fiscal_position.note)
                        fp_ids.append(line.fiscal_position.id)

            if move.product_id.ncm_id:
                fc = move.product_id.ncm_id
                if fc.inv_copy_note and fc.note:
                    if fc.id not in fc_ids:
                        fc_comment.append(fc.note)
                        fc_ids.append(fc.id)

        result['comment'] = " - ".join(fp_comment + fc_comment)
        result['fiscal_category_id'] = picking.fiscal_category_id and \
            picking.fiscal_category_id.id
        result['fiscal_position'] = picking.fiscal_position and \
            picking.fiscal_position.id
        result['ind_final'] = picking.fiscal_position.ind_final
        return result
