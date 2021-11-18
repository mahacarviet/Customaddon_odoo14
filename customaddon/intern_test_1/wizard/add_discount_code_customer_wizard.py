from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AddDiscountCodeCustomerWizard(models.TransientModel):
    _name = 'add.discount.code.customer.wizard'

    input_code = fields.Char(string='Discount Code')
    res_partner_ids = fields.Many2many('res.partner',
                                       string='Partner')

    def action_add_discount_code(self):
        for rec in self:
            if rec.res_partner_ids:
                # truy cap tung thang partner de them discount code
                for partner in rec.res_partner_ids:
                    # them input code vao tung thang partner
                    partner.customer_discount_code = rec.input_code

