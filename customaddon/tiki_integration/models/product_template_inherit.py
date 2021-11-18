import requests
import json
from datetime import *
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re


class ProductTemplateInheritSendo(models.Model):
    _inherit = "product.template"

    tiki_product_id = fields.Integer()
    tiki_category_id = fields.Integer()
    tiki_sku = fields.Char()
    tiki_type = fields.Char()
    tiki_iventory_type = fields.Selection([
        ('backorder', 'Backorder'),
        ('instock', 'Instock'),
        ('virtual', 'Virtual')], default='instock')
    tiki_status = fields.Selection([
        ('1', 'Enabled'),
        ('2', 'Disabled')], default='1')
    tiki_inventory_quantity = fields.Integer()
    tiki_inventory_qty = fields.Integer()
    tiki_inventory_qty_available = fields.Integer()
    tiki_fulfillment_type = fields.Char()

    # Add product from Tiki to Module Core
    def get_seller_product_tiki(self):
        current_seller = self.env['tiki.seller'].sudo().search([])[0]
        # cate = self.env['tiki.categories'].search(['is_primary', '=', True])
        try:
            url = "https://api-sellercenter.tiki.vn/integration/seller/products"
            payload = {}
            headers = {
                'tiki-api': current_seller.secret,
                'User-Agent': current_seller.user_agent,
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            seller_products = response.json()
            list_products = seller_products['data']
            val = {}

            for product in list_products:
                if 'id' in product:
                    #   Link To Sendo Categories
                    for cate in product['categories']:
                        if cate['is_primary'] == 1:
                            category_tiki = cate['id']
                            existed_categories_product = self.env['product.category'].search(
                                [('tiki_cate_id', '=', int(category_tiki))], limit=1)
                            val['categ_id'] = int(existed_categories_product.id)
                            val['tiki_product_id'] = product['id']
                            val['name'] = product['name']
                            val['tiki_category_id'] = int(category_tiki)
                            val['tiki_status'] = str(product['status'])
                            val['tiki_sku'] = str(product['sku'])
                            val['tiki_type'] = product['type']
                            val['default_code'] = product['seller_product_code']
                            val['taxes_id'] = None
                            val['is_published'] = True
                            val['sale_ok'] = True
                            val['purchase_ok'] = False
                            val['image_1920'] = base64.b64encode(urlopen(product["thumbnail"]).read())
                            val['list_price'] = product['list_price']
                            val['standard_price'] = product['price']
                            val['tiki_iventory_type'] = str(product['inventory']['type'])
                            val['tiki_inventory_quantity'] = product['inventory']['quantity']
                            val['tiki_inventory_qty'] = product['inventory']['qty']
                            val['tiki_inventory_qty_available'] = product['inventory']['qty_available'] or 0
                            val['tiki_fulfillment_type'] = product['inventory']['fulfillment_type']
                            existed_seller_product = self.env['product.template'].search(
                                [('tiki_product_id', '=', product['id'])], limit=1)
                            if len(existed_seller_product) < 1:
                                self.env['product.template'].create(val)
                            else:
                                existed_seller_product.write(val)
        except Exception as e:
            print(e)
