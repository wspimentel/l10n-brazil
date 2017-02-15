# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2016 Kmee - www.kmee.com.br
#   @authors Daniel Sadamo <daniel.sadamo@kmee.com.br>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp import models, api, _
from openerp.osv import osv, fields


class WizardValuationHistory(models.TransientModel):
    _inherit = 'wizard.valuation.history'

    '''TODO - We need to use the old API because the Context is not being
     pass to the method read_group( ORM ), the reason seems because this
      method still not migrated to new API.'''
    @api.model
    def compute(self, cr, uid, ids, date, context=None):

        context['history_date'] = date

        fields = [
            'fiscal_classification_id',
            'product_id',
            'location_id',
            'move_id',
            'company_id',
            'date',
            'source',
            'quantity',
            'inventory_value',
            'price_unit_on_quant'
        ]
        group_by = [
            'product_id',
            'location_id',
            'fiscal_classification_id'
        ]
        domain = [('date', '<=', date)]

        result = self.pool.get('stock.history').read_group(
            cr, uid, domain=domain, fields=fields, groupby=group_by,
            context=context)

        return result

    @api.multi
    def open_report_xls(self):

        data = self.read()[0]
        ctx = self.env.context.copy()
        ctx['history_date'] = data['date']
        ctx['search_default_group_by_product'] = True
        ctx['search_default_group_by_location'] = True

        return {
            'domain': "[('date', '<=', '" + data['date'] + "')]",
            'name': _('Stock Value At Date'),
            'type': 'ir.actions.report.xml',
            'report_name': 'wizard.valuation.history',
            'datas': data,
            'context': ctx,
            'nodestroy': True
        }


class StockHistory(osv.osv):

    _inherit = 'stock.history'

    _columns = {
        'fiscal_classification_id': fields.related(
            'product_id', 'fiscal_classification_id', type='many2one',
            relation='account.product.fiscal.classification', string='NCM'
        )
    }

    def read_group(self, cr, uid, domain, fields, groupby, offset=0,
                   limit=None, context=None, orderby=False, lazy=True):
        res = models.Model.read_group(self, cr, uid, domain, fields, groupby,
                                      offset=offset, limit=limit,
                                      context=context, orderby=orderby,
                                      lazy=lazy)
        if context is None:
            context = {}
        date = context.get('history_date', datetime.now())
        if 'inventory_value' in fields:
            group_lines = {}
            for line in res:
                domain = line.get('__domain', domain)
                group_lines.setdefault(
                    str(domain), self.search(cr, uid, domain, context=context))
            line_ids = set()
            for ids in group_lines.values():
                for product_id in ids:
                    line_ids.add(product_id)
            line_ids = list(line_ids)
            lines_rec = {}
            if line_ids:
                cr.execute('SELECT id, product_id, price_unit_on_quant,'
                           ' company_id, quantity FROM stock_history '
                           'WHERE id in %s', (tuple(line_ids),))
                lines_rec = cr.dictfetchall()
            lines_dict = dict((line['id'], line) for line in lines_rec)
            product_ids = list(
                set(line_rec['product_id'] for line_rec in lines_rec))
            products_rec = self.pool['product.product'].read(
                cr, uid, product_ids,
                ['cost_method', 'product_tmpl_id'], context=context)
            products_dict = dict(
                (product['id'], product) for product in products_rec)
            cost_method_product_tmpl_ids = list(
                set(product['product_tmpl_id'][0]
                    for product in products_rec
                    if product['cost_method'] != 'real'))
            histories = []
            if cost_method_product_tmpl_ids:
                cr.execute('SELECT DISTINCT ON'
                           ' (product_template_id, company_id)'
                           ' product_template_id, company_id, cost FROM '
                           'product_price_history WHERE product_template_id '
                           'in %s AND datetime <= %s ORDER BY '
                           'product_template_id, company_id, datetime DESC',
                           (tuple(cost_method_product_tmpl_ids), date))
                histories = cr.dictfetchall()
            histories_dict = {}
            for history in histories:
                histories_dict[
                    (history['product_template_id'],
                     history['company_id'])] = history['cost']
            for line in res:
                inv_value = 0.0
                lines = group_lines.get(str(line.get('__domain', domain)))
                for line_id in lines:
                    line_rec = lines_dict[line_id]
                    product = products_dict[line_rec['product_id']]
                    if product['cost_method'] == 'real':
                        price = line_rec['price_unit_on_quant']
                    else:
                        price = histories_dict.get(
                            (product['product_tmpl_id'][0],
                             line_rec['company_id']), 0.0)
                    inv_value += price * line_rec['quantity']
                line['inventory_value'] = inv_value
                if line['quantity'] == 0.00:
                    line['price_unit_on_quant'] = 0.00
                else:
                    line['price_unit_on_quant'] = inv_value/line['quantity']

        if 'fiscal_classification_id' in fields:
            product_obj = self.pool.get('product.product')
            for line in res:
                product = product_obj.browse(cr, uid, line['product_id'][0])
                fiscal_class = product.fiscal_classification_id.code
                line.update({'fiscal_classification_id': fiscal_class})
        return res
