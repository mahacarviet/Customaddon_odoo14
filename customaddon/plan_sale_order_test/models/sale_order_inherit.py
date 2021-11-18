from odoo import _, models, fields
from odoo.exceptions import UserError, ValidationError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    business_plan = fields.Many2one('plan.sale.order', string='Sale Plan')
    check_plan_sale = fields.Boolean(related='business_plan.check_plan_sale', store=True)

    def _get_plan(self):
        business_plan = self.env['plan.sale.order'].search([('id', '=', id)], limit=1)
        if business_plan:
            self.business_plan = business_plan

    def action_confirm(self):
        if self.business_plan.state != 'approved':
            raise ValidationError(_(
                'This quotation can not be confirmed because the sale plan "%(business_plan)s" has not been approved.',
                business_plan=self.business_plan.name
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

