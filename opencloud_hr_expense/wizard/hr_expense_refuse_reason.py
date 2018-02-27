# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models


class HrExpenseExpenseRefuseWizard(models.TransientModel):

    _name = "hr.expense.expense.refuse.wizard"
    _description = "Hr Expense refuse Reason wizard"

    description = fields.Char(string='Reason', required=True)

    @api.multi
    def expense_refuse_reason(self):
        self.ensure_one()

        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        active_model = context.get('active_model', [])
        if active_model=='hr.expense.expense':
            expense = self.env['hr.expense.expense'].browse(active_ids)
            expense.refuse_expenses(self.description)
        if active_model=='hr.expense':
            expense_line = self.env['hr.expense'].browse(active_ids)
            expense_line.refuse_expenses(self.description)
        return {'type': 'ir.actions.act_window_close'}
