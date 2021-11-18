from odoo import fields, models, api


class ShowWarrantyProductWebsiteInherit(models.Model):
    _inherit = 'website'

    product_ids = fields.Many2many("product.template", string="Product Template")

    product_warranty = fields.Char(related="product_ids.product_warranty", string="Product Warranty", store=True)
    date_from = fields.Date(related="product_ids.date_from", string="Warranty From")
    date_to = fields.Date(related="product_ids.date_to", string="Warranty To")
    check_product_warranty = fields.Boolean(related="product_ids.check_product_warranty")
    check_product_time = fields.Boolean(related="product_ids.check_product_time", store=True)
    day_warranty = fields.Integer(related="product_ids.day_warranty", string="Day Warranty")