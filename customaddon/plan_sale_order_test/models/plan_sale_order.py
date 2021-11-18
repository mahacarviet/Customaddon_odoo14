from odoo import _, models, fields, api


class PlanSaleOrder(models.Model):
    _name = 'plan.sale.order'

    name = fields.Text(string='Name Plan', required=True, tracking=True)
    quotation = fields.Many2one('sale.order', string='Quotation', readonly=True, ondelete='cascade')
    detail = fields.Text(string='Detail Information About Plan', required=True, tracking=True)
    check_sent = fields.Boolean(string='Sent or not', default=False)
    check_edited = fields.Boolean(string='Edited or not', default=False)
    check_plan_sale = fields.Boolean(compute='_compute_check_plan_sale')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approved', 'Approved'),
        ('refused', 'Refused')],
        string='Status', readonly=True, default='draft', compute='_check_status', tracking=True)
    list_partner = fields.One2many('form.approver', 'plan_id', tracking=True)

    def send_plan(self):
        self.check_sent = True
        if self.check_edited == False:
            message = _(
                'Plan "%(name)s" for quotation "%(quotation)s" was created.',
                name=self.name,
                quotation=self.quotation.name
            )
        else:
            message = _(
                'Plan "%(name)s" for quotation "%(quotation)s" was edited.',
                name=self.name,
                quotation=self.quotation.name
            )
        self.quotation.message_post(body=message, message_type='notification', subtype_xmlid='mail.mt_comment',
                                    partner_ids=self.list_partner.partner.ids)

    def _check_status(self):
        partner_num = len(self.list_partner)
        approve_num = 0
        refuse_num = 0
        for partner in self.list_partner:
            if partner.status == 'approved':
                approve_num += 1
            if partner.status == 'refused':
                refuse_num += 1
        if approve_num == partner_num and partner_num != 0:
            self.state = 'approved'
        elif refuse_num != 0:
            self.state = 'refused'
        else:
            if self.check_sent == True:
                self.state = 'sent'
            else:
                self.state = 'draft'

    @api.onchange('name', 'detail', 'list_partner')
    def _change_state_when_edited(self):
        self.state = 'draft'
        self.check_sent = False
        self.check_edited = True

    @api.depends('name')
    def _compute_check_plan_sale(self):
        for rec in self:
            if rec.name == '':
                rec.check_plan_sale = False
            else:
                rec.check_plan_sale = True
