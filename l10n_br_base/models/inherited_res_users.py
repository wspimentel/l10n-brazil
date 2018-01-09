# -*- coding: utf-8 -*-
#
<<<<<<< Updated upstream
# Copyright 2016 Taŭga Tecnologia
=======
# Copyright 2016 Taŭga Tecnologia -
>>>>>>> Stashed changes
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

<<<<<<< Updated upstream
from odoo import api, fields, models
=======
from odoo import fields, models
>>>>>>> Stashed changes


class ResUsers(models.Model):
    _inherit = 'res.users'

    empresa_ids = fields.Many2many(
        string='Empresas Permitidas',
        comodel_name='sped.empresa',
        inverse_name='usuario_ids',
    )
