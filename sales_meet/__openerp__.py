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
{
    'name': 'Meetings',
    'category': 'CRM',
    'version': '1.0',
    'sequence': 1,
    'description': """
    Task on Lead, Add Task from lead, Task Lead, Create Project Task from Lead, 
    Add task from mail, Create task from mail.Task on lead, add task on lead, tasks on lead,
     lead tasks, automated task by lead, 
    Generate task from lead.
""",
    'author': 'Harshal Bhoir (Walplast)',
    'website': 'https://harshalbhoir.github.io/',
    'images': [],
    'depends': ['base', 'calendar', 'crm', 'sale', 'project','hr','purchase','hr_expense','website',
                'hr_timesheet','hr_holidays','stock','sales_team','account','hr_payroll','hr_attendance'],
    
    'data': [ 
            'security/sales_meet_security.xml',
            'security/ir.model.access.csv',
            'static/src/xml/sales_meet_template.xml',
            # 'report/meetings_details_reports_view.xml',
            'views/expense_extension_view.xml',
            'views/grade_master_view.xml',
            'report/meeting_report_xls_view.xml',
            'data/scheduler_data.xml',
            'views/sales_meet_view.xml',
            'views/partner_extension_view.xml',
            'views/hr_extension_view.xml',
            'views/crm_extension_view.xml',
            'views/sales_meet_menus.xml',

             
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# https://stackoverflow.com/questions/39223570/how-to-set-a-field-editable-only-for-a-group-in-odoo9