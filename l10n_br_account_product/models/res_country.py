# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2015  Daniel Sadamo - KMEE                                    #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

from openerp import models, fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    icms_table_id = fields.One2many('state.icms.table',
                                    'origin_state_id',
                                    'Impostos por Estado')

class ResCountryStateIcmsTable(models.Model):
    _name = 'state.icms.table'

    origin_state_id = fields.Many2one('res.country.state')
    icms_tax_id = fields.Many2one('account.tax',
                                  'Alíquota do ICMS',
                                  domain=[('domain', '=','icms'),
                                          # ('type','in',('all','sale'))
                                          ])
    destination_state_id = fields.Many2one('res.country.state',
                                           'Estado de destino')
