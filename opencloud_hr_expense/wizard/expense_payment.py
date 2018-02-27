# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class HrExpensePayment(models.TransientModel):

    _name = "expense.payment"
    _description = "Hr Expense Payment"

    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    expense_id = fields.Many2one('hr.expense.expense', string='Expense', required=True, default=lambda self: self._context.get('expense_id', False))

    @api.multi
    def create_payment(self):
        ####Pagamentos automaticos
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        currency_pool = self.env['res.currency']
        seq_obj = self.env['ir.sequence']
        for pag in self.browse(self.ids):
            # if not inv.modo_pagar_vd or  inv.modo_pagar_vd.id == False:
            #     raise osv.except_osv('Aviso', 'Deve preencher o campo diario de pagamento de VDs na aba outras informacoes.')
            numero_pagamento=''
            # if inv.modo_pagar_vd:
            #     numero_pagamento=seq_obj.get_id(cr, uid, inv.modo_pagar_vd.sequence_id.id)

            for expense in self.env['hr.expense.expense'].browse(pag.expense_id.id):
                move_lines = []
                if expense.account_move_id:
                    for i in expense.line_ids:
                        if i.state!='cancel' and i.state!='done':
                            rec_list_ids = []
                            company_currency = pag.journal_id.company_id.currency_id
                            current_currency = i.currency_id
                            debit = 0.0
                            credit = 0.0
                            # TODO: is there any other alternative then the voucher type ??
                            # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt

                            credit= currency_pool._compute(current_currency, company_currency, i.total_amount)
                            debit=0
                            if credit < 0:
                                debit = -credit
                                credit = 0.0
                            sign = debit - credit < 0 and -1 or 1

                            ##### get account_id #####
                            if not i.employee_id.address_home_id:
                                emp_account = i.employee_id.user_id.partner_id.property_account_payable_id.id
                            else:
                                emp_account = i.employee_id.address_home_id.property_account_payable_id.id

                            #primeira linha do movimento - credito a clientes
                            move_line_cliente = {
                                'name': i.name or '/',
                                'ref': expense.name,
                                'debit': round(credit,2),
                                'credit': round(debit,2),
                                'account_id': emp_account,
                                'quantity': 1,
                                'journal_id': pag.journal_id and pag.journal_id.id or False,
                                'partner_id': i.employee_id.user_id and i.employee_id.user_id.partner_id and i.employee_id.user_id.partner_id.id or False,
                                'currency_id': company_currency <> current_currency and  current_currency or False,
                                'amount_currency': company_currency <> current_currency and sign * i.total_amount or 0.0,
                                'date': i.date,
                                # 'date_maturity': expense.date
                            }

                            move_lines.append((0,0,move_line_cliente))

                            #segunda linha do movimento - debita caixa

                            sign = debit - credit < 0 and -1 or 1
                            move_line_caixa = {
                                'name': i.name or '/',
                                'ref': expense.name,
                                'debit': round(debit,2),
                                'credit': round(credit,2),
                                'account_id': pag.journal_id and pag.journal_id.default_debit_account_id.id or False,
                                'journal_id': pag.journal_id.id,
                                'partner_id': i.employee_id.user_id and i.employee_id.user_id.partner_id and i.employee_id.user_id.partner_id.id or False,
                                'currency_id': company_currency <> current_currency and  current_currency or False,
                                'amount_currency': company_currency <> current_currency and sign * i.total_amount or 0.0,
                                'date': i.date,
                                # 'date_maturity': expense.date
                            }

                            move_lines.append((0,0,move_line_caixa))

                    if pag.journal_id.refund_sequence_id:
                        move = {
                            'name': self.pool.get('ir.sequence').next_by_id(self._cr, self._uid, pag.journal_id.refund_sequence_id.id),
                            'journal_id': pag.journal_id and pag.journal_id.id or False,
                            'narration': expense.description,
                            'date': i.date,
                            'ref': expense.name,
                            'line_ids': move_lines
                        }
                        move_id = move_pool.create(move)

                        move_id.post()

                        lista_l_expense=[]
                        lista_l_payment=[]
                        for i in expense.line_ids:
                            if i.state!='cancel' and i.state!='done':
                                #reconciliar
                                if lista_l_expense!=[]:
                                    lista_exp = str(lista_l_expense).replace('[','(').replace(']',')')
                                    #### so apanha uma linha 2211
                                    self._cr.execute("select id from account_move_line where move_id="+str(expense.account_move_id.id)+" and account_id="+str(emp_account)+" and credit="+str(round(i.total_amount,2))+" and id not in "+str(lista_exp))
                                    line_fatura=self._cr.fetchone()[0]
                                else:
                                    #### so apanha uma linha 2211
                                    self._cr.execute("select id from account_move_line where move_id="+str(expense.account_move_id.id)+" and account_id="+str(emp_account)+" and credit="+str(round(i.total_amount,2)))
                                    line_fatura=self._cr.fetchone()[0]

                                if lista_l_payment!=[]:
                                    lista_pay = str(lista_l_payment).replace('[','(').replace(']',')')
                                    ###
                                    self._cr.execute("select id from account_move_line where move_id="+str(move_id.id)+" and account_id="+str(emp_account)+" and debit="+str(round(i.total_amount,2))+" and id not in "+str(lista_pay))
                                    line_id_cliente=self._cr.fetchone()[0]
                                else:
                                    ###
                                    self._cr.execute("select id from account_move_line where move_id="+str(move_id.id)+" and account_id="+str(emp_account)+" and debit="+str(round(i.total_amount,2)))
                                    line_id_cliente=self._cr.fetchone()[0]

                                data = {
                                    'debit_move_id': line_id_cliente,
                                    'credit_move_id': line_fatura,
                                    'amount': round(i.total_amount,2),
                                }

                                move_reconcile= self.env['account.partial.reconcile'].create(data)

                                lista_l_expense.append(line_fatura)
                                lista_l_payment.append(line_id_cliente)

                                if move_reconcile.full_reconcile_id:
                                    i.paid_expenses()

                        #### se todas as linhas tiverem pagas, a despesa fica como paga ####
                        self._cr.execute("select count(id) from hr_expense where expense_id="+str(expense.id)+" and state not in ('done','cancel')")
                        count=self._cr.fetchone()[0]
                        if count==0:
                            expense.paid_expenses()
                    else:
                        raise UserError(_('Please define a Refund Sequence on Journal!'))

                else:
                    raise UserError(_('Please define a Journal Entry on the expense!'))
