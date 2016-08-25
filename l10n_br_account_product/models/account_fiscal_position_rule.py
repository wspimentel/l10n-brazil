# -*- coding: utf-8 -*-

# Copyright (C) 2015 - Luis Felipe Miléo - KMEE                               #
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import time

from openerp import models, fields, api


class AccountFiscalPositionRule(models.Model):
    _inherit = 'account.fiscal.position.rule'

    def product_fcp_map(self, product_id, to_state=None):
        result = self.env['account.tax']
        fiscal_classification_id = self.env['product.product'].browse(
            product_id).fiscal_classification_id
        fcp = self.env[
            'l10n_br_tax.fcp'].search(
            [('fiscal_classification_id', '=', fiscal_classification_id.id),
             '|', ('to_state_id', '=', False),
             ('to_state_id', '=', to_state.id)])
        if fcp:
            result |= fcp.fcp_tax_id
        else:
            result |= to_state.fcp_tax_id
        return result
