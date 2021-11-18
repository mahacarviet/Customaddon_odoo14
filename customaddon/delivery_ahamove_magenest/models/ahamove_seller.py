import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class RegisterAccountAhamove(models.Model):
    _name = "register.account.move"
    _rec_name = 'name'

    mobile = fields.Char(string='Mobile', limit=1)
    name = fields.Char(string='App Name', limit=1)
    api_key = fields.Char(string='My API Key', limit=1)
    address = fields.Char(string='Shop Address', limit=1)

    def action_view_config(self):
        res_id = self.env['register.account.move'].sudo().search([('mobile', '!=', False)])
        return {
            'name': _('Config Connection AhaMove API'),
            'view_mode': 'form',
            'view_id': self.env.ref('delivery_ahamove_magenest.ahamove_seller_form_view').id,
            'res_model': 'register.account.move',
            'context': "{'create': False}",
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id.id if res_id else False,
        }

    def register_account_ahamove(self):
        try:
            url_1 = "https://apistg.ahamove.com/v1/partner/register_account?mobile=" + str(self.mobile) + "&name="
            url_2 = str(self.name) + "&api_key=" + str(self.api_key) + "&address=" + str(self.address)
            url = str(url_1) + str(url_2)

            payload = {}
            headers = {
                'cache-control': 'no-cache'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            content = response.json()
            if 'token' in content:
                search_shipping = self.env['delivery.carrier'].sudo().search([('delivery_type', '=', 'aha_move')])
                if search_shipping:
                    for ahamove_shipping in search_shipping:
                        ahamove_shipping.write(
                            {'aha_token': content['token'], 'aha_refresh_token': content['refresh_token']})
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
