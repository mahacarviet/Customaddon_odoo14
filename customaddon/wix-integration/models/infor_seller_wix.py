from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _
import requests
import json


class InforSellerWix(models.Model):
    _name = "infor.seller.wix"
    _description = "Seller"

    client_id = fields.Char(string='Client ID')
    client_secret = fields.Char(string='Client Secret')
    auth_code = fields.Char(string='Authorization Code')
    refresh_token = fields.Char(string='Refresh Token')
    access_token = fields.Char(string='Access Token')
    infor_permission = fields.Text(string='Information Permission')

    def request_an_access_token(self):
        try:
            current_seller = self.env['infor.seller.wix'].sudo().search([])

            for record_seller in current_seller:
                if record_seller.auth_code:
                    url = "https://www.wix.com/oauth/access"

                    payload = json.dumps({
                        "grant_type": "authorization_code",
                        "client_id": record_seller.client_id,
                        "client_secret": record_seller.client_secret,
                        "code": record_seller.auth_code
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("POST", url, headers=headers, data=payload)
                    result_response = response.json()
                    val = {}
                    if 'refresh token' in result_response and 'access token' in result_response:
                        val['refresh_token'] = result_response['refresh_token']
                        val['result_response'] = result_response['result_response']
                        existed_cancel_sendo = self.env['sendo.cancel.reason'].search(
                                    [('sendo_cancel_code', '=', result_response['code'])], limit=1)
                        if len(existed_cancel_sendo) < 1:
                            self.env['sendo.cancel.reason'].create(val)
                        else:
                            existed_cancel_sendo.write(val)
                    else:
                        raise ValidationError(result_response['payload']['message'])
                else:
                    raise ValidationError('Authorization Code is Unavailable')
        except Exception as e:
            raise ValidationError(str(e))

    def refresh_an_access_token(self):
        try:
            current_seller = self.env['infor.seller.wix'].sudo().search([])[0]

            for record_seller in current_seller:
                if record_seller.auth_code:
                    url = "https://www.wix.com/oauth/access"

                    payload = json.dumps({
                        "grant_type": "refresh_token",
                        "client_id": record_seller.client_id,
                        "client_secret": record_seller.client_secret,
                        "refresh_token": current_seller.refresh_token
                    })
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("POST", url, headers=headers, data=payload)
                    result_response = response.json()

                    if result_response['success']:
                        pass
                    else:
                        raise ValidationError(result_response['payload']['message'])

        except Exception as e:
            raise ValidationError(str(e))
