# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.exceptions import UserError

import openerp.addons.decimal_precision as dp


class HrExpenseExpense(models.Model):

    _name = "hr.expense.expense"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Expense"
    _order = "date desc"

    name = fields.Char(string='Expense Description')
    date = fields.Date(readonly=True, states={'draft': [('readonly', False)]}, default=fields.Date.context_today, string="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    untaxed_amount = fields.Float(string='Subtotal', store=True, compute='_compute_amount', digits=dp.get_precision('Account'))
    total_amount = fields.Float(string='Total', store=True, compute='_compute_amount', digits=dp.get_precision('Account'))
    company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id.currency_id)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', states={'post': [('readonly', True)], 'done': [('readonly', True)]}, oldname='analytic_account', domain=[('account_type', '=', 'normal')])
    department_id = fields.Many2one('hr.department', string='Department', states={'post': [('readonly', True)], 'done': [('readonly', True)]})
    description = fields.Text()
    payment_mode = fields.Selection([("own_account", "Employee (to reimburse)"), ("company_account", "Company")], default='own_account', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, string="Payment By")
    journal_id = fields.Many2one('account.journal', string='Expense Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, default=lambda self: self.env['account.journal'].search([('type', '=', 'purchase')], limit=1), help="The journal used when the expense is done.")
    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, default=lambda self: self.env['account.journal'].search([('type', 'in', ['case', 'bank'])], limit=1), help="The payment method used when the expense is paid by the company.")
    account_move_id = fields.Many2one('account.move', string='Journal Entry', copy=False, track_visibility="onchange")
    attachment_number = fields.Integer(compute='_compute_attachment_number', string='Number of Attachments')
    state = fields.Selection([('draft', 'To Submit'),
                              ('submit', 'Submitted'),
                              ('approve', 'Approved'),
                              ('post', 'Waiting Payment'),
                              ('done', 'Paid'),
                              ('cancel', 'Refused')
                              ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='draft', required=True,
        help='When the expense request is created the status is \'To Submit\'.\n It is submitted by the employee and request is sent to manager, the status is \'Submitted\'.\
        \nIf the manager approve it, the status is \'Approved\'.\n If the accountant genrate the accounting entries for the expense request, the status is \'Waiting Payment\'.')
    line_ids = fields.One2many('hr.expense', 'expense_id', 'Expense Lines', copy=True)

    @api.depends('line_ids.quantity', 'line_ids.unit_amount', 'line_ids.tax_ids', 'currency_id', 'state')
    def _compute_amount(self):
        untaxed_amount = 0
        total_amount = 0
        for expense in self.line_ids:
            if expense.state not in ('cancel'):
                untaxed_amount += expense.unit_amount * expense.quantity
                taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id, expense.employee_id.user_id.partner_id)
                total_amount += taxes.get('total_included')
        self.untaxed_amount = untaxed_amount
        self.total_amount = total_amount

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group([('res_model', '=', 'hr.expense.expense'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense.id, 0)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.department_id = self.employee_id.department_id

    def _add_followers(self):
        user_ids = []
        employee = self.employee_id
        if employee.user_id:
            user_ids.append(employee.user_id.id)
        if employee.parent_id:
            user_ids.append(employee.parent_id.user_id.id)
        if employee.department_id and employee.department_id.manager_id and employee.parent_id != employee.department_id.manager_id:
            user_ids.append(employee.department_id.manager_id.user_id.id)
        self.message_subscribe_users(user_ids=user_ids)

    # @api.model
    # def create(self, vals):
    #     hr_expense = super(HrExpenseExpense, self).create(vals)
    #     if vals.get('employee_id'):
    #         hr_expense._add_followers()
    #     try:
    #         if 'employee_id' in vals and vals['employee_id']!=False and 'state' in vals and vals['state']=='submit':
    #             #send an email
    #             notification_template = self.env['ir.model.data'].sudo().get_object('opencloud_hr_expense', 'responsavel_expense_email')

    #             employee = self.env['hr.employee'].search([('id', '=', vals['employee_id'])]).parent_id.work_email

    #             if employee:
    #                 notification_template.email_to = employee

    #                 notification_template.email_from = self.employee_id.work_email

    #                 notification_template.send_mail(self.id, False)
    #     except:
    #         rah='asdaasd'
    #     return hr_expense

    # @api.multi
    # def write(self, vals):
    #     res = super(HrExpenseExpense, self).write(vals)
    #     if vals.get('employee_id'):
    #         self._add_followers()
    #     try:
    #         if 'state' in vals and vals['state']=='submit':
    #             #send an email
    #             notification_template = self.env['ir.model.data'].sudo().get_object('opencloud_hr_expense', 'responsavel_expense_email')
    #             employee = self.employee_id.parent_id.work_email
    #             if employee:
    #                 notification_template.email_to = employee

    #                 notification_template.email_from = self.employee_id.work_email

    #                 notification_template.send_mail(self.id, False)
    #     except:
    #         rah='asdaasd'

    #     return res

    @api.multi
    def unlink(self):
        if any(expense.state not in ['draft', 'cancel'] for expense in self) or any(expense.state not in ['draft'] for expense in self.line_ids):
            raise UserError(_('You can only delete draft or refused expenses!'))
        return super(HrExpenseExpense, self).unlink()

    @api.multi
    def submit_expenses(self):
        if any(expense.state != 'draft' for expense in self) or any(expense.state != 'draft' for expense in self.line_ids):
            raise UserError(_("You can only submit draft expenses!"))
        self.write({'state': 'submit'})
        for i in self.line_ids:
            i.write({'state': 'submit'})

    @api.multi
    def approve_expenses(self):
        self.write({'state': 'approve'})
        for i in self.line_ids:
            if i.state not in ['cancel']:
                i.write({'state': 'approve'})

    @api.multi
    def refuse_expenses(self, reason):
        self.write({'state': 'cancel'})
        for i in self.line_ids:
            if i.state not in ['approve']:
                i.write({'state': 'cancel'})
        if self.employee_id.user_id:
            body = (_("Your Expense %s has been refused.<br/><ul class=o_timeline_tracking_value_list><li>Reason<span> : </span><span class=o_timeline_tracking_value>%s</span></li></ul>") % (self.name, reason))
            self.message_post(body=body, partner_ids=[self.employee_id.user_id.partner_id.id])

    @api.multi
    def paid_expenses(self):
        self.write({'state': 'done'})
        for i in self.line_ids:
            if i.state not in ['cancel']:
                i.write({'state': 'done'})

    @api.multi
    def reset_expenses(self):
        self.write({'state': 'draft'})
        for i in self.line_ids:
            i.write({'state': 'draft'})

    # @api.multi
    # def _track_subtype(self, init_values):
    #     self.ensure_one()
    #     if 'state' in init_values and self.state == 'approve':
    #         return 'hr_expense.mt_expense_approved'
    #     elif 'state' in init_values and self.state == 'submit':
    #         return 'hr_expense.mt_expense_confirmed'
    #     elif 'state' in init_values and self.state == 'cancel':
    #         return 'hr_expense.mt_expense_refused'
    #     return super(HrExpense, self)._track_subtype(init_values)

    def _prepare_move_line(self, line):
        '''
        This function prepares move line of account.move related to an expense
        '''
        partner_id = self.employee_id.address_home_id.commercial_partner_id.id
        return {
            'date_maturity': line.get('date_maturity'),
            'partner_id': partner_id,
            'name': line['name'][:64],
            'debit': round(line['price'],2) > 0 and round(line['price'],2),
            'credit': round(line['price'],2) < 0 and round(-line['price'],2),
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids'),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency')) or -abs(line.get('amount_currency')),
            'currency_id': line.get('currency_id'),
            'tax_line_id': line.get('tax_line_id'),
            'ref': line.get('ref'),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id'),
            'product_uom_id': line.get('uom_id'),
            'analytic_account_id': line.get('analytic_account_id'),
        }

    @api.multi
    def _compute_expense_totals(self, company_currency, account_move_lines, move_date):
        '''
        internal method used for computation of total amount of an expense in the company currency and
        in the expense currency, given the account_move_lines that will be created. It also do some small
        transformations at these account_move_lines (for multi-currency purposes)

        :param account_move_lines: list of dict
        :rtype: tuple of 3 elements (a, b ,c)
            a: total in company currency
            b: total in hr.expense currency
            c: account_move_lines potentially modified
        '''
        self.ensure_one()
        total = 0.0
        total_currency = 0.0
        for line in account_move_lines:
            line['currency_id'] = False
            line['amount_currency'] = False
            if self.currency_id != company_currency:
                line['currency_id'] = self.currency_id.id
                line['amount_currency'] = line['price']
                line['price'] = self.currency_id.with_context(date=move_date or fields.Date.context_today(self)).compute(line['price'], company_currency, round=False)
            total -= line['price']
            total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, account_move_lines

    @api.multi
    def action_move_create(self):
        '''
        main function that is called when trying to create the accounting entries related to an expense
        '''
        if any(expense.state not in ('approve','post') for expense in self) or any(expenses.state not in ('approve','cancel','post') for expenses in self.line_ids):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if any(expense.employee_id != self[0].employee_id for expense in self) or any(expense.employee_id != self[0].employee_id for expense in self.line_ids):
            raise UserError(_("Expenses must belong to the same Employee."))

        if any(not expense.journal_id for expense in self) or any(not expense.journal_id for expense in self.line_ids):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        journal_dict = {}
        maxdate = False
        # for expense in self:
        for expense in self.line_ids:
            if expense.state!='cancel':
                if expense.date > maxdate:
                    maxdate = expense.date
                jrn = expense.bank_journal_id if expense.payment_mode == 'company_account' else expense.journal_id
                journal_dict.setdefault(jrn, [])
                journal_dict[jrn].append(expense)

        for journal, expense_list in journal_dict.items():
            try:
                #create the move that will contain the accounting entries
                move = self.env['account.move'].create({
                    'journal_id': journal.id,
                    'company_id': self.env.user.company_id.id,
                    'date': maxdate,
                })
                for expense in expense_list:
                    company_currency = expense.company_id.currency_id
                    diff_currency_p = expense.currency_id != company_currency
                    #one account.move.line per expense (+taxes..)
                    move_lines = expense._move_line_get()

                    #create one more move line, a counterline for the total on payable account
                    total, total_currency, move_lines = expense._compute_expense_totals(company_currency, move_lines, maxdate)
                    if expense.payment_mode == 'company_account':
                        if not expense.bank_journal_id.default_credit_account_id:
                            raise UserError(_("No credit account found for the %s journal, please configure one.") % (expense.bank_journal_id.name))
                        emp_account = expense.bank_journal_id.default_credit_account_id.id
                    else:
                        if not expense.employee_id.address_home_id:
                            if not expense.employee_id.user_id or not expense.employee_id.user_id.partner_id:
                                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (expense.employee_id.name))
                            else:
                                emp_account = expense.employee_id.user_id.partner_id.property_account_payable_id.id
                        else:
                            emp_account = expense.employee_id.address_home_id.property_account_payable_id.id

                    move_lines.append({
                            'type': 'dest',
                            'name': expense.employee_id.name,
                            'price': round(total,2),
                            'account_id': emp_account,
                            'date_maturity': expense.date,
                            'amount_currency': diff_currency_p and total_currency or False,
                            'currency_id': diff_currency_p and expense.currency_id.id or False,
                            'ref': expense.employee_id.address_home_id.ref or False
                            })

                    #convert eml into an osv-valid format
                    lines = map(lambda x:(0, 0, expense._prepare_move_line(x)), move_lines)
                    move.write({'line_ids': lines})
                    expense.write({'account_move_id': move.id, 'state': 'post'})

                    if expense.payment_mode == 'company_account':
                        expense.paid_expenses()
                move.post()
                if self.payment_mode == 'company_account':
                    self.paid_expenses()
                    self.write({'account_move_id': move.id})
                else:
                    self.write({'account_move_id': move.id, 'state': 'post'})

            except:
                #create the move that will contain the accounting entries
                move_lines2 = []
                for expense in expense_list:
                    company_currency = expense.company_id.currency_id
                    diff_currency_p = expense.currency_id != company_currency
                    #one account.move.line per expense (+taxes..)
                    move_lines = expense._move_line_get()

                    #create one more move line, a counterline for the total on payable account
                    total, total_currency, move_lines = expense._compute_expense_totals(company_currency, move_lines, maxdate)
                    if expense.payment_mode == 'company_account':
                        if not expense.bank_journal_id.default_credit_account_id:
                            raise UserError(_("No credit account found for the %s journal, please configure one.") % (expense.bank_journal_id.name))
                        emp_account = expense.bank_journal_id.default_credit_account_id.id
                    else:
                        if not expense.employee_id.address_home_id:
                            if not expense.employee_id.user_id or not expense.employee_id.user_id.partner_id:
                                raise UserError(_("No Home Address found for the employee %s, please configure one.") % (expense.employee_id.name))
                            else:
                                emp_account = expense.employee_id.user_id.partner_id.property_account_payable_id.id
                        else:
                            emp_account = expense.employee_id.address_home_id.property_account_payable_id.id

                    move_lines.append({
                            'type': 'dest',
                            'name': expense.employee_id.name,
                            'price': round(total,2),
                            'account_id': emp_account,
                            'date_maturity': expense.date,
                            'amount_currency': diff_currency_p and total_currency or False,
                            'currency_id': diff_currency_p and expense.currency_id.id or False,
                            'ref': expense.employee_id.address_home_id.ref or False
                            })

                    for pos in map(lambda x:(0, 0, expense._prepare_move_line(x)), move_lines):
                        move_lines2.append(pos)

                    if expense.payment_mode == 'company_account':
                        expense.paid_expenses()
                #### create do move ####
                move = self.env['account.move'].create({
                    'journal_id': journal.id,
                    'company_id': self.env.user.company_id.id,
                    'date': maxdate,
                    'line_ids': move_lines2
                })
                move.post()
                if self.payment_mode == 'company_account':
                    self.paid_expenses()
                    self.write({'account_move_id': move.id})
                    for i in self.line_ids:
                        i.write({'account_move_id': move.id})
                else:
                    self.write({'account_move_id': move.id, 'state': 'post'})
                    for i in self.line_ids:
                        i.write({'account_move_id': move.id, 'state': 'post'})

        return True

    @api.multi
    def _move_line_get(self):
        account_move = []
        for expense in self:
            if expense.product_id:
                account = expense.product_id.product_tmpl_id._get_product_accounts()['expense']
                if not account:
                    raise UserError(_("No Expense account found for the product %s (or for it's category), please configure one.") % (expense.product_id.name))
            else:
                account = self.env['ir.property'].with_context(force_company=expense.company_id.id).get('property_account_expense_categ_id', 'product.category')
                if not account:
                    raise UserError(_('Please configure Default Expense account for Product expense: `property_account_expense_categ_id`.'))
            move_line = {
                    'type': 'src',
                    'name': expense.name.split('\n')[0][:64],
                    'price_unit': expense.unit_amount,
                    'quantity': expense.quantity,
                    'price': round(expense.total_amount,2),
                    'account_id': account.id,
                    'product_id': expense.product_id.id,
                    'uom_id': expense.product_uom_id.id,
                    'analytic_account_id': expense.analytic_account_id.id,
                }
            account_move.append(move_line)

            # Calculate tax lines and adjust base line
            taxes = expense.tax_ids.compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            account_move[-1]['price'] = round(taxes['total_excluded'],2)
            account_move[-1]['tax_ids'] = expense.tax_ids.id
            for tax in taxes['taxes']:
                account_move.append({
                    'type': 'tax',
                    'name': tax['name'],
                    'price_unit': tax['amount'],
                    'quantity': 1,
                    'price': round(tax['amount'],2),
                    'account_id': tax['account_id'] or move_line['account_id'],
                    'tax_line_id': tax['id'],
                })
        return account_move

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'hr.expense.expense'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.expense.expense', 'default_res_id': self.id}
        return res

class HrExpenseInherit(models.Model):
    _inherit = "hr.expense"

    @api.model
    def _get_default_product_id(self):
        product_def=False
        product = self.env['product.product'].search([('can_be_expensed', '=', True)], limit=1)
        if product:
            product_def = product
    
        return product_def
 
    expense_id = fields.Many2one('hr.expense.expense', 'Expense', ondelete='cascade') #, select=True
    product_id = fields.Many2one('product.product', string='Product',  domain=[('can_be_expensed', '=', True)], required=True, default=_get_default_product_id) #, default=_get_default_product_id

    @api.model
    def create(self, vals):
        print "GGGGGGGGGGGGGGGGGGGGGGG"
        if not vals.get('payment_mode'):
            if vals.get('expense_id'):
                menu = self.env['hr.expense.expense'].browse(vals.get('expense_id')).payment_mode
                vals['payment_mode']=menu

        print "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP" , vals
        hr_expense = super(HrExpenseInherit, self).create(vals)

        print "LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL" , hr_expense
        return hr_expense

    def _prepare_move_line(self, line):
        '''
        This function prepares move line of account.move related to an expense
        '''
        partner_id = self.employee_id.address_home_id.commercial_partner_id.id
        return {
            'date_maturity': line.get('date_maturity'),
            'partner_id': partner_id,
            'name': line['name'][:64],
            'debit': round(line['price'],2) > 0 and line['price'],
            'credit': round(line['price'],2) < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids'),
            'amount_currency': line['price'] > 0 and abs(line.get('amount_currency')) or -abs(line.get('amount_currency')),
            'currency_id': line.get('currency_id'),
            'tax_line_id': line.get('tax_line_id'),
            'ref': line.get('ref'),
            'quantity': line.get('quantity',1.00),
            'product_id': line.get('product_id'),
            'product_uom_id': line.get('uom_id'),
            'analytic_account_id': line.get('analytic_account_id'),
        }

    @api.multi
    def refuse_expenses(self, reason):
        expense = self.expense_id
        self.write({'state': 'cancel'})
        # expense.write({'description': reason})
        if self.employee_id.user_id:
            body = (_("Your Expense %s has been refused.<br/><ul class=o_timeline_tracking_value_list><li>Reason<span> : </span><span class=o_timeline_tracking_value>%s</span></li></ul>") % (self.name, reason))
            expense.message_post(body=body, partner_ids=[self.employee_id.user_id.partner_id.id])
