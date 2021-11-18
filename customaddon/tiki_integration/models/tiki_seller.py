import requests
from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _


class TikiSeller(models.Model):
    _name = "tiki.seller"
    _description = "Seller Tiki"

    seller_id = fields.Char('Seller ID')
    code = fields.Char('Code')
    contract_code = fields.Char('Contact Code')
    name = fields.Char('Name')
    logo = fields.Char('Logo')
    hotline = fields.Char('Hotline')
    email = fields.Char('Email')
    connect_to = fields.Char('Connect to')
    secret = fields.Char('Secret')
    user_agent = fields.Text('User Agent')

    def get_seller_tiki(self):
        try:
            exited_record = self.env['tiki.seller'].sudo().search([])[0]
            url = "https://api-sellercenter.tiki.vn/integration/sellers"
            payload = {}
            headers = {
                'tiki-api': exited_record.secret,
                'User-Agent': exited_record.user_agent,
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            seller = response.json()
            val = {}

            if ('id' and 'name' and 'code' and 'contract_code' and 'secret' and 'email' and 'connect_to' and 'logo') in seller:
                val['seller_id'] = seller['id']
                val['name'] = seller['name']
                val['code'] = seller['code']
                val['contract_code'] = seller['contract_code']
                val['secret'] = seller['secret']
                val['email'] = seller['email']
                val['connect_to'] = seller['connect_to']
                val['logo'] = seller['logo']
            existed_seller = self.env['tiki.seller'].search([('secret', '=', seller['secret'])], limit=1)
            if len(existed_seller) < 1:
                self.env['tiki.seller'].create(val)
            else:
                existed_seller.write(val)
        except Exception as e:
            print(e)
