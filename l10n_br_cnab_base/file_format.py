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

FORMAT_TYPES = ('Arquivo-Remessa', 'Arquivo-Retorno')

class FileFormat(osv.osv):
    _name = 'cnab.file_format'

    _columns = {
                'name': fields.char('Name', size=256),
                'version': fields.char('Version', size=256),
                'description': fields.text('Description'),
                'records_ids': fields.one2many('cnab.record_format', 'file_id', 'Records'),
                'type': fields.selection(zip(FORMAT_TYPES, FORMAT_TYPES), 'Type', required=True),
                }

class RecordFormat(osv.osv):
    _name = 'cnab.record_format'
    
    def _get_id(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for recordformat in self.browse(cr, uid, ids):
            res[recordformat.id] = recordformat.fields_ids[0].value
        return res
    
    _columns = {
                'file_id': fields.many2one('cnab.file_format', 'File'),
                'record_id': fields.many2one('cnab.record_format', 'Parent Record'),
                'identifier': fields.function(_get_id, method=True, type='char', string="IdType"),
                'name': fields.char('Name', size=256),
                'description': fields.char('Description', size=256),
                'repeatable': fields.boolean('repeatable'),
                'records_ids': fields.one2many('cnab.record_format', 'record_id', 'Inner Records'),
                'fields_ids': fields.one2many('cnab.field_format', 'record_id', 'Fields'),
                }

class FieldFormat(osv.osv):
    _name = 'cnab.field_format'
    
    VALID_TYPES = ('STRING', 'CHARACTER', 'INTEGER', 'DATE', 'BIGDECIMAL')
    VALID_FORMATS = ('DATE_DDMMYY', 'DECIMAL_DD')
    VALID_PADDINGS = ('ZERO_LEFT',)
    
    InternalTypes = ('IdType', 'Field', 'SequencialNumber')
    
    _columns = {
                'record_id': fields.many2one('cnab.record_format', 'Record'),
                'sequence': fields.integer('Sequence'),
                'type': fields.selection(zip(InternalTypes, InternalTypes), 'Type'),
                'name': fields.char('Name', size=256),
                'value': fields.char('Value', size=256),
                'length': fields.integer('Length'),
                'position': fields.integer('Position'),
                'value_type': fields.selection(zip(VALID_TYPES, VALID_TYPES), 'Value Type'),
                'format': fields.selection(zip(VALID_FORMATS, VALID_FORMATS), 'Format'),
                'padding': fields.selection(zip(VALID_PADDINGS, VALID_PADDINGS), 'Padding'),
                }
    
    _order = 'sequence'
