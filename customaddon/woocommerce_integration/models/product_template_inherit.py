import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re
from woocommerce import API


class ProductTemplateInheritWoo(models.Model):
    _inherit = "product.template"

    woo_product_id = fields.Char(string='Product ID', store=True)
    woo_date_created = fields.Char('Created at')
    woo_date_modified = fields.Char('Updated at')
    check_product_woo = fields.Boolean()

    product_category_woocommerce = fields.Many2many('woocommerce.category', 'woocommerce_product_template',
                                                    string='Woocommerce Category')

    def get_product_woocommerce(self):
        try:
            current_seller = self.env['woocommerce.seller'].sudo().search([])[0]

            url = str(current_seller.link_website) + "wp-json/wc/v3/products?consumer_key=" + str(
                current_seller.consumer_key) + "&consumer_secret=" + str(current_seller.consumer_secret)

            payload = {}
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            list_products = response.json()

            for data in list_products:
                if 'id' in data:
                    vals = {
                        'woo_product_id': data['id'],
                        'default_code': data['sku'],
                        'name': data['name'],
                        'sale_ok': data['on_sale'],
                        'purchase_ok': data['purchasable'],
                        'type': 'product',
                        'taxes_id': None,
                        'is_published': True,
                        'categ_id': 1,
                        'woo_date_created': data['date_created'],
                        'woo_date_modified': data['date_modified'],
                        'list_price': data['price'],
                        'check_product_woo': True,
                        'weight': data['weight'],
                        'description': re.sub(r'<.*?>', '', data['description']),
                        'image_1920': base64.b64encode(urlopen(data["images"][0]["src"]).read()),
                    }

                    existed_product = self.env['product.template'].search(
                        [('woo_product_id', '=', data['id'])], limit=1)
                    if len(existed_product) < 1:
                        self.env['product.template'].create(vals)
                    else:
                        existed_product.write(vals)
                else:
                    raise ValidationError(_('Sync Category From Woocommerce Is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))

    def get_product_woocommerce_category_attribute(self):
        try:
            current_seller = self.env['woocommerce.seller'].sudo().search([])[0]

            url = str(current_seller.link_website) + "wp-json/wc/v3/products?consumer_key=" + str(
                current_seller.consumer_key) + "&consumer_secret=" + str(current_seller.consumer_secret)

            payload = {}
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            list_products = response.json()
            val = {}

            for data in list_products:
                if 'id' in data:
                    existed_product = self.env['product.template'].search(
                        [('woo_product_id', '=', data['id'])], limit=1)
                    if len(existed_product) < 1:
                        pass
                    else:
                        category = data["categories"]
                        #   Add Woocommerce Category
                        for cate in category:
                            existed_categories_product = self.env['woocommerce.category'].search(
                                [('woocommerce_cate_id', '=', int(cate["id"]))], limit=1)
                            existed_product.product_category_woocommerce = [(4, existed_categories_product.id)]

                        #   Add Variant For Product
                        attrib_line_vals = []
                        if data["attributes"]:
                            attrib_line_vals = self.prepare_attribute_vals(data)
                        if len(attrib_line_vals) > 0:
                            val['attribute_line_ids'] = attrib_line_vals
                            existed_product.sudo().attribute_line_ids = False
                            existed_product.write(val)
                else:
                    raise ValidationError(_('Sync Category From Woocommerce Is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))

    def prepare_attribute_vals(self, result):
        product_attribute_obj = self.env['product.attribute']
        product_attribute_value_obj = self.env['product.attribute.value']
        attrib_line_vals = []
        if 'attributes' in result:
            for attrib in result.get('attributes'):
                attrib_name = attrib.get('name')
                attrib_values = attrib.get('options')[0]
                attr_val_ids = []
                attribute = product_attribute_obj.search([('name', '=ilike', attrib_name)], limit=1)
                if not attribute:
                    attribute = product_attribute_obj.create({'name': attrib_name})
                attrib_value = attribute.value_ids.filtered(lambda x: x.name == attrib_values)
                if attrib_value:
                    attr_val_ids.append(attrib_value[0].id)
                else:
                    attrib_value = product_attribute_value_obj.with_context(active_id=False).create(
                        {'attribute_id': attribute.id, 'name': attrib_values})
                    attr_val_ids.append(attrib_value.id)
                if attr_val_ids:
                    attribute_line_ids_data = [0, 0,
                                               {'attribute_id': attribute.id, 'value_ids': [[6, 0, attr_val_ids]]}]
                    attrib_line_vals.append(attribute_line_ids_data)
        return attrib_line_vals

    def update_stock_product_woocommerce(self):
        try:
            current_seller = self.env['woocommerce.seller'].sudo().search([])[0]
            product = "products/" + self.woo_product_id
            data = {
                "manage_stock": True if int(self.qty_available) > 0 else False,
                "stock_quantity": int(self.qty_available)
            }

            wcapi = API(
                url=str(current_seller.link_website),
                consumer_key=str(current_seller.consumer_key),
                consumer_secret=str(current_seller.consumer_secret),
                wp_api=True,
                version="wc/v3",
                query_string_auth=True  # Force Basic Authentication as query string true and using under HTTPS
            )

            result = wcapi.put(product, data).json()

            if not "id" in result:
                raise ValidationError(_('Update Stock Available Product Woocommerce is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))
