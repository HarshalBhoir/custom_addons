from openerp import models, fields, api, _, tools
import datetime
import time
import xlwt
from cStringIO import StringIO
import re
import base64
from openerp import http
from openerp.addons.web.controllers.main import serialize_exception,content_disposition
from openerp.http import request, serialize_exception as _serialize_exception
import pytz
from openerp.exceptions import UserError

class Binary(http.Controller):
	 
	@http.route('/web/binary/download_document', type='http', auth="public")
	@serialize_exception
	def download_document(self,model,field,id,filename=None, **kw):
		""" Download link for files stored as binary fields.
		:param str model: name of the model to fetch the binary from
		:param str field: binary field
		:param str id: id of the record from which to fetch the binary
		:param str filename: field holding the file's name, if any
		:returns: :class:`werkzeug.wrappers.Response`
		"""
		Model = request.registry[model]
		cr, uid, context = request.cr, request.uid, request.context
		fields = [field]
		res = Model.read(cr, uid, [int(id)], fields, context)[0]
		filecontent = base64.b64decode(res.get(field) or '')
		if not filecontent:
			 return request.not_found()
		else:
			if not filename:
				filename = '%s_%s' % (model.replace('.', '_'), id)
			return request.make_response(filecontent,[
					('Content-Disposition', content_disposition(filename)),
					('Content-Type', 'application/vnd.ms-excel'),
					# ('Content-Type', 'application/octet-stream'),
					('Content-Length', len(filecontent))
			])


class hr_payslip_run_extension(models.Model):
    _inherit = 'hr.payslip.run'
    
    date = fields.Date(string="Date")
    company_id = fields.Many2one('res.company',string="Company", default=lambda self: self.env['res.company']._company_default_get())
    
    ### Customers Report
    @api.multi
    def hr_employee_report(self):
        # Column Headers
        if self.date:
            heading = "Salary Up-Load"
            company = self.company_id.name
            date =  datetime.datetime.strptime(self.date, tools.DEFAULT_SERVER_DATE_FORMAT).strftime('%d-%b-%Y')
            date1 =  datetime.datetime.strptime(self.date, tools.DEFAULT_SERVER_DATE_FORMAT)
            month = date1.strftime('%B')
            year = date1.strftime('%Y')
            file_name = "Salary Upload For %s %s" % (month, year)
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet 1')
            sp_style = xlwt.easyxf('font: bold on, height 200; borders: bottom thin, top thin, left thin, right thin')
            base_style = xlwt.easyxf('align: wrap 1; borders: bottom thin, top thin, left thin, right thin')
            worksheet.write_merge(0, 0, 0, 2, heading, sp_style)
            worksheet.write_merge(2, 2, 0, 0, "Company", sp_style)
            worksheet.write_merge(2, 2, 1, 4, company, sp_style)
            worksheet.write_merge(4, 4, 0, 0, "Date", sp_style)
            worksheet.write_merge(4, 4, 1, 1, date, sp_style)
            row_index = 6

            headers = ['Sr. No','Employee Code','Account Number','Employee Name','Dr./Cr.','Amount','Narration']

            for index, value in enumerate(headers):
            	worksheet.write(row_index, index, value, sp_style)
            	worksheet.col(0).width = 3000
            	worksheet.col(1).width = 4000
            	worksheet.col(2).width = 5000
            	worksheet.col(3).width = 5000
            	worksheet.col(4).width = 2000
            	worksheet.col(5).width = 4000
            	worksheet.col(6).width = 6000
            row_index += 1
            narretion =  "Salary For %s %s" % (month, year)     
            sn = 1
            for record in self.slip_ids:
            	net = 0
            	for emp in record:
            		for line in emp.line_ids:
            			if line.code == "NET":
            				net = line.amount
            	worksheet.write(row_index, 0, str(sn), base_style)
            	worksheet.write(row_index, 1, record.employee_id.id, base_style)
            	worksheet.write(row_index, 2, record.employee_id.bank_account_id.acc_number, base_style)
            	worksheet.write(row_index, 3, record.employee_id.name, base_style)
            	worksheet.write(row_index, 4, 'Cr', base_style)
            	worksheet.write(row_index, 5, net, base_style)
            	worksheet.write(row_index, 6, narretion, base_style)
            	sn +=1
            	row_index += 1
 
            fp = StringIO()
            workbook.save(fp)
            fp.seek(0)
            data = fp.read()
            fp.close()
            encoded_data = base64.encodestring(data)
            local_tz = pytz.timezone(self._context.get('tz') or 'UTC')
            attach_vals = {
            	'name':'%s' % ( file_name ),
            	'datas':encoded_data,
            	'datas_fname':'%s.xls' % ( file_name ),
            	'res_model':'hr.payslip.run',
            }
            doc_id = self.env['ir.attachment'].create(attach_vals)
            return {
            	'type' : 'ir.actions.act_url',
            	'url': '/web/binary/download_document?model=%s&field=%s&id=%s&filename=%s.xls' % ('ir.attachment','datas',doc_id.id,doc_id.name),
            	'target': 'self',
            }
        else :
             raise UserError("Please Insert Date.") 

