from odoo import _, models, fields


class FormApprover(models.Model):
    _name = "form.approver"


    plan_id = fields.Many2one('plan.sale.order', string='Sale Plan', ondelete='cascade')
    partner = fields.Many2one('res.partner', string='Approver')
    status = fields.Selection(string='Status', selection=[
        ('pending', 'Waiting for Approvement'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], required=True, default='pending')
    check_current_account = fields.Boolean(default=False, compute='_check_current_account')

    def check_approve(self):
        self.status = 'approved'
        message = _(
            '%(partner_name)s approved the plan "%(business_plan_name)s".',
            partner_name=self.partner.display_name,
            business_plan_name=self.plan_id.name
        )
        self.plan_id.quotation.message_post(body=message, message_type='notification', subtype_xmlid='mail.mt_comment',
                                            partner_ids=self.plan_id.ids)

    def check_refuse(self):
        self.status = 'refused'
        message = _(
            '%(partner_name)s refused the plan "%(business_plan_name)s".',
            partner_name=self.partner.display_name,
            business_plan_name=self.plan_id.name,
        )
        self.plan_id.quotation.message_post(body=message, message_type='notification', subtype_xmlid='mail.mt_comment',
                                            partner_ids=self.plan_id.ids)

    def _check_current_account(self):
        for rec in self:
            if rec.env.user.partner_id.id == rec.partner.id:
                rec.check_current_account = True
            else:
                rec.check_current_account = False
