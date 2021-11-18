from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    customer_discount_code = fields.Char()

    check_discount_code = fields.Boolean(compute='_compute_check_discount_code', store=True)

    @api.onchange('customer_discount_code')
    def _compute_customer_discount_code(self):
        if (str(self.customer_discount_code)[0:4] == 'VIP_'):
            if (int(self.customer_discount_code[4:]) > 0) and (int(self.customer_discount_code[4:]) < 100):
                self.customer_discount_code = self.customer_discount_code
            else:
                self.customer_discount_code = ''
        else:
            self.customer_discount_code = ''

    @api.depends('customer_discount_code')
    def _compute_check_discount_code(self):
        for rec in self:
            if (str(rec.customer_discount_code)[0:4] == 'VIP_'):
                if (int(rec.customer_discount_code[4:]) > 0) and (int(rec.customer_discount_code[4:]) < 100):
                        rec.check_discount_code = True
                else:
                        rec.check_discount_code = False
            else:
                rec.check_discount_code = False

    def action_add_discount_code(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Company',
            'view_mode': 'form',
            'res_model': 'add.discount.code.customer.wizard',
            'target': 'new',
            'context': {
                'default_res_partner_ids': self.ids,
            }
        }
