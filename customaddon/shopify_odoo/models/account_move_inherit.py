import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveInherit(models.Model):
    _inherit = "account.move"

    shopify_order = fields.Char()
    shopify_transactions = fields.Char()
    shopify_location = fields.Char()
    check_refund_shopify = fields.Boolean(string='Check Refund Shopify', default=False)

    def create_refund_shopify(self):
        try:
            if self.name[0] == 'R':
                if not self.check_refund_shopify:
                    list_products = []
                    current_account_id = self.env.uid
                    search_account = self.env['res.users'].sudo().search([('id', '=', current_account_id)])
                    search_token = self.env['s.sp.app'].sudo().search([('web_user', '=', search_account.login)])
                    if not search_token:
                        raise ValidationError('My Account Can Not Create Refund Shopify Order.')
                    search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_account.login)])
                    api_version = search_shop.shop_app_ids[0].api_version
                    if not search_shop:
                        raise ValidationError('Database In My Shop Is Wrong.')
                    for product in self.invoice_line_ids:
                        val = {
                            "line_item_id": int(product.shopify_line_item_id) if int(
                                product.shopify_line_item_id) else 0,
                            "quantity": int(product.quantity),
                            "restock_type": "return",
                            "location_id": int(self.shopify_location)
                        }
                        list_products.append(val)

                    url = "https://" + search_account.login + "/admin/api/" + api_version + "/orders/" + self.shopify_order + "/refunds.json"

                    payload = json.dumps({
                        "refund": {
                            "currency": search_shop.shop_currency,
                            "notify": True,
                            "note": "Refund Order",
                            "shipping": {
                                "full_refund": True
                            },
                            "refund_line_items": list_products,
                            "transactions": [
                                {
                                    "parent_id": self.shopify_transactions,
                                    "amount": self.amount_total,
                                    "kind": "refund",
                                    "gateway": "bogus"
                                }
                            ]
                        }
                    })

                    headers = {
                        'X-Shopify-Access-Token': search_token.token_shop_app,
                        'Content-Type': 'application/json'
                    }

                    response = requests.request("POST", url, headers=headers, data=payload)
                    print(response)
                    result = response.json()
                    self.check_refund_shopify = True
                    print(result)
                    if 'errors' in result:
                        raise ValidationError(result['errors'])
                else:
                    raise ValidationError('This Credit Note Is Not An Shopify Order.')
            else:
                raise ValidationError('This Invoice Is Not Create Refund.')
        except Exception as e:
            raise ValidationError(str(e))


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"

    shopify_line_item_id = fields.Char(related='sale_line_ids.shopify_line_id')
