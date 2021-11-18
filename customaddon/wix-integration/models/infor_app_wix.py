import requests
import json
from datetime import *
from odoo import fields, models, api
from urllib.request import urlopen
import base64
import re
from odoo.exceptions import UserError, ValidationError


class WixProduct(models.Model):
    _name = "infor.app.wix"
    _description = "Information App Wix"

    instance_id = fields.Char(string='instance ID')
    app_name = fields.Char(string='App Name')
    app_version = fields.Char(string='App Version')
    is_free = fields.Boolean(string='App Is Free')
    package_name = fields.Char(string='Package Name')
    billing_cycle = fields.Char(string='Billing Cycle')
    site_display_name = fields.Char(string='Site Display Name')
    locale = fields.Char(string='Locale')
    payment_currency = fields.Char(string='Payment Currency')
    url_website = fields.Char(string='Url Website')

    def get_infor_app(self):
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

                if 'instance' in result_response:
                    if result_response['instance']['isFree'] == 'true':
                        val = {
                            'instance_id': result_response['instance']['instanceId'],
                            "app_name": result_response['instance']['appName'],
                            'app_version': result_response['instance']['appVersion'],
                            'is_free': True,
                            'package_name': None,
                            'billing_cycle': None,
                            'site_display_name': result_response['site']['siteDisplayName'],
                            'locale': result_response['site']['locale'],
                            'payment_currency': result_response['site']['paymentCurrency'],
                            'url_website': result_response['site']['url']
                        }
                        existed_app = self.env['infor.app.wix'].search(limit=1)
                        if len(existed_app) < 1:
                            self.env['infor.app.wix'].create(val)
                        else:
                            existed_app.write(val)
                    else:
                        val = {
                            'instance_id': result_response['instance']['instanceId'],
                            "app_name": result_response['instance']['appName'],
                            'app_version': result_response['instance']['appVersion'],
                            'is_free': False,
                            'package_name': result_response['instance']['billing']['billingCycle'],
                            'billing_cycle': result_response['instance']['billing']['packageName'],
                            'site_display_name': result_response['site']['siteDisplayName'],
                            'locale': result_response['site']['locale'],
                            'payment_currency': result_response['site']['paymentCurrency'],
                            'url_website': result_response['site']['url']
                        }
                        existed_app = self.env['infor.app.wix'].search(limit=1)
                        if len(existed_app) < 1:
                            self.env['infor.app.wix'].create(val)
                        else:
                            existed_app.write(val)
                else:
                    raise ValidationError(result_response['message'])
            else:
                raise ValidationError('Access Token is Invalid or Expired')

        except Exception as e:
            raise ValidationError(str(e))
