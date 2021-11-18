from odoo import api, fields, models


class UserNeedApprove(models.TransientModel):
    _name = "user.need.approve"

    order_id = fields.Many2one(string="Quotation/Order", comodel_name="sale.order")
    user_ids = fields.Many2many(comodel_name="res.users", string="Users",
                                domain=lambda self: self._default_domain_ids())

    def _default_domain_ids(self):
        return [('groups_id', 'in', self.env.ref('advanced_quotation_approval.group_approve_quotation').id)]

    def confirm(self):
        # pass
        if self.order_id and self.user_ids:
            partner_id = []
            for user in self.user_ids:
                self.order_id.activity_schedule('mail.mail_activity_data_todo', summary="Approve Quotation", user_id=user.id)
                if user.partner_id:
                    partner_id.append(user.partner_id.id)
            self.order_id.update({
                'users_need_approve': [(6, 0, self.user_ids.ids)],
                'is_submitted': True
            })
            if self.order_id.partner_id:
                self.sudo().order_id.partner_id.message_subscribe(partner_ids=partner_id)
