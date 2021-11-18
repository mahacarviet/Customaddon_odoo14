from odoo import api, fields, models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    ghn_shop_id = fields.Char('GHN shop_id', help='shop_id giúp quản lý nhiều cửa hàng trên GHN')
