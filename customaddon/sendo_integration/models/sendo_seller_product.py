import requests
import json
from datetime import *
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re


class SendoSellerProduct(models.Model):
    _name = "sendo.seller.product"
    _description = "Sendo Product Queue"

    seller_product_id = fields.Char(string='Product ID')
    name = fields.Char(string='Product Name')

    #       Add To Module Sendo Integration
    def get_seller_product_sendo(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]

            url = "https://open.sendo.vn/api/partner/product/search/"

            payload = json.dumps({
                "page_size": 50,
                "product_name": "",
                "date_from": None,
                "date_to": None
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if "exp" in response.json():
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif response.json()["success"]:

                seller_products = response.json()
                list_products = seller_products["result"]["data"]

                val = {}
                for product in list_products:
                    if 'id' in product:
                        val['seller_product_id'] = product['id']
                        val['name'] = product['name']
                        existed_seller_product = self.env['sendo.seller.product'].search(
                            [('seller_product_id', '=', product['id'])], limit=1)
                        if len(existed_seller_product) < 1:
                            self.env['sendo.seller.product'].create(val)
                        else:
                            existed_seller_product.write(val)
            else:
                raise ValidationError(_('Sync List Product From Sendo Is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))

    #       Call API For Each Product
    def get_each_product_sendo_to_product_template(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]

            list_product_sendo = self.env['sendo.seller.product'].sudo().search([])

            for each_product_sendo in list_product_sendo:

                url = "https://open.sendo.vn/api/partner/product?id=" + each_product_sendo["seller_product_id"]

                payload = ""

                headers = {
                    'Authorization': 'Bearer ' + current_seller.token_connection
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                if "exp" in response.json():
                    raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
                elif response.json()["success"]:
                    seller_products = response.json()

                    product = seller_products["result"]

                    val = {}
                    if 'id' in product:
                        #   Link To Sendo Categories
                        existed_categories_product = self.env['product.category'].search(
                            [('sendo_cate_id', '=', int(product['cat_4_id']))], limit=1)
                        val['categ_id'] = int(existed_categories_product.id)
                        val['sendo_product_id'] = int(product['id'])
                        val['sendo_category_id'] = int(existed_categories_product.sendo_cate_id)
                        val['type'] = 'product'
                        val['name'] = product['name']
                        val['taxes_id'] = None
                        val['is_published'] = True
                        val['list_price'] = product['price']
                        val['default_code'] = product['sku']
                        val['sale_ok'] = True
                        val['purchase_ok'] = False
                        val['image_1920'] = base64.b64encode(urlopen(product["image"]).read())
                        val['weight'] = float(product['weight'] / 1000)
                        val['description'] = re.sub(r'<.*?>', '', product['description'])

                        #   Field Sendo Add To Core
                        val['sendo_height'] = float(product['height'])
                        val['sendo_length'] = float(product['length'])
                        val['sendo_width'] = float(product['width'])
                        val['sendo_unit_id'] = str(product['unit_id'])
                        val['sendo_url_avatar_image'] = product['image']
                        val['check_product_sendo'] = True

                        #   Check Sendo Product Stock Available
                        if product['stock_availability']:
                            val['sendo_stock_availability'] = True
                            val['sendo_stock_quantity'] = int(product['stock_quantity'])
                            # val['qty_available'] = float(product['stock_quantity'])
                        else:
                            val['sendo_stock_availability'] = False

                        #   Check Sendo Product Is Promotion
                        if product['is_promotion']:
                            val['sendo_is_promotion'] = True
                            val['sendo_special_price'] = float(product['special_price'])
                            if product['promotion_from_date_timestamp']:
                                val['sendo_promotion_from_date'] = date.fromtimestamp(
                                    int(product['promotion_from_date_timestamp']))
                            else:
                                val['sendo_promotion_from_date'] = date.today()
                            if product['promotion_to_date_timestamp']:
                                val['sendo_promotion_to_date'] = date.fromtimestamp(
                                    int(product['promotion_to_date_timestamp']))
                            else:
                                val['sendo_promotion_to_date'] = date.today() + timedelta(days=9000)
                        else:
                            val['sendo_is_promotion'] = False

                        # Search theo sendo id
                        existed_seller_product = self.env['product.template'].search(
                            [('sendo_product_id', '=', product['id'])], limit=1)

                        #   Check Product In Database
                        if len(existed_seller_product) < 1:
                            self.env['product.template'].create(val)
                        else:
                            # existed_seller_product.sudo().attribute_line_ids = False
                            existed_seller_product.write(val)
                else:
                    raise ValidationError(_('Sync Product From Sendo Is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))

    def get_variants_for_product_sendo(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]

            list_product_sendo = self.env['sendo.seller.product'].sudo().search([])

            for each_product_sendo in list_product_sendo:

                url = "https://open.sendo.vn/api/partner/product?id=" + each_product_sendo["seller_product_id"]

                payload = ""

                headers = {
                    'Authorization': 'Bearer ' + current_seller.token_connection
                }

                response = requests.request("GET", url, headers=headers, data=payload)

                if "exp" in response.json():
                    raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
                elif response.json()["success"]:
                    seller_products = response.json()

                    product = seller_products["result"]

                    val = {}
                    if 'id' in product:
                        # search theo sendo id
                        existed_seller_product = self.env['product.template'].search(
                            [('sendo_product_id', '=', product['id'])], limit=1)
                        if len(existed_seller_product) < 1:
                            pass
                        else:
                            #   Add Variant For Product
                            attrib_line_vals = []
                            if product['is_config_variant'] and product['attributes']:
                                attrib_line_vals = self.prepare_attribute_vals(product)
                            if len(attrib_line_vals) > 0:
                                val['attribute_line_ids'] = attrib_line_vals

                            existed_seller_product.sudo().attribute_line_ids = False
                            existed_seller_product.write(val)
                else:
                    raise ValidationError(_('Sync Product From Sendo Is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))

    def prepare_attribute_vals(self, result):
        product_attribute_obj = self.env['product.attribute']
        product_attribute_value_obj = self.env['product.attribute.value']
        attrib_line_vals = []
        if 'attributes' in result:
            for attrib in result.get('attributes'):
                attrib_name = attrib.get('attribute_name')
                attrib_values = attrib.get('attribute_values')
                attr_val_ids = []
                attribute = product_attribute_obj.search([('name', '=ilike', attrib_name)], limit=1)
                if not attribute:
                    attribute = product_attribute_obj.create({'name': attrib_name})
                for attrib_vals in attrib_values:
                    if attrib_vals.get('is_selected'):
                        value_name = attrib_vals.get('value')
                        attrib_value = attribute.value_ids.filtered(lambda x: x.name == value_name)
                        if attrib_value:
                            attr_val_ids.append(attrib_value[0].id)
                        else:
                            attrib_value = product_attribute_value_obj.with_context(active_id=False).create(
                                {'attribute_id': attribute.id, 'name': value_name})
                            attr_val_ids.append(attrib_value.id)
                if attr_val_ids:
                    attribute_line_ids_data = [0, 0,
                                               {'attribute_id': attribute.id, 'value_ids': [[6, 0, attr_val_ids]]}]
                    attrib_line_vals.append(attribute_line_ids_data)
        return attrib_line_vals
