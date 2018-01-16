# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
	'name': 'MSP1 Reports Enhancements',
	'version': '1.0',
	'category': 'Extra Tools',
	'sequence': 1,
	'summary': 'MSP1 Reports Enhancements',
	'description': """
MSP1 Enhancements
========================================================================================================================================
You can manage:
---------------
*  MSP1 Enhancements
------------------------------------------------------ ------------------------------------------------------ ---------------------------
	""",
	'author': 'Aqua-Giraffe',
	'website': 'http://www.aqua-giraffe.com/',
	'depends': ['base','report','account','sale','crm','hr','stock','hr_payroll','l10n_in_hr_payroll','hr_expense','mail'],
	'init_xml': [],
	'data': [
		'security/ir_rule.xml',
		'account_invoice_view.xml',
		'hr_payroll_view.xml',
		'hr_payroll_report.xml',
		'payslip_batches_xls_report.xml',
		'views/layouts.xml',
		# 'views/msp1_reports.xml',
		'views/report_payslip.xml',
		'views/report_payslipdetails.xml',
		'views/report_payrolladvice.xml',
		'views/report_invoice.xml',
		'views/report_expense.xml',
		'views/report_contributionregister.xml',
		'views/report_saleorder.xml',
		'views/report_stockinventory.xml',
		'views/crm_lead_extension_view.xml',
		],
	'demo_xml': [],
	'installable': True,
	'application': True,
	'auto_install': True,
	'qweb': [],
}
