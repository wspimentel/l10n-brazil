# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models, _


class TipoLogradouro(models.Model):
    _name = 'esocial.tipo_logradouro'
    _description = 'Tipos de Logradouro'
    _order = 'name'
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    codigo = fields.Char(
        size=9,
        string='Codigo',
        required=True,
    )
    nome = fields.Char(
        string='Nome',
        required=True,
    )
    name = fields.Char(
        compute='_compute_name',
        store=True,
    )

    @api.depends('codigo', 'nome')
    def _compute_name(self):
        for tipo in self:
            tipo.name = tipo.codigo + '-' + tipo.nome