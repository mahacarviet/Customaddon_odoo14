# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime
from time import *
from odoo.exceptions import UserError, ValidationError
import requests
import json


class SDiscount(models.Model):
    _name = 's.discount'
    _description = 's_discount'
    _rec_name = 'discount_name'

    discount_name = fields.Char()
    decrease_price = fields.Monetary(default=0.0)
    valid_date_from = fields.Date(default=date.today())
    valid_date_to = fields.Date()
    shop_user_id = fields.Integer()

    res_partner_discount_shopify = fields.Many2many('res.partner', string='Customers')
    product_discount_shopify = fields.Many2many('product.template', string='Products')
    currency_id = fields.Many2one('res.currency', string='Currency')

    @api.onchange('shop_user_id')
    def _add_shop_user_id(self):
        for rec in self:
            rec.shop_user_id = self.env.uid

    @api.onchange('valid_date_to')
    def check_valid_date_to(self):
        for rec in self:
            if rec.valid_date_to:
                if rec.valid_date_to < rec.valid_date_from:
                    raise ValidationError('Valid Date From Must Start Earlier Valid Date To. ')

    def get_customer_shopify(self):
        try:
            # current_id = self.env.uid
            current_id = 8
            search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version

            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/customers.json"

            payload = {}
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
                'limit': '50'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()

            if 'customers' in result:
                list_customer = []
                for person in result['customers']:
                    search_customer = self.env['res.partner'].sudo().search([("shopify_customer_id", "=", person['id'])],
                                                                            limit=1)
                    if search_customer:
                        list_customer.append(search_customer.id)
                self.res_partner_discount_shopify = [(6, 0, list_customer)]
                print(list_customer)
        except Exception as e:
            raise ValidationError(str(e))

    def get_product_shopify(self):
        try:
            # current_id = self.env.uid
            current_id = 8
            search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version

            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/products.json"

            payload = {}
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()

            if 'products' in result:
                list_product = []
                for product in result['products']:
                    search_product = self.env['product.template'].sudo().search(
                        [("shopify_product_id", "=", product['variants'][0]['id'])], order='id DESC', limit=50)
                    if search_product:
                        for discount_product in search_product:
                            list_product.append(discount_product.id)
                self.product_discount_shopify = [(6, 0, list_product)]
                print(list_product)
        except Exception as e:
            raise ValidationError(str(e))

# class ShopifyDiscountLine(models.Model):
#     _name = 'shopify.discount.line'
#
#     s_product_id = fields.Many2one('product.template', string='Product')
