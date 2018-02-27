# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo.tools.translate import _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import tools, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT , DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _
import logging
from odoo.osv import  osv
from odoo import SUPERUSER_ID
from time import gmtime, strftime
from openerp.exceptions import UserError , ValidationError
import requests
import urllib
import simplejson



class res_partner_extension(models.Model):
    _inherit = "res.partner"

    bp_code = fields.Char('Partner Code')
    partner_group_id = fields.Many2one("res.partner.group", string="Group")
    pan_no = fields.Char('Pan No')
    tin_no = fields.Char('Tin No')
    vat_no = fields.Char('Vat No')
    cst_no = fields.Char('Cst No')
    gst_no = fields.Char('Gst No')
    credit_limit = fields.Float(string='Credit limit')
    

class res_partner_group(models.Model):
    _name = "res.partner.group"

    name = fields.Char('Partner Group', required=False)
    value = fields.Char('Value')
    isactive = fields.Boolean("Active")
