# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json
from datetime import datetime
import base64
import re
from urllib.request import urlopen


class SShop(models.Model):
    _name = 's.fetch'
    _description = 's_fetch'
    _rec_name = 's_shop_s_fetch'

    date_time_from = fields.Date()
    date_time_to = fields.Date()
    shop_user_id = fields.Integer()

    s_shop_s_fetch = fields.Many2one('s.shop', string='Shop')
    s_fetch_log_product_shopify = fields.Many2many('s.fetch.log.product', string='Fetch Log Product')
    s_fetch_log_order_shopify = fields.Many2many('s.fetch.log.order', string='Fetch Log Order')

    @api.onchange('shop_user_id', 'res_partner_s_fetch')
    def _add_shop_user_id(self):
        # self.shop_user_id = self.env.uid
        self.shop_user_id = 8
        search_user = self.env['res.users'].search([('id', '=', self.shop_user_id)], limit=1)
        search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)], limit=1)
        self.s_shop_s_fetch = search_shop.id

    def fetch_product_shopify(self):
        try:
            # current_id = self.env.uid
            current_id = 8
            search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)])[0]
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)])
            api_version = search_shop.shop_app_ids[0].api_version

            url_1 = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/products.json"
            url_2 = "?created_at_min=" + str(self.date_time_from) + "&created_at_max=" + str(self.date_time_to)
            url = str(url_1) + str(url_2)

            payload = {}
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()
            fetch_count = 0
            if 'products' in result:
                for product in result['products']:
                    if 'id' in product:
                        for pro_val in product['variants']:
                            product_vals = {
                                'shopify_product_id': pro_val['id'],
                                'name': str(product['title']) + " " + str(pro_val['title']) if len(
                                    product['variants']) > 1 else str(product['title']),
                                'lst_price': pro_val['price'],
                                'description': re.sub(r'<.*?>', '', product['body_html']) if product[
                                    'body_html'] else None,
                                'shopify_product_type': product['product_type'],
                                'default_code': pro_val['sku'] if pro_val['sku'] else None,
                                'barcode': pro_val['barcode'] if pro_val['barcode'] else None,
                                'check_product_shopify': True,
                                'sale_ok': True if product['status'] == 'active' else False,
                                'purchase_ok': False,
                                'type': 'product',
                                'taxes_id': None,
                                'is_published': True,
                                'categ_id': 1,
                                'shopify_user_id': current_id,
                                'image_1920': base64.b64encode(
                                    urlopen(product['images'][0]['src']).read()) if product['images'] else None,
                                'shopify_shop_id': search_shop.id
                            }
                            existed_product = self.env["product.template"].sudo().search(
                                [('shopify_product_id', '=', pro_val['id'])], limit=1)
                            if not existed_product:
                                self.env['product.template'].sudo().create(product_vals)
                                fetch_count = fetch_count + 1
                            else:
                                existed_product.sudo().write(product_vals)
                                fetch_count = fetch_count + 1
            self.s_fetch_log_product_shopify = [(0, 0, {
                'date_time_from': self.date_time_from,
                'date_time_to': self.date_time_to,
                'time_fetch': datetime.now(),
                'success_fetch': fetch_count,
                'shop_user_id': self.shop_user_id
            })]

        except Exception as e:
            raise ValidationError(str(e))

    def fetch_order_shopify(self):
        try:
            # current_id = self.env.uid
            current_id = 8
            search_user = self.env['res.users'].search([('id', '=', current_id)], limit=1)
            search_token = self.env['s.sp.app'].sudo().search([('web_user', 'ilike', search_user.login)], limit=1)
            search_shop = self.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)], limit=1)
            api_version = search_shop.shop_app_ids[0].api_version

            url_1 = "https://" + str(search_user.login) + "/admin/api/" + str(api_version) + "/orders.json"
            url_2 = "?created_at_min=" + str(self.date_time_from) + "&created_at_max=" + str(self.date_time_to)
            url = str(url_1) + str(url_2)

            payload = {}
            headers = {
                'X-Shopify-Access-Token': search_token.token_shop_app
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()
            fetch_count = 0
            if 'orders' in result:
                list_order_product = []
                for order in result['orders']:
                    # todo: Search and Link or Create Customer in Odoo
                    if 'customer' not in order:
                        search_customer = self.env['res.partner'].sudo().search(
                            [('name', '=', order['shipping_address']['name']),
                             ('phone', '=', order['shipping_address']['phone'])], limit=1)
                        if not search_customer:
                            self.env['res.partner'].create({
                                'company_type': 'person',
                                'name': order['shipping_address']['name'],
                                'phone': order['shipping_address']['phone'],
                                'address1': order['shipping_address']['address1'],
                                'city': order['shipping_address']['city'],
                                'shopify_user_id': self.shop_user_id,
                                'country': self.env['res.country'].sudo().search(
                                    [('name', '=', order['shipping_address']['country'])], limit=1).id})
                    create_time_order = (order['created_at'].split('+')[0])
                    time_order = create_time_order.replace('T', ' ')
                    link_partner = self.env['res.partner'].sudo().search(
                        [('name', '=', order['shipping_address']['name']),
                         ('phone', '=', order['shipping_address']['phone'])], limit=1)
                    # transaction_id = shopify.Transaction.find(order_id=order.id)
                    if len(order['fulfillments']) > 0:
                        shopify_location = str(order['fulfillments'][0]['location_id'])
                    else:
                        shopify_location = None
                    order_vals = {
                        'shopify_order_id': order['id'],
                        'name': order['id'],
                        'shopify_payment_method': order['gateway'],
                        'shopify_currency': order['currency'],
                        # 'shopify_transactions_id': str(transaction_id[0].id) if 'id' in transaction_id[
                        #     0].attributes else None,
                        'shopify_transactions_id': None,
                        'shopify_location_id': str(order['location_id']) if order['location_id'] else shopify_location,
                        'state': 'draft',
                        'note': str(order['note']) if order['note'] else None,
                        'shopify_user_id': self.shop_user_id,
                        'date_order': datetime.strptime(time_order, '%Y-%m-%d %H:%M:%S'),
                        'partner_id': link_partner.id if 'customer' not in order else self.env[
                            'res.partner'].sudo().search([('shopify_customer_id', '=', order['customer']['id'])],
                                                         limit=1).id
                    }
                    existing_orders = self.env['sale.order'].sudo().search([('shopify_order_id', '=', order['id'])],
                                                                           limit=1)
                    if len(existing_orders) < 1:
                        new_record = self.env['sale.order'].sudo().create(order_vals)
                        #   Add Product to Order
                        if new_record:
                            if order['line_items']:
                                vals_product = order['line_items']
                                for order_product in vals_product:
                                    #   Check And Add Product Tax
                                    if order_product['taxable']:
                                        list_tax = []
                                        for product_tax in order_product['tax_lines']:
                                            if product_tax['rate']:
                                                search_tax = self.env['account.tax'].sudo().search(
                                                    [('amount', '=', float(product_tax['rate'] * 100)),
                                                     ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')],
                                                    limit=1)
                                                if search_tax:
                                                    list_tax.append(search_tax.id)
                                                else:
                                                    self.env['account.tax'].create({
                                                        'amount': float(product_tax['rate'] * 100),
                                                        'amount_type': 'percent',
                                                        'type_tax_use': 'sale',
                                                        'name': 'Tax ' + str(product_tax['rate'] * 100) + ' %',
                                                        'active': True
                                                    })
                                                    search_tax_1 = self.env['account.tax'].sudo().search(
                                                        [('amount', '=', float(product_tax['rate'] * 100)),
                                                         ('amount_type', '=', 'percent'),
                                                         ('type_tax_use', '=', 'sale')],
                                                        limit=1)
                                                    list_tax.append(search_tax_1.id)
                                        existing_products = self.env['product.template'].sudo().search(
                                            [('shopify_product_id', '=', order_product['variant_id'])], limit=1)
                                        if existing_products:
                                            list_order_product.append({
                                                'shopify_line_id': order_product['id'],
                                                'product_id': existing_products.product_variant_id.id,
                                                'product_uom_qty': order_product['quantity'],
                                                'price_unit': order_product['price'],
                                                'tax_id': list_tax
                                            })
                                            if list_order_product:
                                                new_record.order_line = [(0, 0, e) for e in list_order_product]
                                            list_order_product = []
                                    else:
                                        existing_products = self.env['product.template'].sudo().search(
                                            [('shopify_product_id', '=', order_product['variant_id'])], limit=1)
                                        if existing_products:
                                            list_order_product.append({
                                                'shopify_line_id': order_product['id'],
                                                'product_id': existing_products.product_variant_id.id,
                                                'product_uom_qty': order_product['quantity'],
                                                'price_unit': order_product['price']
                                            })
                                            if list_order_product:
                                                new_record.order_line = [(0, 0, e) for e in list_order_product]
                                            list_order_product = []
                        fetch_count = fetch_count + 1
                    else:
                        existing_orders.sudo().write(order_vals)
                        fetch_count = fetch_count + 1
                self.s_fetch_log_order_shopify = [(0, 0, {
                    'date_time_from': self.date_time_from,
                    'date_time_to': self.date_time_to,
                    'time_fetch': datetime.now(),
                    'success_fetch': fetch_count,
                    'shop_user_id': self.shop_user_id
                })]
        except Exception as e:
            raise ValidationError(str(e))


class SFetchLogProduct(models.Model):
    _name = 's.fetch.log.product'
    _description = 's_fetch'

    date_time_from = fields.Date()
    date_time_to = fields.Date()
    time_fetch = fields.Datetime()
    success_fetch = fields.Integer()
    shop_user_id = fields.Integer()


class SFetchLogOrder(models.Model):
    _name = 's.fetch.log.order'
    _description = 's_fetch'

    date_time_from = fields.Date()
    date_time_to = fields.Date()
    time_fetch = fields.Datetime()
    success_fetch = fields.Integer()
    shop_user_id = fields.Integer()
