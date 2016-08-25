# -*- encoding: utf-8 -*-

# Copyright (C) 2015  Luis Felipe Miléo - KMEE                                #
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    fcp_tax_id = fields.Many2one(
        'account.tax', string=u"% Fundo de Combate à Pobreza (FCP)",
        help=u"Percentual adicional inserido na alíquota interna"
        u" da UF de destino, relativo ao Fundo de Combate à"
        u" Pobreza (FCP) em operações interestaduais com o "
        u"consumidor com esta UF. "
        u"Nota: Percentual máximo de 2%,"
        u" conforme a legislação")
    gnre_id = fields.Many2one(
        'l10n_br_tax.gnre',
        string=u'Código de recolhimento')
