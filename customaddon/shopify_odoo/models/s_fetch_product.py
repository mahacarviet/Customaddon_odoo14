# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json
from datetime import datetime


class SFetchProduct(models.Model):
    _name = 's.fetch.product'
    _description = 's_fetch_product'
    _rec_name = 's_shop_s_fetch_product'

    date_time_update = fields.Date()
    shop_user_id = fields.Integer()

    s_shop_s_fetch_product = fields.Many2one('s.shop', string='Shop')
    s_fetch_product_log_shopify = fields.One2many('s.fetch.product.log', 's_fetch_log_shopify_id',
                                                  string='Log Product Shopify')

    @api.onchange('shop_user_id')
    def _add_shop_user_id(self):
        # self.shop_user_id = self.env.uid
        self.shop_user_id = 16
        search_user = self.env['res.users'].search([('id', '=', self.shop_user_id)], limit=1)
        search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)], limit=1)
        self.s_shop_s_fetch_product = search_shop.id

    def fetch_product_shopify(self):
        try:
            # current_id = self.env.uid
            current_id = 16
            search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)], limit=1)
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)], limit=1)
            api_version = search_shop.shop_app_ids[0].api_version

            if self.s_fetch_product_log_shopify:
                for product in self.s_fetch_product_log_shopify:
                    url = "https://" + str(search_user.login) + "/admin/api/" + str(
                        api_version) + "/inventory_levels/set.json"

                    payload = json.dumps({
                        "location_id": product.s_location_shopify_id.shopify_id,
                        "inventory_item_id": product.product_shopify_ids.shopify_inventory_item_id,
                        "available": product.inventory_quantity
                    })
                    headers = {
                        'X-Shopify-Access-Token': search_token.token_shop_app,
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("POST", url, headers=headers, data=payload)
                    if response.status_code == 200:
                        print('Success!')
                    elif response.status_code == 404:
                        raise ValidationError('Something Wrong When You Update Inventory Product Shopify.')
                    result = response.json()
                    print(result)

        except Exception as e:
            raise ValidationError(str(e))


class SFetchProductLog(models.Model):
    _name = 's.fetch.product.log'
    _description = 's_fetch_product_log'

    s_fetch_log_shopify_id = fields.Many2one('s.fetch.product')
    product_shopify_ids = fields.Many2one('product.template', string='Product',
                                          domain="[('shopify_product_id', '!=', False)]")
    inventory_quantity = fields.Integer(string='Quantity')

    s_location_shopify_id = fields.Many2one('s.location.inventory', string='Location ID')
