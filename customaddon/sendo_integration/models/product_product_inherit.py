from odoo import fields, models, api, _


class ProductProductInheritSendo(models.Model):
    _inherit = "product.product"

    sendo_product_id = fields.Integer(related='product_tmpl_id.sendo_product_id')
    sendo_category_id = fields.Integer(related='product_tmpl_id.sendo_category_id')
    sendo_stock_availability = fields.Boolean(string='Stock Availability',
                                              related='product_tmpl_id.sendo_stock_availability')
    sendo_height = fields.Float(string='Height', related='product_tmpl_id.sendo_height')
    sendo_length = fields.Float(string='Length', related='product_tmpl_id.sendo_length')
    sendo_width = fields.Float(string='Width', related='product_tmpl_id.sendo_width')
    sendo_unit_id = fields.Selection([
        ('1', 'Cái'),
        ('2', 'Bộ'),
        ('3', 'Chiếc'),
        ('4', 'Đôi'),
        ('5', 'Hộp'),
        ('6', 'Cuốn'),
        ('7', 'Chai'),
        ('8', 'Thùng')], string='Unit Product', related='product_tmpl_id.sendo_unit_id')
    sendo_stock_quantity = fields.Integer(string='Stock Quantity', related='product_tmpl_id.sendo_stock_quantity')
    sendo_promotion_from_date = fields.Date(string='Promotion From Date',
                                            related='product_tmpl_id.sendo_promotion_from_date')
    sendo_promotion_to_date = fields.Date(string='Promotion To Date', related='product_tmpl_id.sendo_promotion_to_date')
    sendo_is_promotion = fields.Boolean(string='Promotion', related='product_tmpl_id.sendo_is_promotion')
    sendo_special_price = fields.Float(string='Special Price', related='product_tmpl_id.sendo_special_price')
    check_product_sendo = fields.Boolean(related='product_tmpl_id.check_product_sendo')
