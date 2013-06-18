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

import time
import netsvc
from tools.translate import _
from osv import osv, fields

class CNABPayerInfo(osv.osv):
    _name = 'cnab.bradesco.payer_info'
    
    _columns = {
                'codigo_agencia': fields.char('Código', size=5),
                'digito_agencia': fields.char('Dígito', size=1),
                'razao_conta': fields.char('Razão', size=5),
                'numero_conta': fields.char('Número', size=7),
                'digito_conta': fields.char('Dígito', size=1),
               }
