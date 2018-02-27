from openerp import models, fields, api, _, tools
from openerp.exceptions import UserError, Warning, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import datetime
from datetime import timedelta
import time
from dateutil import relativedelta
from cStringIO import StringIO
import xlwt
import re
import base64
import pytz

# from odoo import http
# from odoo.http import content_disposition, dispatch_rpc, request, \
#                       serialize_exception as _serialize_exception
# from odoo.addons.website.models import website


import json
import odoo.http as http
from odoo.http import request
from odoo.addons.web.controllers.main import ExcelExport


class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)

    @http.route('/web/export/xls_view', type='http', auth='user')
    def export_xls_view(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )



class meetings_details_report(models.TransientModel):
    _name = 'meetings.details.report'
    _description = "Meetings Details Report"
    
    name = fields.Char(string="MeetingsDetailsReport", compute="_get_name")
    date_from = fields.Date(string="Date From", default=lambda self: fields.datetime.now())
    date_to = fields.Date(string="Date To", default=lambda self: fields.datetime.now())
    attachment_id = fields.Many2one( 'ir.attachment', string="Attachment", ondelete='cascade')
    datas = fields.Binary(string="XLS Report", related="attachment_id.datas")
    user_id = fields.Many2one( 'res.users', string="User")
    user_ids = fields.Many2many('res.users', 'meetings_details_report_res_user_rel', string='Users')
    report = fields.Binary('Prepared file', filters='.xls', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')

    
    @api.constrains('date_from','date_to')
    @api.depends('date_from','date_to')
    def date_range_check(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_("Start Date should be before or be the same as End Date."))
        return True
    
    @api.depends('date_from','date_to')
    @api.multi
    def _get_name(self):
        rep_name = "Meetings_Details_Report"
        if self.date_from and self.date_to:
            date_from = datetime.datetime.strptime(self.date_from, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%Y')
            date_to = datetime.datetime.strptime(self.date_to, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%Y')
            if self.date_from == self.date_to:
                rep_name = "Meetings Details Report(%s).xls" % (date_from,)
            else:
                rep_name = "Meetings Details Report(%s|%s).xls" % (date_from, date_to)
        self.name = rep_name


    @api.multi
    def export_xls(self):
        context = self._context
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'calendar.event'
        datas['form'] = self.read()[0]
        for field in datas['form'].keys():
            if isinstance(datas['form'][field], tuple):
                datas['form'][field] = datas['form'][field][0]
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'sales_meet.meeting_report_xls.xlsx',
                    'datas': datas,
                    'name': 'Meetings'
                    }


    @api.multi
    def print_report(self):
        
        self.ensure_one()
        # self.sudo().unlink()
        if self.date_from and self.date_to:
            if not self.attachment_id:
                pending_order_ids = []
                order_list = []
                # file_name = self.name + '.xls'
                workbook = xlwt.Workbook(encoding='utf-8')
                worksheet = workbook.add_sheet('Meeting Details')
                fp = StringIO()
                
                main_style = xlwt.easyxf('font: bold on, height 400; align: wrap 1, vert centre, horiz center; borders: bottom thick, top thick, left thick, right thick')
                sp_style = xlwt.easyxf('font: bold on, height 350;')
                header_style = xlwt.easyxf('font: bold on, height 220; align: wrap 1,  horiz center; borders: bottom thin, top thin, left thin, right thin')
                base_style = xlwt.easyxf('align: wrap 1; borders: bottom thin, top thin, left thin, right thin')
                base_style_gray = xlwt.easyxf('align: wrap 1; borders: bottom thin, top thin, left thin, right thin; pattern: pattern fine_dots, fore_color white, back_color gray_ega;')
                base_style_yellow = xlwt.easyxf('align: wrap 1; borders: bottom thin, top thin, left thin, right thin; pattern: pattern fine_dots, fore_color white, back_color yellow;')
                
                worksheet.write_merge(0, 1, 0, 18, self.name ,main_style)
                row_index = 2
                
                worksheet.col(0).width = 4000
                worksheet.col(1).width = 8000
                worksheet.col(2).width = 8000
                worksheet.col(3).width = 8000
                worksheet.col(4).width = 12000
                worksheet.col(5).width = 8000
                worksheet.col(6).width = 8000
                worksheet.col(7).width = 8000
                worksheet.col(8).width = 8000
                worksheet.col(9).width = 12000
                worksheet.col(10).width = 8000
                worksheet.col(11).width = 8000
                worksheet.col(12).width = 8000
                worksheet.col(13).width = 8000
                worksheet.col(14).width = 8000
                worksheet.col(15).width = 8000
                worksheet.col(16).width = 8000
                worksheet.col(17).width = 8000
                worksheet.col(18).width = 8000

                
                # Headers
                header_fields = ['Sr.No','Date','Responsible','Meeting Subject','Address','Lead','Customer','Description','Source',
                'Destination','Source Address','Destination Address','Stage','Activity','Latitude','Longitude',
                'Next Activity','Next Date','Next Subject']
                row_index += 1
                
            #     # https://github.com/python-excel/xlwt/blob/master/xlwt/Style.py
                
                for index, value in enumerate(header_fields):
                    worksheet.write(row_index, index, value, header_style)
                row_index += 1

                user_id = [user.id for user in self.user_ids]


                if self.user_ids:
                    meeting_ids = self.env['calendar.event'].sudo().search([('user_id','in',user_id),('start_datetime','>=',self.date_from),('start_datetime','<=',self.date_to)])
                else:
                    meeting_ids = self.env['calendar.event'].sudo().search([('start_datetime','>=',self.date_from),('start_datetime','<=',self.date_to)])
                
                if (not meeting_ids):
                    raise Warning(_('Record Not Found'))

                if meeting_ids:
                    count = 0        
                    for meeting_id in meeting_ids:
                        po_date = ''
                        new_index = row_index

                        if meeting_id:
                            count +=1
                            worksheet.write(row_index, 0,count, base_style)
                            worksheet.write(row_index, 1,meeting_id.start_datetime, base_style)
                            worksheet.write(row_index, 2,meeting_id.user_id.name or '', base_style)
                            worksheet.write(row_index, 3,meeting_id.name or '', base_style)
                            worksheet.write(row_index, 4,meeting_id.reverse_location or '', base_style)
                            worksheet.write(row_index, 5,meeting_id.lead_id.name or '', base_style)
                            worksheet.write(row_index, 6,meeting_id.partner_id.name or '', base_style)
                            worksheet.write(row_index, 7,meeting_id.description or '', base_style)
                            worksheet.write(row_index, 8,meeting_id.source or '', base_style)
                            worksheet.write(row_index, 9,meeting_id.destination or '', base_style)
                            worksheet.write(row_index, 10,meeting_id.source_address or '', base_style)
                            worksheet.write(row_index, 11,meeting_id.destination_address or '', base_style)
                            worksheet.write(row_index, 12,meeting_id.stage_id.name or '', base_style)
                            worksheet.write(row_index, 13,meeting_id.categ_id.name or '', base_style)
                            worksheet.write(row_index, 14,meeting_id.checkin_lattitude or '', base_style)
                            worksheet.write(row_index, 15,meeting_id.checkin_longitude or '', base_style)
                            worksheet.write(row_index, 16,meeting_id.next_activity_id.name or '', base_style)
                            worksheet.write(row_index, 17,meeting_id.date_action or '', base_style)
                            worksheet.write(row_index, 18,meeting_id.title_action or '', base_style)
                            
                            
                            row_index += 1

                        # if count != 0:
                        #     worksheet.write_merge(new_index, new_index+count-1, 1, 1, meeting_id.name.strip(), base_style)


                row_index +=1
                # workbook.write(row,col+6,"Main total:",sub_header_style)
                # workbook.write(row,col+7,all_inv_total,sub_header_style)
                workbook.save(fp)
                # fp.seek(0)
                # data = fp.read()
                # fp.close()
                # encoded_data = base64.encodestring(data)
                # local_tz = pytz.timezone(self._context.get('tz') or 'UTC')
                # attach_vals = {
                #     'name':'%s' % ( file_name ),
                #     'datas':encoded_data,
                #     'datas_fname':'%s.xls' % ( file_name ),
                #     'res_model':'meetings.details.report',
                # }
                # doc_id = self.env['ir.attachment'].create(attach_vals)
                # self.attachment_id = doc_id.id

            out = base64.encodestring(fp.getvalue())
            self.write({'state': 'get','report': out,'name':'meeting_detail.xls'})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'meetings.details.report',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,
                # 'views': [(False, 'form')],
                'target': 'new',
            }
