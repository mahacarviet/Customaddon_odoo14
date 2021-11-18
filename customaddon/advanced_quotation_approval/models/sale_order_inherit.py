from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    users_need_approve = fields.Many2many('res.users', 'sale_order_user_approve_rel', 'order_id', 'user_id', string="List user need approve quotation")
    is_submitted = fields.Boolean(string="Quotation is Submitted", default=False, copy=False)
    invisible_approve_button = fields.Boolean(string="Invisible Approve Button", compute="compute_invisible_approve_button", default=True)
    is_done_approve = fields.Boolean(string="Is Done Approve", default=False, copy=False)

    def compute_invisible_approve_button(self):
        for rec in self:
            rec.invisible_approve_button = True
            if rec.users_need_approve:
                if self.env.user.id in rec.users_need_approve.ids:
                    rec.invisible_approve_button = False

    def submit_quotation(self):
        view_form = self.env.ref('advanced_quotation_approval.user_need_approve_view_form').id
        return {
            'name': "Select Users",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'user.need.approve',
            'views': [(view_form, 'form')],
            'view_id': view_form,
            'target': 'new',
            'context': {'default_order_id': self.id},
        }

    def approve_quotation(self):
        if self.users_need_approve:
            if self.env.user.id in self.users_need_approve.ids:
                activity = self.env['mail.activity'].search([('res_model', '=', 'sale.order'), ('res_id', '=', self.id), ('user_id', '=', self.env.user.id), ('summary', '=', 'Approve Quotation')])
                if activity:
                    activity.action_done()
                if len(self.users_need_approve) == 1:
                    self.sudo().is_done_approve = True
                self.users_need_approve = [(3, self.env.user.id)]
            else:
                raise UserError("You don't need approve")
        else:
            raise UserError("No one needs approval")
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    # def approve_and_confirm(self):
    #     activity = self.env['mail.activity'].search([('res_model', '=', 'sale.order'), ('res_id', '=', self.id), ('summary', '=', 'Approve Quotation')])
    #     if activity:
    #         activity.action_done()
    #     self.sudo().is_done_approve = True
        # self.action_confirm()

    def action_confirm(self):
        self.sudo().is_done_approve = True
        return super(SaleOrderInherit, self).action_confirm()
