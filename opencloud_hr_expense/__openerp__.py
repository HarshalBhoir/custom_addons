# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#Manage expenses by Employees
#This application allows you to add lines to expenses.

{
    'name': 'Expense Tracker - Update',
    'author': 'Opencloud',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 95,
    'summary': 'Expenses Validation, Invoicing',
    'support': 'geral@opencloud.pro',
    'description': "Allows you to assign multiple expenses at the same time",
    'website': 'http://opencloud.pro',
    'depends': ['hr_contract', 'account_accountant', 'report', 'hr_expense'],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'wizard/expense_payment.xml',
        'wizard/hr_expense_refuse_reason.xml',
        'views/hr_expense_views.xml',
        # 'views/report_expense.xml',
        'views/hr_dashboard.xml',
        'email_project_task.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'images': ['images/Expenses_Update1.png'],
    'currency': 'INR',
}
