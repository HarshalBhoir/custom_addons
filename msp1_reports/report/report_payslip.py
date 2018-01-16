#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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

# from openerp import api, tools
# from openerp.osv import osv
# from openerp.report import report_sxw
# from openerp.addons.hr_payroll.report import report_payslip
# 
# class payslip_report(report_payslip.payslip_report):
# 
#     def __init__(self, cr, uid, name, context):
#         super(payslip_report, self).__init__(cr, uid, name, context)
#         self.localcontext.update({
#             'get_payslip_lines': self.get_payslip_lines,
#         })
#         self.context = context
# 
#     @api.multi
#     def get_payslip_lines(self, obj):
#         res = []
#         ids = []
#         for id in range(len(obj)):
#             if obj[id].appears_on_payslip is True:
#                 ids.append(obj[id].id)
#             print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",obj[id]
#         if ids:
#             res = self.env['hr.payslip.line'].browse(ids)
#         return res
# 
# 
# class wrapped_report_payslip(report_payslip.wrapped_report_payslip,payslip_report):
#     _name = 'report.msp1_reports.report_payslip'
#     _inherit = 'report.abstract_report'
#     _template = 'msp1_reports.report_payslip'
#     _wrapped_report_class = payslip_report
#  
#     @api.multi
#     def render_html(self, data=None):
#         
#         report_obj = self.env['report']
#         report = report_obj._get_report_from_name(self._template)
#        
#         docargs = {
#             'get_payslip_lines': self.get_payslip_lines,
#             'doc_ids': self._ids,
#             'doc_model': report.model,
#             'docs': self,
#         }
#         return report_obj.render(self._template, docargs)
# 
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
