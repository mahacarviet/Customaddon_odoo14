from odoo import _, models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta


class ContractCustomer(models.Model):
    _name = 'contract.customer'
    _rec_name = "contract_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    contract_id = fields.Char(string='Contract Reference', required=True, copy=False, readonly=True,
                              default=lambda self: _('New'))
    signing_date = fields.Date(default=date.today())
    amount_total = fields.Float()
    state = fields.Selection([('new', "Mới"),
                              ('done', "Hoàn thành")], default="new")
    payment_term = fields.Integer(string='Payment Term (Days)', default=7)

    check_create_activity = fields.Date(default=date.today() + timedelta(days=30))

    customer_name_id = fields.Many2one('res.partner', string='Customer Name')
    contract_sale_order = fields.One2many("sale.order", "sale_order_contract_id", string="Information Order")
    payments_contract_id = fields.One2many('contract.payments', 'contract_payment_customer', string='Payments Contract')

    @api.onchange('payment_term')
    def check_payment_term(self):
        if self.payment_term < 0:
            raise ValidationError('Payment Term Value must be greater than 0')

    def create_activity(self):
        total_percent = 0
        list_percent = self.payments_contract_id.mapped('percent_payment')
        for percent in list_percent:
            if percent:
                total_percent += percent
        if total_percent == 100:
            pass
        else:
            record_id = self.id
            term_pay = self.payment_term - 1
            if (self.check_create_activity - timedelta(days=term_pay)).strftime('%Y-%m-%d') == (date.today()).strftime(
                    '%Y-%m-%d'):
                search_group = self.env['res.groups'].search([('name', 'ilike', 'Billing')], limit=1)
                for member in search_group.users:
                    search_account = self.env['res.users'].search([('name', '=', member.name)], limit=1)
                    self.env['mail.activity'].create({
                        'summary': 'Due Debt Payment',
                        'activity_type_id': 1,
                        'date_deadline': self.check_create_activity,
                        'user_id': search_account.id,
                        'note': 'Payment Of Contract Debt.',
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'contract.customer')], limit=1).id,
                        'res_id': record_id
                    })
            else:
                pass

    @api.onchange('payments_contract_id')
    def check_onchange_payments_contract_id(self):
        if self.payments_contract_id:
            total_percent = 0
            list_percent = self.payments_contract_id.mapped('percent_payment')
            for percent in list_percent:
                if percent:
                    total_percent += percent
            if total_percent > 100:
                raise ValidationError('Total Percent Payment Value must be equal to 100')

    def action_done(self):
        self.state = 'done'

    @api.model
    def create(self, vals):
        if vals.get('contract_id', _('New')) == _('New'):
            vals['contract_id'] = self.env['ir.sequence'].next_by_code('contract.customer') or _('New')
        res = super(ContractCustomer, self).create(vals)
        print(res.id)
        return res


class ContractPayments(models.Model):
    _name = "contract.payments"
    _description = "Contract Payments"

    percent_payment = fields.Float(string='Percent Payments (%)')
    total_amount = fields.Float(compute='_compute_calculate_money')
    date_payment = fields.Date(default=date.today())
    next_date_payment = fields.Date(default=date.today() + timedelta(days=7))

    contract_payment_customer = fields.Many2one('contract.customer', string="Appointment")

    @api.depends('percent_payment')
    def _compute_calculate_money(self):
        check_percent = 0
        for rec in self:
            if rec.percent_payment > 100:
                raise ValidationError('Percent Payment Value must be smaller than 100')
            elif rec.percent_payment < 0:
                raise ValidationError('Percent Payment Value must be greater than 0')
            else:
                check_percent = check_percent + rec.percent_payment
                if check_percent <= 100:
                    rec.total_amount = rec.percent_payment / 100 * self.contract_payment_customer.amount_total
                    self.contract_payment_customer.check_create_activity = rec.next_date_payment
                else:
                    raise ValidationError('Total Percent Payment Value must be equal to 100')
