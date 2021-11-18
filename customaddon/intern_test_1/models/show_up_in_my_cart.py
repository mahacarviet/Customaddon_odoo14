from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = 'website'

    # discount_price = fields.Float(compute="_get_discount_price_api")
    discount_price_total = fields.Float(compute="_get_discount_price_total_api")

    # @api.depends()
    # def get_discount_price(self):
    #     for rec in self:
    #         if rec.sale_get_order().partner_id.customer_discount_code:
    #             rec.discount_price = (1 - float(str(rec.customer_discount_code)[4:]) / 100) * rec.product.list_price
    #             return rec.discount_price
    #         else:
    #             rec.discount_price = rec.product.list_price
    #             return rec.discount_price

    @api.depends('partner_id.customer_discount_code')
    def get_discount_price_total(self):
        for rec in self:
            if rec.partner_id.customer_discount_code:
                rec.discount_price_total = (1 - float(
                    str(rec.customer_discount_code)[4:]) / 100) * rec.amount_total
                # return rec.discount_price_total
            else:
                rec.discount_price_total = rec.website_sale_order.amount_total
                # return rec.discount_price_total
