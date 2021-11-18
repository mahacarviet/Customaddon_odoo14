from odoo import fields, models, api


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order'

    product_template_ids = fields.Many2many('product.template', string='Product Template')

    product_warranty = fields.Char(related="product_template_ids.product_warranty", string="Product Warranty")
    date_from = fields.Date(related="product_template_ids.date_from", string="Warranty From")
    date_to = fields.Date(related="product_template_ids.date_to", string="Warranty To")
    check_product_warranty = fields.Boolean(related="product_template_ids.check_product_warranty")
    check_product_time = fields.Boolean(related="product_template_ids.check_product_time")
    day_warranty = fields.Integer(related="product_template_ids.day_warranty", string="Day Warranty")


    discount_total = fields.Monetary(compute="_compute_discount_total")

    def _compute_discount_total(self):
        for rec in self:
            if rec.check_product_warranty == False:
                rec.discount_total = (rec.amount_untaxed + rec.amount_tax) * (1 - 0.1)
            else:
                if rec.check_product_time == True:
                    rec.discount_total = (1 - 0.1) / 100 * (rec.amount_untaxed + rec.amount_tax)
