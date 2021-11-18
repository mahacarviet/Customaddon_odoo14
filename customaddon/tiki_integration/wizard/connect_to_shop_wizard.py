import requests
from odoo import fields, models, api
from odoo.http import request


class SellerConnectWizard(models.TransientModel):
    _name = 'tiki.connect.wizard'
    _description = 'Connect to Tiki Integration'

    secret = fields.Char(string='Connection parameters')
    user_agent = fields.Selection([
        ('chrome', 'Chrome'),
        ('edge', 'Edge'),
        ('firefox', 'Firefox')], string='User Agent')

    def default_get(self, fields_list):
        res = super(SellerConnectWizard, self).default_get(fields_list)
        current_seller = self.env['tiki.seller'].sudo().search([])[0]
        if len(current_seller) < 1:
            pass
        else:
            res['secret'] = current_seller.secret
        return res

    def init_connect_tiki_seller_submit(self):
        if self.user_agent == 'chrome':
            user_agent_val = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
        elif self.user_agent == 'firefox':
            user_agent_val = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
        else:
            user_agent_val = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
        val = {
            'secret': self.secret,
            'user_agent': user_agent_val,
        }
        existed_secret = self.env['tiki.seller'].search([('secret', '=', self.secret)], limit=1)
        if len(existed_secret) < 1:
            self.env['tiki.seller'].create(val)
        else:
            existed_secret.write(val)





