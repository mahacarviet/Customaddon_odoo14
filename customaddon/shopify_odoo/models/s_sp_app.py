# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import requests
from odoo.exceptions import UserError, ValidationError


class SSpApp(models.Model):
    _name = 's.sp.app'
    _description = 's_sp_app'
    _rec_name = 'web_user'

    shop_app_s_apps = fields.Many2one("s.app", string='App')
    shop_app_s_shops = fields.Many2one("s.shop", string='Shop')
    token_shop_app = fields.Char()
    web_user = fields.Char()
    password_user = fields.Char()

    def update_script_tag_shopify(self):
        try:
            #   Get list id script tag
            list_script_tag = []
            url_1 = "https://" + str(self.web_user) + "/admin/api/" + str(
                self.shop_app_s_apps.api_version) + "/script_tags.json"

            payload_1 = {}
            headers_1 = {
                'X-Shopify-Access-Token': self.token_shop_app
            }

            response_1 = requests.request("GET", url_1, headers=headers_1, data=payload_1)
            result_1 = response_1.json()
            if 'script_tags' in result_1:
                for script in result_1['script_tags']:
                    if 'id' in script:
                        list_script_tag.append(script['id'])

            #   Delete script tag
            count_script = len(list_script_tag)
            for i in range(count_script):
                url_2 = "https://" + str(
                    self.web_user) + "/admin/api/" + str(self.shop_app_s_apps.api_version) + "/script_tags/" + str(
                    list_script_tag[i]) + ".json"

                payload_2 = {}
                headers_2 = {
                    'X-Shopify-Access-Token': self.token_shop_app
                }

                response_2 = requests.request("DELETE", url_2, headers=headers_2, data=payload_2)
                result_2 = response_2.json()
                if 'error' in result_2:
                    raise ValidationError(result_2['error'])

            #   Create script tag
            url_3 = "https://" + str(self.web_user) + "/admin/api/" + str(
                self.shop_app_s_apps.api_version) + "/script_tags.json"

            payload_3 = json.dumps({
                "script_tag": {
                    "event": "onload",
                    "src": self.shop_app_s_apps.link_script_tag
                }
            })
            headers_3 = {
                'X-Shopify-Access-Token': self.token_shop_app,
                'Content-Type': 'application/json',
            }

            response_3 = requests.request("POST", url_3, headers=headers_3, data=payload_3)
            result_3 = response_3.json()
            if 'error' in result_3:
                raise ValidationError(result_3['error']['src'][0])
        except Exception as e:
            raise ValidationError(str(e))
