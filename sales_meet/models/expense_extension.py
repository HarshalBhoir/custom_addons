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
import dateutil.parser
# import requests
# import urllib
# import simplejson


class expense_extension(models.Model):
	_inherit = "hr.expense"

	def _default_grade(self):
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		grade = self.env['hr.employee'].search([('id', '=', employee_id.id)]).grade_id.id
		return grade

	def _default_work_location(self):
		return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).work_location



	meeting_id = fields.Many2one("calendar.event", string="Meeting" ) #,  domain=[('user_id', 'in',[self.env.uid])]
	name = fields.Char(string='Expense Description', required=False) # related="product_id.name" ,
	grade_id = fields.Many2one("grade.master", string="Grade" , default=_default_grade, store=True, track_visibility='onchange' ) #related="employee_id.grade_id" 
	grade_amount = fields.Float(string='Amount allocated' , compute='_compute_grade_amount' , store=True, track_visibility='onchange')
	fixed_asset = fields.Boolean("Fixed Asset", store=True, track_visibility='onchange', compute='_compute_grade_amount')
	unit_amount = fields.Float(string='Unit Price', store=True, track_visibility='onchange', readonly=False )
	week_no = fields.Char(string='Week' , compute='_onchange_date' , store=True, track_visibility='onchange' , readonly=False )
	backdate_alert = fields.Boolean("Back Dated Record", store=True, track_visibility='onchange')
	work_location = fields.Char(string='Work Location', default=_default_work_location, store=True, track_visibility='onchange' , readonly=False )
	idempere_no = fields.Char(string='Idempiere No' , store=True, track_visibility='onchange' , readonly=False )
	meeting_address = fields.Char(string='Meeting Address', related="meeting_id.reverse_location" , store=True, track_visibility='onchange' , readonly=False )
	claimed_amount = fields.Float(string='Claimed Amount', store=True, track_visibility='onchange', readonly=False )


	# attach_doc_count = fields.Integer(string="Number of documents attached", compute='count_docs')

	@api.onchange('claimed_amount')
	def _onchange_claimed_amount(self):
		if self.claimed_amount:
			self.unit_amount = self.claimed_amount


	@api.onchange('product_id')
	def _onchange_product_id(self):
		amount = 0.0
		fixed_asset = False
		if self.product_id:
			if not self.name:
				self.name = self.product_id.display_name or ''

			grade_ids = self.env['grade.master'].search([('id', '=', self.grade_id.id)])
			for line_ids in grade_ids.grade_line_ids:
				for lines in line_ids:
					if lines.name.id == self.product_id.id:

						amount = lines.value
						fixed_asset = lines.fixed_asset

			# self.unit_amount = amount
			self.claimed_amount = amount
			daymonth = datetime.strptime(self.date, "%Y-%m-%d")
			month2 = daymonth.strftime("%b")
			day = daymonth.strftime("%d")
			week_day = daymonth.strftime("%A")
			year = daymonth.strftime("%Y")
			self.name = self.product_id.name + ' ' + str(day) + ' ' + str(month2) + ' ' + str(week_day) + ' ' + str(year) 
			# self.fixed_asset = fixed_asset
			# self.grade_amount = amount
			self.product_uom_id = self.product_id.uom_id
			self.tax_ids = self.product_id.supplier_taxes_id
			account = self.product_id.product_tmpl_id._get_product_accounts()['expense']
			if account:
			    self.account_id = account


	# @api.one
	@api.depends('product_id')
	def _compute_grade_amount(self):
		print "DDDDDDDDDDDDDDDDDDDDDDDD _compute_grade_amount  DDDDDDDDDDDDDDDDDDDD"
		grade_amount = 0.0
		fixed_asset = False
		grade_ids = self.env['grade.master'].search([('id', '=', self.grade_id.id)])
		for line_ids in grade_ids.grade_line_ids:
			for lines in line_ids:
				if lines.name.id == self.product_id.id:
					grade_amount = lines.value
					fixed_asset = lines.fixed_asset

		self.grade_amount = grade_amount
		self.fixed_asset = fixed_asset


	# @api.onchange('unit_amount')
	# @api.depends('grade_amount')
	# def onchange_unit_amount(self):
	# 	print "Unit Amount !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" , self.grade_amount , self.unit_amount
	# 	if self.unit_amount:

	@api.model
	def create(self, vals):
		
		result = super(expense_extension, self).create(vals)

		create_date = dateutil.parser.parse(result.create_date).date()
		back_date = create_date - timedelta(days=15 ) 
		expense_date = datetime.strptime(result.date, '%Y-%m-%d').date()
		if expense_date < back_date:
			result.backdate_alert = True

		return result



	@api.onchange('date')
	def _onchange_date(self):
		for res in self:
			if res.date:
				datey = res.date
				today = datetime.now()
				daymonth = datetime.strptime(datey, "%Y-%m-%d")
				month2 = daymonth.strftime("%b")
				week_number2 = (daymonth.day - 1) // 7 + 1
				# day_of_month = datetime.now().day
				# month = datetime.now().strftime("%b")
				# today = datetime.now()
				# week_number = (day_of_month - 1) // 7 + 1
				# create_date = datetime.strptime(self.create_date + 15, "%Y-%m-%d")

				res.week_no =  month2 + ' ' + str(week_number2) + ' Week'
				res.meeting_id = ''

			return {'domain': {
			    'meeting_id': [('user_id', 'in', [res.env.uid]),('expense_date', 'in', [res.date]),('name','!=',False)],
			}}