# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class CodigoAliquotaFPAS(models.Model):
    _name = "esocial.codigo_aliquota"
    _description = "Códigos e Alíquotas de FPAS/Terceiros"
    _order = 'codigo'

    codigo = fields.Char(
        size=3,
        string='Código FPAS',
        required=True,
    )
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]
    codigo_tributaria_fpas_ids = fields.Many2many(
        'esocial.classificacao_tributaria',
        string='Código',
        relation='tributaria_fpas_ids',
    )

    nome = fields.Text(
        string='Classificação Tributária',
    )

    descricao = fields.Text(
        string='Descrição',
        required=True,
    )

    name = fields.Char(
        compute='_compute_name',
        store=True,
    )

    @api.onchange('codigo')
    def _valida_codigo(self):
        for codigo_aliguota in self:
            if codigo_aliguota.codigo:
                if codigo_aliguota.codigo.isdigit():
                    codigo_aliguota.codigo = codigo_aliguota.codigo.zfill(1)
                else:
                    res = {'warning': {
                        'title': _('Código Incorreto!'),
                        'message': _('Campo Código somente aceita números!'
                                     ' - Corrija antes de salvar')
                    }}
                    codigo_aliguota.codigo = False
                    return res

    @api.depends('codigo', 'descricao')
    def _compute_name(self):
        for codigo_aliguota in self:
            codigo_aliguota.name = codigo_aliguota.codigo