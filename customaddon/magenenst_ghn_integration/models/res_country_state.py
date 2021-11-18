from odoo import api, fields, models, _
import requests
import json
from odoo.exceptions import UserError, ValidationError


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    ghn_province_id = fields.Integer(string="GHN mã tỉnh/TP", help='Mã tỉnh/TP theo Giao hàng Nhanh')

    def fetch_all_province_id(self):
        try:
            request_url = "https://online-gateway.ghn.vn/shiip/public-api/master-data/province"
            ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
            headers = {
                'Content-type': 'application/json',
                'Token': ghn_token
            }
            req = requests.get(request_url, headers=headers)
            # req.raise_for_status()
            content = req.json()
            data = content['data']
            if content['code'] == 200:
                for rec in data:
                    existed_state = self.env['res.country.state'].sudo().search([('name', 'ilike', rec['ProvinceName'])])
                    if existed_state:
                        for ex in existed_state:
                            ex.sudo().write({'ghn_province_id': rec['ProvinceID']})
            else:
                raise ValidationError(_(content['code_message_value']))
        except Exception as e:
            raise ValidationError(str(e))
