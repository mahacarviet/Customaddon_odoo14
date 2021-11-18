from odoo import api, fields, models, _

class ShopifyXeroSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    shopify_api_key = fields.Char('Shopify API Key', config_parameter='shopify_xero.shopify_api_key')
    shopify_shared_secret = fields.Char('Shopify Shared Secret', config_parameter='shopify_xero.shopify_shared_secret')
    shopify_api_version = fields.Char('Shopify API Version', config_parameter='shopify_xero.shopify_api_version')
    xero_client_id = fields.Char('Xero Client ID', config_parameter='shopify_xero.xero_client_id')
    xero_client_secret = fields.Char('Xero Client Secret', config_parameter='shopify_xero.xero_client_secret')