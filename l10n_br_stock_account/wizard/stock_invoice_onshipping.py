# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2009  Renato Lima - Akretion
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

FISCAL_DOC_REF = [
    ('account.invoice', u'Fatura'),
]


class StockInvoiceOnShipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.multi
    def _compute_fiscal_doc_ref(self):
        ref_id = False
        picking_obj = self.env['stock.picking']
        for record in picking_obj.browse(
                self._context.get('active_ids', False)):
            move = record.move_lines[0]
            if move.origin_returned_move_id:
                ref_id = self.env['account.invoice'].search([
                    ('nfe_access_key', '=',
                     move.origin_returned_move_id.picking_id.fiscal_document_access_key)
                ], limit=1).id
            res = 'account.invoice,%d' % ref_id
            return res

    journal_id = fields.Many2one(
        'account.journal', 'Destination Journal',
        domain="[('type', '=', journal_type)]")
    fiscal_category_journal = fields.Boolean(
        u'Diário da Categoria Fiscal', default=True)

    fiscal_doc_ref = fields.Reference(selection=FISCAL_DOC_REF, readonly=False,
                                      default=_compute_fiscal_doc_ref,
                                      string=u'Documento Fiscal Relacionado')

    @api.multi
    def create_invoice(self):
        context = dict(self.env.context)
        active_ids = context.get('active_ids', [])
        for picking in self.env['stock.picking'].browse(active_ids):
            journal_id = picking.fiscal_category_id.property_journal
            if self.fiscal_doc_ref:
                context.update({'fiscal_doc_ref': self.fiscal_doc_ref})
            if not journal_id:
                raise UserError(
                    _('Invalid Journal!'),
                    _('There is not journal defined for this company: %s in '
                      'fiscal operation: %s !') %
                    (picking.company_id.name,
                     picking.fiscal_category_id.name))
            self.write({'journal_id': journal_id.id})
        result = super(StockInvoiceOnShipping, self.with_context(
            context)).create_invoice()
        return result
