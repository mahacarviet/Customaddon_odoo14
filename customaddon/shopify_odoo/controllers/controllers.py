# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import shopify
import werkzeug
from werkzeug.utils import redirect
from werkzeug.http import dump_cookie
import random
import string
import base64
import re
from urllib.request import urlopen
from datetime import *
import calendar
import time
base_url = "https://odoo.website"


class ShopifyApp(http.Controller):
    @http.route('/shopify/auth/<string:name>', auth='public', type='http', website=True)
    def shopify_auth(self, name=None, **kw):
        search_app = http.request.env['s.app'].sudo().search([('app_name', '=', name)])
        shopify.Session.setup(api_key=search_app.api_key, secret=search_app.secret_key)
        shop_url = request.params['shop']
        callback_url = base_url + "/shopify/finalize/" + name
        scopes = ['read_products', 'write_products', 'read_product_listings', 'read_orders', 'write_orders',
                  'read_inventory', 'write_inventory', 'read_customers', 'write_customers',
                  'read_gift_cards', 'write_gift_cards', 'read_discounts', 'write_discounts', 'read_script_tags',
                  'write_script_tags', 'read_assigned_fulfillment_orders', 'write_assigned_fulfillment_orders']
        new_session = shopify.Session(shop_url, search_app.api_version)
        auth_url = new_session.create_permission_url(scopes, callback_url)
        print(auth_url)
        return werkzeug.utils.redirect(auth_url)

    @http.route('/shopify/finalize/<string:name>', auth='public', type='http', website=True)
    def shopify_finalize(self, name=None, **kwargs):
        request_params = request.params
        shop_url = request_params['shop']
        x = shop_url.split('.')
        shop_name = x[0]
        result_str = ''.join(random.choice(string.digits) for i in range(10))
        search_shop = http.request.env['s.shop'].sudo().search([('shop_owner', '=', shop_name)])
        search_app = http.request.env['s.app'].sudo().search([('app_name', '=', name)])
        if search_shop:
            search_shop.sudo().write({
                'shop_base_url': shop_url,
                'shop_owner': shop_name,
                'shop_user': shop_url,
                'shop_password': result_str,
                'shop_app_ids': [(4, search_app.id)]
            })
        else:
            search_shop = request.env['s.shop'].sudo().create({
                'shop_base_url': shop_url,
                'shop_owner': shop_name,
                'shop_user': shop_url,
                'shop_password': result_str,
                'shop_app_ids': [(4, search_app.id)]
            })
        search_user = request.env['res.users'].sudo().search([('login', '=', shop_url)], limit=1)
        if search_user:
            search_user.sudo().write({
                'name': shop_name,
                'login': shop_url,
                'password': str(result_str)
            })
        else:
            request.env['res.users'].sudo().create({
                'name': shop_name,
                'login': shop_url,
                'password': str(result_str)
            })
        uid = search_user
        #   Login in Odoo
        current_shop = request.env['s.shop'].sudo().search([('shop_owner', '=', shop_name)], limit=1)

        print(result_str)
        print(uid)
        session = shopify.Session(shop_url, search_app.api_version)
        access_token = session.request_token(request_params)
        # link_shop = request.env['s.shop'].sudo().search([('shop_owner', '=', shop_name)], limit=1)
        if current_shop:
            current_shop.sudo().write({'shop_user_id': uid})
        search_shop_app = request.env['s.sp.app'].sudo().search([('token_shop_app', '=', access_token)], limit=1)
        if search_shop_app:
            search_shop_app.sudo().write({
                'web_user': shop_url,
                'password_user': '1',
                'shop_app_s_apps': search_app.id,
                'shop_app_s_shops': search_shop.id
            })
        else:
            search_shop_app = request.env['s.sp.app'].sudo().create({
                'token_shop_app': access_token,
                'web_user': shop_url,
                'password_user': '1',
                'shop_app_s_apps': search_app.id,
                'shop_app_s_shops': search_shop.id
            })
        session = shopify.Session(shop_url, search_app.api_version, access_token)
        shopify.ShopifyResource.activate_session(session)

        # # todo: create shop in 'res.partner'
        # current_shop = shopify.Shop.current()
        # search_partner = request.env['res.partner'].search([('email', '=', current_shop.customer_email)], limit=1)
        # if not search_partner:
        #     partner_id = request.env['res.partner'].sudo().create({
        #         'company_type': 'company',
        #         'name': current_shop.name,
        #         'street': current_shop.address1,
        #         'street2': current_shop.address2 if current_shop.address2 else None,
        #         'city': current_shop.city,
        #         'zip': current_shop.zip,
        #         'email': current_shop.customer_email,
        #         'website': current_shop.domain,
        #         'shopify_user_id': uid,
        #         'shopify_shop_id': request.env['s.shop'].search([("shop_base_url", "=", current_shop.domain)], limit=1).id
        #     })
        #     print(partner_id)
        #
        # #   Update Shop Currency
        # search_shop.sudo().write({'shop_currency': current_shop.currency})
        #
        #   # Active Shop Currency Un Module Core
        # active_currency = request.env['res.currency'].search(
        #     [("name", "=", current_shop.currency), ("active", "=", True)])
        # if not active_currency:
        #     active_currency_1 = request.env['res.currency'].search(
        #         [("name", "=", current_shop.currency), ("active", "=", False)])
        #     if active_currency_1:
        #         active_currency_1.active = True
        #
        # search_account = request.env['res.users'].sudo().search([('id', '=', request.env.user.id)], limit=1)
        # commission_group = request.env.ref('shopify_odoo.group_shopify_admin')
        # commission_group.sudo().write({'users': [(4, search_account.id)]})
        # # Update Email Shop Account
        # if not search_account.email:
        #     search_account.sudo().write({'email': current_shop.customer_email})
        # else:
        #     search_account.sudo().write({'email': current_shop.customer_email})
        #
        # # todo: create customer in 'res.partner'
        # website = 'https://' + current_shop.domain
        # current_customer = shopify.Customer.search()
        # for customer in current_customer:
        #     list_customer = request.env['res.partner'].search([("shopify_customer_id", "=", customer.id)], limit=1)
        #     if not list_customer:
        #         customer_name = customer.first_name + ' ' + customer.last_name
        #         request.env['res.partner'].sudo().create({
        #             'shopify_customer_id': customer.id,
        #             'company_type': 'person',
        #             'name': customer_name,
        #             'parent_id': request.env['res.partner'].search([("website", "=", website)], limit=1).id,
        #             'phone': customer.phone,
        #             'email': customer.email,
        #             'shopify_user_id': uid,
        #             'shopify_shop_id': request.env['s.shop'].search([("shop_base_url", "=", current_shop.domain)], limit=1).id
        #         })
        #
        # # todo: create product in 'product.template'
        # product_current = shopify.Product.find()
        # for product in product_current:
        #     for pro_val in product.variants:
        #         product_vals = {
        #             'shopify_product_id': pro_val.id,
        #             'name': str(product.title) + " " + str(pro_val.title) if len(product.variants) > 1 else str(product.title),
        #             'lst_price': pro_val.price,
        #             'description': re.sub(r'<.*?>', '', product.body_html) if product.body_html else None,
        #             'shopify_product_type': product.product_type,
        #             'default_code': pro_val.sku if pro_val.sku else None,
        #             'barcode': pro_val.barcode if pro_val.barcode else None,
        #             'check_product_shopify': True,
        #             'sale_ok': True if product.status == 'active' else False,
        #             'purchase_ok': False,
        #             'type': 'product',
        #             'taxes_id': None,
        #             'is_published': True,
        #             'categ_id': 1,
        #             'shopify_user_id': uid,
        #             'image_1920': base64.b64encode(urlopen(product.images[0].src).read()) if product.images else None,
        #             'shopify_shop_id': request.env['s.shop'].search([("shop_base_url", "=", current_shop.domain)], limit=1).id
        #         }
        #         existed_product = request.env["product.template"].sudo().search(
        #             [('shopify_product_id', '=', pro_val.id)],
        #             limit=1)
        #         if not existed_product:
        #             request.env['product.template'].sudo().create(product_vals)
        #         else:
        #             existed_product.sudo().write(product_vals)

        # todo: create order in 'sale.order'
        list_order = shopify.Order.find()
        list_order_product = []
        for order in list_order:
            # todo: Search and Link or Create Customer in Odoo
            if 'customer' not in order.attributes:
                search_customer = request.env['res.partner'].sudo().search(
                    [('name', '=', order.shipping_address.name), ('phone', '=', order.shipping_address.phone)], limit=1)
                if not search_customer:
                    request.env['res.partner'].sudo().create({
                        'shopify_user_id': uid,
                        'company_type': 'person',
                        'name': order.shipping_address.name,
                        'phone': order.shipping_address.phone,
                        'address1': order.shipping_address.address1,
                        'city': order.shipping_address.city,
                        'country': request.env['res.country'].sudo().search(
                            [('name', '=', order.shipping_address.country)], limit=1).id})
            create_time_order = (order.created_at.split('+')[0])
            time_order = create_time_order.replace('T', ' ')
            link_partner = request.env['res.partner'].sudo().search(
                [('name', '=', order.shipping_address.name), ('phone', '=', order.shipping_address.phone)], limit=1)
            transaction_id = shopify.Transaction.find(order_id=order.id)
            if len(transaction_id) > 0:
                if 'id' in transaction_id[0].attributes:
                    transaction = str(transaction_id[0].id)
                else:
                    transaction = None
            else:
                transaction = None
            if len(order.fulfillments) > 0:
                  shopify_location = str(order.fulfillments[0].attributes['location_id'])
            else:
                  shopify_location = None
            order_vals = {
                'shopify_order_id': order.id,
                'name': order.id,
                'shopify_payment_method': order.gateway,
                'shopify_currency': order.currency,
                'shopify_transactions_id': transaction,
                'shopify_location_id': str(order.location_id) if order.location_id else shopify_location,
                'state': 'draft',
                'note': str(order.note) if order.note else None,
                'shopify_user_id': uid,
                'date_order': datetime.strptime(time_order, '%Y-%m-%d %H:%M:%S'),
                'partner_id': link_partner.id if 'customer' not in order.attributes else request.env[
                    'res.partner'].sudo().search([('shopify_customer_id', '=', order.customer.id)], limit=1).id
            }

            existing_orders = request.env['sale.order'].sudo().search([('shopify_order_id', '=', order.id)], limit=1)
            if len(existing_orders) < 1:
                new_record = request.env['sale.order'].sudo().create(order_vals)
                #   Add Product to Order
                if new_record:
                    if "line_items" in order.attributes:
                        vals_product = order.line_items
                        for order_product in vals_product:
                            #   Check And Add Product Tax
                            if order_product.taxable:
                                list_tax = []
                                for product_tax in order_product.tax_lines:
                                    if 'rate' in product_tax.attributes:
                                        search_tax = request.env['account.tax'].sudo().search(
                                            [('amount', '=', float(product_tax.rate * 100)),
                                             ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')], limit=1)
                                        if search_tax:
                                            list_tax.append(search_tax.id)
                                        else:
                                            request.env['account.tax'].sudo().create({
                                                'amount': float(product_tax.rate * 100),
                                                'amount_type': 'percent',
                                                'type_tax_use': 'sale',
                                                'name': 'Tax ' + str(product_tax.rate * 100) + ' %',
                                                'active': True
                                            })
                                            search_tax_1 = request.env['account.tax'].sudo().search(
                                                [('amount', '=', float(product_tax.rate * 100)),
                                                 ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')],
                                                limit=1)
                                            list_tax.append(search_tax_1.id)
                                existing_products = request.env['product.template'].sudo().search(
                                    [('shopify_product_id', '=', order_product.variant_id)], limit=1)
                                if existing_products:
                                    list_order_product.append({
                                        'shopify_line_id': order_product.id,
                                        'product_id': existing_products.product_variant_id.id,
                                        'product_uom_qty': order_product.quantity,
                                        'price_unit': order_product.price,
                                        'tax_id': list_tax
                                    })
                                    if list_order_product:
                                        new_record.order_line = [(0, 0, e) for e in list_order_product]
                                    list_order_product = []
                            else:
                                existing_products = request.env['product.template'].sudo().search(
                                    [('shopify_product_id', '=', order_product.variant_id)], limit=1)
                                if existing_products:
                                    list_order_product.append({
                                        'shopify_line_id': order_product.id,
                                        'product_id': existing_products.product_variant_id.id,
                                        'product_uom_qty': order_product.quantity,
                                        'price_unit': order_product.price
                                    })
                                    if list_order_product:
                                        new_record.order_line = [(0, 0, e) for e in list_order_product]
                                    list_order_product = []
            else:
                existing_orders.sudo().write(order_vals)
        #
        # password_login = request.env['s.shop'].search([('shop_base_url', '=', current_shop.domain)])
        # print(password_login.shop_password)
        #
        # # todo: insert script theme
        # script_src = search_app.link_script_tag
        # existedScriptTags = shopify.ScriptTag.find(src=script_src)
        # print(shopify.ScriptTag.find())
        # if not existedScriptTags:
        #     shopify.ScriptTag.create({
        #         "event": "onload",
        #         "src": script_src
        #     })
        # request.env['create.webhook.shopify'].sudo().create_product_shopify(uid)
        # request.env['create.webhook.shopify'].sudo().create_order_shopify(uid)
        # request.env['create.webhook.shopify'].sudo().update_product_shopify(uid)
        # request.env['create.webhook.shopify'].sudo().update_order_shopify(uid)
        # search_shop_app.create_webhook(topic, address)


        print(shopify.ScriptTag.find())
        print(shopify.Webhook.find())
        # login
        db = http.request.env.cr.dbname
        request.env.cr.commit()
        uid = request.session.authenticate(db, current_shop.shop_user, current_shop.shop_password)
        # redirect ve action, menu -> redern form view 1 models
        # models co truong shop_id de viet record rule
        return werkzeug.utils.redirect('https://odoo.website/web#cids=1&home=')


