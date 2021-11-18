from odoo import fields, models, api
from datetime import *

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    date_from = fields.Date(string="Warranty From")
    date_to = fields.Date(string="Warranty To")
    product_warranty = fields.Char(compute="_compute_product_warranty", string="Product Warranty")
    check_product_warranty = fields.Boolean(compute="_compute_check_product_warranty")
    check_product_time = fields.Boolean(compute="_compute_check_product_time", store=True)
    day_warranty = fields.Integer(compute="_compute_day_warranty", string="Day Warranty")

    # @api.depends('date_to')
    def _compute_check_product_time(self):
        for rec in self:
            if rec.check_product_warranty == True:
                if (rec.date_to == '') or (rec.date_from == ''):
                    rec.check_product_time = False
                else:
                    if date.today() < rec.date_to:
                        rec.check_product_time = True
                    else:
                        rec.check_product_time = False
            else:
                rec.check_product_time = False

    # @api.depends('date_to', 'date_from')
    def _compute_product_warranty(self):
        for rec in self:
            if (rec.date_to == '') or (rec.date_from == ''):
                rec.product_warranty = ''
            else:
                if rec.date_from < rec.date_to:
                    print(rec.date_to > rec.date_from)
                    rec.product_warranty = "PWR/" + rec.date_from.strftime("%d%m%y") + "/" + rec.date_to.strftime("%d%m%y")
                else:
                    rec.product_warranty = ''

    @api.depends('product_warranty')
    def _compute_check_product_warranty(self):
        for rec in self:
            if rec.product_warranty != '':
                rec.check_product_warranty = True
            else:
                rec.check_product_warranty = False

    @api.depends('date_to', 'check_product_time')
    def _compute_day_warranty(self):
        for rec in self:
            if rec.check_product_time == True:
                rec.day_warranty = (rec.date_to - date.today()).days
            else:
                rec.day_warranty = ''

    def action_update_product_warranty(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Company',
            'view_mode': 'form',
            'res_model': 'update.product.warranty.wizard',
            'target': 'new',
            'context': {
                'default_product_template_wizard': self.ids,
            }
        }
