import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class AhamoveListServices(models.Model):
    _name = "ahamove.list.services"
    _rec_name = 'name'

    mobile = fields.Char(string='Mobile', limit=1)
    name = fields.Char(string='App Name', limit=1)
    api_key = fields.Char(string='My API Key', limit=1)
    address = fields.Char(string='Shop Address', limit=1)

    def get_list_services(self):
        try:
            # url = "https://apistg.ahamove.com/v1/order/service_types?city_id=" + ma thanh pho
            url = "https://apistg.ahamove.com/v1/order/service_types?city_id=SGN"

            payload = {}
            headers = {
                'cache-control': 'no-cache'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            content = response.json()
            if not 'code' in content:
                pass
            else:
                if ('description' in content) and ('title' in content):
                    raise_error = str(content['title']) + "/" + str(content['title'])
                    raise ValidationError(raise_error)
                if 'description' in content:
                    raise ValidationError(content['description'])
                if 'title' in content:
                    raise ValidationError(content['title'])
        except Exception as e:
            raise ValidationError(str(e))
