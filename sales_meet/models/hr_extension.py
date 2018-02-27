# -*- coding: utf-8 -*-
##############################################################################
#
#	This module uses OpenERP, Open Source Management Solution Framework.
#	Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>
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
import dateutil.parser
import calendar
from odoo.addons import decimal_precision as dp


class hr_employee_category(models.Model):
	_name = "hr.employee.category"

	name  = fields.Char('Category')
	category_id  = fields.Char('Category ID')



class hr_extension(models.Model):
	_inherit = "hr.employee"

	# bp_code = fields.Char('Partner Code')
	grade_id = fields.Many2one("grade.master", string="Grade")
	c_bpartner_id = fields.Char('Idempiere ID')
	emp_id = fields.Char('Employee ID')
	date_of_joining = fields.Date("Date of Joining")
	date_of_resignation = fields.Date("Date of Resignation")
	last_date = fields.Date("Last Date Working")
	status = fields.Selection([
        ('present', 'Present'),
        ('transfer', 'Transfer'),
        ('left', 'Left')
        ], string='Status', copy=False, index=True, store=True)
	zone = fields.Selection([
        ('north', 'North'),
        ('east', 'East'),
        ('west', 'West'),
        ('south', 'South')
        ], string='Zone', copy=False, index=True, store=True)
	roll = fields.Selection([
        ('onroll', 'Onroll'),
        ('offroll', 'Offroll'),
        ('consultant', 'Consultant')
        ], string='Roll', copy=False, index=True, store=True)
	fnf = fields.Selection([
        ('na', 'NA'),
        ('pending', 'Pending'),
        ('processed', 'Processed')
        ], string='F & F', copy=False, index=True, store=True)
	category_ids = fields.Many2one("hr.employee.category", string="Category")
	category_id = fields.Char(string="Category ID" , related='category_ids.category_id')

	@api.model
	def get_ul(self, empl_id, date_from, date_to):
		# if date_to is None:
		# 	date_to = datetime.now().strftime('%Y-%m-%d')
		unpaid = self.env['hr.holidays.status'].search([('name','=','Unpaid')])
		# print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
		self._cr.execute("SELECT sum(o.number_of_days) from hr_holidays as o where \
							 o.employee_id=%s \
							 AND to_char(o.date_from, 'YYYY-MM-DD') >= %s AND to_char(o.date_to, 'YYYY-MM-DD') <= %s ",
							(empl_id, date_from, date_to))
		res = self._cr.fetchall()

		# print "JJJJJJJJJJJJJJJJJJJJJJJJJJ" , res
		return res and res[0] or 0.0


	@api.model
	def get_leaves(self, empl_id, date_from, date_to, unpaid):
		self._cr.execute("SELECT sum(o.number_of_days) from hr_holidays as o where \
							 o.employee_id=%s \
							 AND to_char(o.date_from, 'YYYY-MM-DD') >= %s AND to_char(o.date_to, 'YYYY-MM-DD') <= %s AND o.holiday_status_id = %s",
							(empl_id, date_from, date_to, unpaid))
		res = self._cr.fetchone()

		return res and res[0] or 0.0


class hr_payslip(models.Model):
	_inherit = "hr.payslip"

	unpaid_id = fields.Many2one('hr.holidays.status', string="Status",  default=lambda self: self.env['hr.holidays.status'].search([('name', '=', 'Unpaid')], limit=1))
	month_days = fields.Integer(string="Days" , store=True, track_visibility='always')

	@api.onchange('date_from','date_to')
	def _default_days(self):
		if self.date_from and self.date_to:
			date_from = self.date_from
			date_to = self.date_to
			today = datetime.now()
			daymonthfrom = datetime.strptime(date_from, "%Y-%m-%d")
			daymonthto = datetime.strptime(date_to, "%Y-%m-%d")
			monthfrom = daymonthfrom.strftime("%m")
			monthto = daymonthto.strftime("%m")
			yearfrom = int(daymonthfrom.strftime("%Y"))
			yearto = daymonthto.strftime("%Y")

			monthfrom2 =  int(monthfrom[1:] if monthfrom.startswith('0') else monthfrom)
			monthto2 =  int(monthto[1:] if monthto.startswith('0') else monthto)

			if monthfrom2 == monthto2:
				self.month_days =  calendar.monthrange(yearfrom,monthfrom2)[1]



