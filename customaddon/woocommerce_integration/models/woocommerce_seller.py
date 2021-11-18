import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from woocommerce import API



class WoocommerceSeller(models.Model):
    _name = "woocommerce.seller"
    _description = "Seller"
    _rec_name = 'link_website'

    link_website = fields.Char(string='Link Website', limit=1)
    consumer_key = fields.Char(string='My Consumer Key', limit=1)
    consumer_secret = fields.Char(string='My Consumer Secret', limit=1)

    def action_view_config(self):
        res_id = self.env['woocommerce.seller'].sudo().search([('consumer_key', '!=', False)])
        return {
            'name': _('Config Connection Woocommerce API'),
            'view_mode': 'form',
            'view_id': self.env.ref('woocommerce_integration.woocommerce_seller_form_view').id,
            'res_model': 'woocommerce.seller',
            'context': "{'create': False}",
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': res_id.id if res_id else False,
        }

    def test_connect(self):
        try:
            wcapi = API(
                url=self.link_website,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                wp_api=True,
                version="wc/v3",
                query_string_auth=True  # Force Basic Authentication as query string true and using under HTTPS
            )
            response = wcapi.get("products/tags").json()
            if "id" in response[0]:
                val = {
                    'link_website': self.link_website,
                    "consumer_key": self.consumer_key,
                    'consumer_secret': self.consumer_secret
                }
                existed_secret = self.env['woocommerce.seller'].search([('link_website', '=', self.link_website)], limit=1)
                if len(existed_secret) < 1:
                    self.env['woocommerce.seller'].create(val)
                else:
                    existed_secret.write(val)
            else:
                raise ValidationError(_('My Database is Wrong.'))
        except Exception as e:
            raise ValidationError(str(e))
