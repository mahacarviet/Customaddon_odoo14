import requests
import json
from datetime import *
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from urllib.request import urlopen
import base64
import re


class InforBusinessWix(models.Model):
    _name = "infor.business.wix"
    _description = "Wix Business Information"

    primary = fields.Char(string='Properties Categories')
    language = fields.Char()
    paymentCurrency = fields.Char(string='Payment Currency')
    email = fields.Char()
    phone = fields.Char()
    fax = fields.Char()
    businessName = fields.Char(string='Business Name')
    description = fields.Char()
    googleFormattedAddress = fields.Char(string='Google Formatted Address')

    def get_list_product_wix(self):
        try:
            current_app = self.env['infor.seller.wix'].sudo().search([])[0]
            if current_app.auth_code:
                url = "https://www.wixapis.com/site-properties/v4/properties"

                payload = {}
                headers = {
                    'Authorization': current_app.access_token
                }

                response = requests.request("GET", url, headers=headers, data=payload)
                result_response = response.json()
                if 'siteDisplayName' in result_response:
                    val = {
                        'primary': result_response['properties']['categories']['primary'],
                        "language": result_response['properties']['language'],
                        'paymentCurrency': result_response['properties']['paymentCurrency'],
                        'email': result_response['properties']['email'],
                        'phone': result_response['properties']['phone'],
                        'fax': result_response['properties']['fax'],
                        'businessName': result_response['properties']['businessName'],
                        'description': result_response['properties']['description'],
                        'googleFormattedAddress': result_response['address']['googleFormattedAddress']
                    }
                    existed_infor_business = self.env['infor.business.wix'].search(
                        [('businessName', '=', result_response['businessName'])], limit=1)
                    if len(existed_infor_business) < 1:
                        self.env['infor.business.wix'].create(val)
                    else:
                        existed_infor_business.write(val)
                else:
                    raise ValidationError(result_response['message'])
            else:
                raise ValidationError('Access Token is Invalid or Expired')
        except Exception as e:
            raise ValidationError(str(e))
