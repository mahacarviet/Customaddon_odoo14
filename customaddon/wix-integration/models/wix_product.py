import requests
import json
from datetime import *
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re


class WixProduct(models.Model):
    _name = "wix.product"
    _description = "Wix Products"

    product_id = fields.Char(string='Product ID')
    name = fields.Char(string='Product Name')
    visible = fields.Boolean(string='Visible Product')
    productType = fields.Char(string='Product Type')
    description = fields.Text(string='Description')
    sku = fields.Char(string='SKU')
    weight = fields.Float(string='Weight')
    trackInventory = fields.Boolean(string='Track Inventory')
    quantity = fields.Integer()
    inStock = fields.Boolean(string='Product in Stock')
    currency = fields.Char()
    price = fields.Float(string='Product Price')
    discountedPrice = fields.Float(string='Discounted Product Price')
    image = fields.Binary()
    productOptions = fields.Boolean(string='Manage Variants')
    inventoryItemId = fields.Char(string='Inventory Item ID')
    ribbon = fields.Char()
    brand = fields.Char()
    attribute_value = fields.Char()

    product_product_variant_id = fields.One2many('wix.product.variants', 'product_variant_product_id')

    def get_list_product_wix(self):
        try:
            current_app = self.env['infor.seller.wix'].sudo().search([])[0]
            if current_app.auth_code:
                url = "https://www.wixapis.com/apps/v1/instance"

                payload = {}
                headers = {
                    'Authorization': current_app.access_token
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                result_response = response.json()

                for record_product in result_response:
                    if 'id' in record_product:
                        val = {
                            'product_id': record_product['id'],
                            "name": record_product['instance'],
                            'visible': record_product['visible'].capitalize(),
                            'productType': record_product['productType'],
                            'description': re.sub(r'<.*?>', '', record_product['description']),
                            'sku': record_product['sku'] if 'sku' in record_product else None,
                            'weight': float(record_product['weight']),
                            'trackInventory': record_product['stock']['trackInventory'].capitalize(),
                            'quantity': int(record_product['stock']['quantity']),
                            'inStock': record_product['stock']['inStock'].capitalize(),
                            'currency': record_product['priceData']['currency'],
                            'price': record_product['priceData']['price'],
                            'discountedPrice': record_product['priceData']['discountedPrice'],
                            'productOptions': True if record_product['productOptions'].capitalize() else False,
                            'attribute_value': record_product['productOptions'],
                            'inventoryItemId': record_product['inventoryItemId'],
                            'ribbon': record_product['ribbon'],
                            'brand': record_product['brand'],
                            'image': base64.b64encode(urlopen(record_product['media']['mainMedia']["image"]['url']).read())
                        }
                        existed_product = self.env['wix.product'].search([('product_id', '=', record_product['id'])], limit=1)
                        if len(existed_product) < 1:
                            self.env['wix.product'].create(val)
                        else:
                            existed_product.write(val)

                            # Function Get Product Variant
                    else:
                        raise ValidationError(result_response['message'])
            else:
                raise ValidationError('No Information To Sync Data From Wix To Odoo')
        except Exception as e:
            raise ValidationError(str(e))

