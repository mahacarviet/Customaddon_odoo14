import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SendoSeller(models.Model):
    _name = "sendo.seller"
    _description = "Seller"
    _rec_name = 'shop_key'

    shop_key = fields.Char(string='My Shop Key', limit=1)
    secret_key = fields.Char(string='My Secret Key', limit=1)
    token_connection = fields.Char(string='My Token', limit=1)
    date_startup = fields.Date(string='Date Startup', limit=1)
    sendo_order_date_from = fields.Date(string='Order Date From', limit=1)
    sendo_order_date_to = fields.Date(string='Order Date To', limit=1)

    def action_view_config(self):
        res_id = self.env['sendo.seller'].sudo().search([('shop_key', '!=', False)])
        return {
            'name': _('Config connection Sendo API'),
            'view_mode': 'form',
            'view_id': self.env.ref('sendo_integration.sendo_seller_form_view').id,
            'res_model': 'sendo.seller',
            'context': "{'create': False}",
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id.id if res_id else False,
        }

    def test_connect(self):
        try:
            url = "https://open.sendo.vn/login"
            payload = json.dumps({
                "shop_key": self.shop_key,
                "secret_key": self.secret_key
            })
            headers = {
                'Content-Type': 'application/json',
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.json()["success"]:
                token_connection = response.json()["result"]["token"]
                val = {
                    'shop_key': self.shop_key,
                    "secret_key": self.secret_key,
                    'token_connection': token_connection,
                    'date_startup': self.date_startup
                }
                existed_secret = self.env['sendo.seller'].search([('secret_key', '=', self.secret_key)], limit=1)
                if len(existed_secret) < 1:
                    self.env['sendo.seller'].create(val)
                else:
                    existed_secret.write(val)
            else:
                raise ValidationError(_('My Shop Key or Secret Key is wrong.'))
        except Exception as e:
            print(e)
