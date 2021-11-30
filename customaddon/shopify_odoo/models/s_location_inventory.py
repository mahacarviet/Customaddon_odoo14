
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SLocationInventory(models.Model):
    _name = "s.location.inventory"
    _description = "s_location_inventory"
    _rec_name = "shopify_name"

    shopify_id = fields.Char()
    shopify_name = fields.Char()
    shopify_address1 = fields.Char()
    shopify_address2 = fields.Char()
    shopify_city = fields.Char()
    shopify_province = fields.Char()
    shopify_country_name = fields.Char()
