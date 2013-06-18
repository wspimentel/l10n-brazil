# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Thinkopen - Portugal & Brasil
#    Copyright (C) Thinkopen Solutions (<http://www.thinkopensolutions.com>).
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

{
    'name': 'CNAB Base',
    'version': '0.011',
    'category': 'CNAB',
    'sequence': 38,
    'complexity': 'normal',
    'description': '''== CNAB Base Module ==
CNAB export and import base module.
See other modules for bank specific formats (eg. cnab_bradesco).''',
    'author': 'ThinkOpen Solutions',
    'website': 'http://www.thinkopensolution.com',
    'images': ['images/oerp61.jpeg',],
    'depends': ['base',
                'account',
                ],
    'init_xml': [],
    'update_xml': [#'cnab_base_view.xml',
                   #'cnab_base_workflow.xml',
                   'sequence_type.xml',
                   'root_menus.xml',
                   'file_format_view.xml',
                   'res_bank_view.xml',
                   'wizard/file_format_loader_view.xml',
                   'wizard/export_cnab_view.xml',
                   'wizard/import_cnab_view.xml',
                   ],
    'demo_xml': [#'cnab_base_demo.xml',
                 ],
    'installable': True,
    'application': True,
    'certificate': '',
}
