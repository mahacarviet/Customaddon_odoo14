# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json

link_ngrok = "https://7525-27-72-103-14.ngrok.io"


class CreateWebhookShopify(models.Model):
    _name = 'create.webhook.shopify'
    _rec_name = 'webhook_name'

    webhook_name = fields.Char()
    webhook_id = fields.Char()

    def create_product_shopify(self, shop_id):
        try:
            # current_id = self.env.uid
            # current_id = 8
            search_user = self.env['res.users'].search([('id', '=', shop_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)], limit=1)
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version

            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/webhooks.json"

            payload = json.dumps({
                "webhook": {
                    "topic": "products/create",
                    "address": str(link_ngrok) + "/shopify/" + str(shop_id) + "/products/create",
                    "format": "json",
                    "fields": []
                }
            })
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            result = response.json()

            if 'errors' in result:
                raise ValidationError(result['errors'])
            else:
                self.env['create.webhook.shopify'].sudo().create(
                    {'webhook_name': result['webhook']['topic'], 'webhook_id': result['webhook']['id']})
        except Exception as e:
            raise ValidationError(str(e))

    def create_order_shopify(self, shop_id):
        try:
            # current_id = self.env.uid
            # current_id = 8
            search_user = self.env['res.users'].search([('id', '=', shop_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version

            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/webhooks.json"

            payload = json.dumps({
                "webhook": {
                    "topic": "orders/create",
                    "address": str(link_ngrok) + "/shopify/" + str(shop_id) + "/orders/create",
                    "format": "json",
                    "fields": []
                }
            })
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            result = response.json()

            if 'errors' in result:
                raise ValidationError(result['errors'])
            else:
                self.env['create.webhook.shopify'].sudo().create(
                    {'webhook_name': result['webhook']['topic'], 'webhook_id': result['webhook']['id']})
        except Exception as e:
            raise ValidationError(str(e))

    def update_product_shopify(self, shop_id):
        try:
            # current_id = self.env.uid
            # current_id = 8
            search_user = self.env['res.users'].search([('id', '=', shop_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version

            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/webhooks.json"

            payload = json.dumps({
                "webhook": {
                    "topic": "products/update",
                    "address": str(link_ngrok) + "/shopify/" + str(shop_id) + "/products/update",
                    "format": "json",
                    "fields": []
                }
            })
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            result = response.json()

            if 'errors' in result:
                raise ValidationError(result['errors'])
            else:
                self.env['create.webhook.shopify'].sudo().create(
                    {'webhook_name': result['webhook']['topic'], 'webhook_id': result['webhook']['id']})
        except Exception as e:
            raise ValidationError(str(e))

    def update_order_shopify(self, shop_id):
        try:
            # current_id = self.env.uid
            # current_id = 8
            search_user = self.env['res.users'].search([('id', '=', shop_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version

            url = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/webhooks.json"

            payload = json.dumps({
                "webhook": {
                    "topic": "orders/updated",
                    "address": str(link_ngrok) + "/shopify/" + str(shop_id) + "/orders/updated",
                    "format": "json",
                    "fields": []
                }
            })
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app,
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            result = response.json()

            if 'errors' in result:
                raise ValidationError(result['errors'])
            else:
                self.env['create.webhook.shopify'].sudo().create(
                    {'webhook_name': result['webhook']['topic'], 'webhook_id': result['webhook']['id']})
        except Exception as e:
            raise ValidationError(str(e))
