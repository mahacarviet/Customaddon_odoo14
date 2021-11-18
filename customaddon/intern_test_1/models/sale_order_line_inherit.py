from odoo import fields, models, api


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    discount_code = fields.Char(related="order_partner_id.customer_discount_code", string="Discount Code")
    check_discount_code = fields.Boolean(related="order_partner_id.check_discount_code", string="Check Discount Code")


    sale_order_discount_estimated = fields.Monetary(string="Discount Price", compute='_compute_discount_price')
    discount_total = fields.Float(compute="_compute_discount_total")
    # discount_temp = fields.Float()


    def _compute_discount_price(self):
        for rec in self:
            if rec.check_discount_code == False:
                rec.sale_order_discount_estimated = rec.price_subtotal
            else:
                rec.sale_order_discount_estimated = (1 - float(str(rec.discount_code)[4:]) / 100) * rec.price_subtotal

    # def _compute_discount_total(self):
    #     for rec in self:
    #         rec.discount_temp = int(str(rec.discount_code)[4:]) / 100 * rec.price_subtotal
    #         rec.discount_total = rec.discount_total + rec.discount_temp
