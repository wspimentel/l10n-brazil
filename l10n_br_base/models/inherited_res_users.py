# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    empresa_ids = fields.Many2many(
        string='Empresas que este usuário tem acesso',
        comodel_name='sepd.empresa',
        reverse_name='usuario_ids',
    )
