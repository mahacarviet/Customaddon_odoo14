
from odoo import fields, models, api


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    product_warranty = fields.Char(related="product_template_id.product_warranty", string="Product Warranty")
    date_from = fields.Date(related="product_template_id.date_from", string="Warranty From")
    date_to = fields.Date(related="product_template_id.date_to",string="Warranty To")
    check_product_warranty = fields.Boolean(related="product_template_id.check_product_warranty")
    check_product_time = fields.Boolean(related="product_template_id.check_product_time", store=True)
    day_warranty = fields.Integer(related="product_template_id.day_warranty", string="Day Warranty")


    sale_order_discount_estimated = fields.Monetary(string="Discount Price", compute='_compute_discount_price')

    def _compute_discount_price(self):
        for rec in self:
            if rec.check_product_warranty == False:
                rec.sale_order_discount_estimated = rec.price_subtotal * (1 - 0.1)
            else:
                if rec.check_product_time == True:
                    rec.sale_order_discount_estimated = (1 - 0.1) / 100 * rec.price_subtotal
                else:
                    rec.sale_order_discount_estimated = rec.price_subtotal


