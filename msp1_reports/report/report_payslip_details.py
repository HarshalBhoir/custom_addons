#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo.report import report_sxw
from odoo import models, fields, api, _
from odoo.addons.hr_payroll import report

# class payslip_details_report_in(report.report_payslip_details.PayslipDetailsReport):
# 
#     # def __init__(self, cr, uid, name, context):
#     #     super(payslip_details_report_in, self).__init__(cr, uid, name, context)
#     #     self.localcontext.update({
#     #         'get_details_by_rule_category': self.get_details_by_rule_category,
#     #     })
#         
#     @api.model
#     def render_html(self, docids, data=None):
#         payslips = self.env['hr.payslip'].browse(docids)
#         docargs = {
#             'doc_ids': docids,
#             'doc_model': 'hr.payslip',
#             'docs': payslips,
#             'data': data,
#             'get_details_by_rule_category': self.get_details_by_rule_category(payslips.mapped('details_by_salary_rule_category').filtered(lambda r: r.appears_on_payslip)),
#             'get_lines_by_contribution_register': self.get_lines_by_contribution_register(payslips.mapped('line_ids').filtered(lambda r: r.appears_on_payslip)),
#             # 'get_details_by_rule_category': self.get_details_by_rule_category,
#         }
#         return self.env['report'].render('hr_payroll.report_payslipdetails', docargs)

# 
# class wrapped_report_payslipdetailsin(models.TransientModel):
#     _name = 'report.msp1_reports.report_payslipdetails'
#     _inherit = 'report.abstract_report'
#     _template = 'msp1_reports.report_payslipdetails'
#     _wrapped_report_class = payslip_details_report_in
# 
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
