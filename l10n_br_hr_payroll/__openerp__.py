# -*- coding: utf-8 -*-
# (c) 2014 Kmee - Luis Felipe Mileo <mileo@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name' : 'Brazilian Localization HR Payroll',
    'description' : """
Brazilian Localization HT Payroll""",
    'category' : 'Localization',
    'author' : 'KMEE',
    'maintainer': 'KMEE',
    'website' : 'http://www.kmee.com.br',
    'version' : '0.1',
    'depends' : ['hr_payroll', 'hr_contract', 'l10n_br_hr'],
    'data': [
             'data/l10n_br_hr_payroll_data.xml',
             'view/hr_contract_view.xml',
             ],
    'test': [],
    'installable': True,
    'images': [],
    'auto_install': False,
    'license': 'AGPL-3',
}
