from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    money_debt = fields.Float(string='Hạn mức tiền nợ', default=10000)
    time_debt = fields.Float(string='Hạn mức thời gian nợ (Tháng)')

    contract_customer_partner = fields.One2many('contract.customer', 'customer_name_id', string='Contract Customer')

    def check_debt_customer(self):
        money_debit = 0
        for order in self.sale_order_ids:
            if not order.state == 'done' or order.state == 'cancel':
                money_debit = money_debit + order.amount_total

        for invoiced_refund in self.invoice_ids:
            if invoiced_refund.move_type == 'out_invoice':
                if invoiced_refund.payment_state in ('in_payment', 'partial', 'paid'):
                    money_debit = money_debit - invoiced_refund.amount_total + invoiced_refund.amount_residual
                # elif invoiced_refund.payment_state == 'reversed':
                #     money_debit = money_debit - invoiced_refund.amount_total
                else:
                    pass
            elif invoiced_refund.move_type == 'out_refund':
                if invoiced_refund.payment_state in ('in_payment', 'partial'):
                    money_debit = money_debit - invoiced_refund.amount_total + invoiced_refund.amount_residual
                    # money_debit = money_debit - invoiced_refund.amount_residual
                elif invoiced_refund.payment_state == 'paid':
                    money_debit = money_debit - invoiced_refund.amount_total
                else:
                    pass
            else:
                pass
        print(money_debit)
        return money_debit
