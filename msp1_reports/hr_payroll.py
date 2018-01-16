# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from urllib import urlencode
from urlparse import urljoin
from openerp import fields, osv , models
from openerp.tools.translate import _
from openerp import tools, api, netsvc
import odoo.addons.decimal_precision as dp
import base64
import time
import re

class hr_payslip(models.Model):
	_name = "hr.payslip"
	_inherit = ['hr.payslip','mail.thread']
	_description = "Pay Slip"
	
	
	def hr_verify_sheet(self, cr, uid, ids, context=None):
		temp_browse = self.browse(cr,uid,ids)
		if isinstance(temp_browse,list): temp_browse=temp_browse[0]
		emp_id = temp_browse.employee_id.id
		resource_id = temp_browse.employee_id.resource_id.id
		temp_id1 = self.pool.get('hr.employee').browse(cr,uid,emp_id)
		if resource_id:
			user_id = self.pool.get('resource.resource').browse(cr,uid,resource_id)
			if isinstance(user_id,list): user_id=user_id[0]
			login = user_id.user_id.login
		obj_mail_server = self.pool.get('ir.mail_server')
		mail_server_ids = obj_mail_server.search(cr, uid, [], context=context)
		if not mail_server_ids:
			raise osv.except_osv(_('Mail Error'), _('No mail outgoing mail server specified!'))
		mail_server_record = obj_mail_server.browse(cr, uid, mail_server_ids[0])
		if temp_id1.work_email == False:
			raise osv.except_osv(_('Email Configuration Error !'), _("Email not found !"))
		
		self.compute_sheet(cr, uid, ids, context)
		self.write(cr, uid, ids, {'state': 'verify'}, context=context)
		
		assert len(ids) == 1, 'This option should only be used for a single id at a time.'
		ir_model_data = self.pool.get('ir.model.data')
		try:
			compose_form = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form = False
		try:
			template = ir_model_data.get_object_reference(cr, uid, 'msp1_reports', 'email_template_payslip')[1]
		except ValueError:
			template = False
		
		ctx = dict(context,active_ids=ids)
		
		compose_id = self.pool.get('mail.compose.message').create(cr, uid,
			{
			'model': self._name,
			'composition_mode': 'mass_mail',
			'template_id': template,
			'post': True,
			'notify': True,
			}, context=ctx)
		
		self.pool.get('mail.compose.message').write(cr, uid, [compose_id],
			self.pool.get('mail.compose.message').onchange_template_id(
				cr, uid, [compose_id],
				template, 'mass_mail', self._name, ids[0],
				context=ctx)['value'],
				context=ctx)
		
		temp = self.pool.get('mail.compose.message').send_mail(cr, uid, [compose_id], context=ctx)
		
		return True


	@api.multi
	def get_payslip_lines_report(self, obj):
		res = []
		ids = []
		if isinstance(obj, int): obj = [obj]
		for id in range(len(obj)):
			if obj[id].appears_on_payslip is True:
				ids.append(obj[id].id)
			
		if ids:
			res = self.env['hr.payslip.line'].browse(ids)
		return res