from odoo import fields, models, api, _
import requests
import json
from odoo.exceptions import UserError, ValidationError


#       Class Product Category
class WoocommerceCategory(models.Model):
    _name = "woocommerce.category"
    _rec_name = "woocommerce_name"

    woocommerce_cate_id = fields.Integer(string='Category ID')
    woocommerce_name = fields.Char(string='Category Name')
    woocommerce_slug = fields.Char(string='Category Slug')
    woocommerce_parent_id = fields.Char(string='Woocommerce Parent ID')
    woocommerce_count = fields.Integer(string='Count All Product')

    woocommerce_product_template = fields.Many2many('product.template', string='Woocommerce Category')

    #       Add To Module Sale
    def get_categories_woocommerce(self):
        try:
            current_seller = self.env['woocommerce.seller'].sudo().search([])[0]

            url = str(current_seller.link_website) + "wp-json/wc/v3/products/categories?consumer_key=" + str(
                current_seller.consumer_key) + "&consumer_secret=" + str(current_seller.consumer_secret)

            payload = {}
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            result_category = response.json()
            val = {}
            if result_category:
                for cate in result_category:
                    if cate['id']:
                        val['woocommerce_cate_id'] = cate['id']
                        val['woocommerce_name'] = cate['name'].replace('amp;', '')
                        val['woocommerce_slug'] = cate['slug']
                        val['woocommerce_parent_id'] = cate['parent']
                        val['woocommerce_count'] = cate['count']

                        existed_category = self.env['woocommerce.category'].search(
                            [('woocommerce_cate_id', '=', cate['id'])], limit=1)
                        if len(existed_category) < 1:
                            self.env['woocommerce.category'].create(val)
                        else:
                            existed_category.write(val)
                    else:
                        pass
            else:
                raise ValidationError(_('Sync Category From Woocommerce Is Fail.'))
        except Exception as e:
            raise ValidationError(str(e))
