from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    sale_order_contract_id = fields.Many2one("contract.customer", string="Contract Customer")

    def action_confirm(self):
        check_money_debt = self.env['res.partner'].search([('id', '=', int(self.partner_id))], limit=1)
        money_debt = check_money_debt.money_debt
        money_order = self.partner_id.check_debt_customer()
        if money_order > money_debt:
            raise ValidationError(_(
                'This quotation can not be confirmed because customer exceeds the debt limit.',
            ))
        else:
            if self._get_forbidden_state_confirm() & set(self.mapped('state')):
                raise UserError(_(
                    'It is not allowed to confirm an order in the following states: %s'
                ) % (', '.join(self._get_forbidden_state_confirm())))

            for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
                order.message_subscribe([order.partner_id.id])
            self.write(self._prepare_confirmation_values())

            # Context key 'default_name' is sometimes propagated up to here.
            # We don't need it and it creates issues in the creation of linked records.
            context = self._context.copy()
            context.pop('default_name', None)

            self.with_context(context)._action_confirm()
            if self.env.user.has_group('sale.group_auto_done_setting'):
                self.action_done()
            return True

    def create_contract_customer(self):
        vals = {
            'customer_name_id': self.partner_id.id,
            'amount_total': self.amount_total,
            'signing_date': date.today(),
            'state': 'new',
            'contract_sale_order': self.ids
        }
        self.env['contract.customer'].create(vals)
