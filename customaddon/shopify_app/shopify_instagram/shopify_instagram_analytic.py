from odoo import models, fields, api
import logging
import traceback
_logger = logging.getLogger(__name__)


class InstagramAddToCart(models.Model):
    _name = 'instagram.add.to.cart'

    shop = fields.Many2one('shopify.instagram.shop', string='Shop', index=True, ondelete='cascade')
    media = fields.Many2one('instagram.media', string='Media', index=True)
    product_name = fields.Char('Product Name')
    product_url = fields.Char('Product URL')
    ip_user = fields.Char('IP user')
    date = fields.Date('Date', index=True)
    datetime = fields.Datetime('DateTime')
    hour = fields.Integer('Hour')


