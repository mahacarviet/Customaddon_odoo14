import requests
import json
from datetime import *
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re


class WixProductVariants(models.Model):
    _name = "wix.product.variants"
    _description = "Wix Product Variants"

    variant_id = fields.Char(string='Variant ID')
    name = fields.Char(string='Product Name')
    visible = fields.Boolean(string='Visible Product')
    productType = fields.Char(string='Product Type')
    description = fields.Text(string='Description')
    sku = fields.Char(string='SKU')

    product_variant_product_id = fields.Many2one('wix.product', 'product_product_variant_id')