# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import string
import json
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError, AccessDenied
from odoo.http import Controller, Response, request, route
import werkzeug
from werkzeug.utils import redirect
from werkzeug.http import dump_cookie
import base64
import re
from urllib.request import urlopen
from datetime import *
import requests


class ShopifyWebhook(Controller):

    @route('/shopify/<int:shop_id>/products/create', type='json', auth='public', csrf=False, website=False, methods=['POST', 'GET'])
    def create_product_callback(self, shop_id=None, **post):
        try:
            search_user = request.env['res.users'].sudo().search([('id', '=', shop_id)], limit=1)
            search_shop = request.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)], limit=1)
            product = request.jsonrequest
            if product.get('id'):
                for pro_val in product['variants']:
                    product_vals = {
                        'shopify_product_id': pro_val['id'],
                        'name': str(product['title']) + " " + str(pro_val['title']) if len(product['variants']) > 1 else str(product['title']),
                        'lst_price': pro_val['price'],
                        'description': re.sub(r'<.*?>', '', product['body_html']) if product['body_html'] else None,
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
                        'shopify_user_id': shop_id,
                        'image_1920': base64.b64encode(
                            urlopen(product['images'][0]['src']).read()) if product['images'] else None,
                        'shopify_shop_id': search_shop.id
                    }
                    create_product = request.env['product.template'].sudo().create(product_vals)
                    if create_product:
                        return Response("OK", status=200)
                    else:
                        return Response("OK", status=200)
            else:
                return Response("OK", status=200)
        except Exception as e:
            raise ValidationError(str(e))

    @route('/shopify/<int:shop_id>/products/update', type='json', auth='public', csrf=False, website=False, methods=['POST', 'GET'])
    def update_product_callback(self, shop_id=None, **post):
        try:
            search_user = request.env['res.users'].sudo().search([('id', '=', shop_id)], limit=1)
            search_shop = request.env['s.shop'].sudo().search([('shop_base_url', '=', search_user.login)], limit=1)
            product = request.jsonrequest
            if product.get('id'):
                for pro_val in product['variants']:
                    product_vals = {
                        'shopify_product_id': pro_val['id'],
                        'name': str(product['title']) + " " + str(pro_val['title']) if len(product['variants']) > 1 else str(product['title']),
                        'lst_price': pro_val['price'],
                        'description': re.sub(r'<.*?>', '', product['body_html']) if product['body_html'] else None,
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
                        'shopify_user_id': shop_id,
                        'image_1920': base64.b64encode(
                            urlopen(product['images'][0]['src']).read()) if product['images'] else None,
                        'shopify_shop_id': search_shop.id
                    }
                    search_product = request.env["product.template"].sudo().search(
                        [('shopify_product_id', '=', pro_val['id'])], limit=1)
                    if search_product:
                        search_product.sudo().write(product_vals)
                        return Response("OK", status=200)
                    else:
                        raise ValidationError('This Product Is Not Created In Product Template.')
                return Response("OK", status=200)
            else:
                return Response("OK", status=200)
        except Exception as e:
            raise ValidationError(str(e))

    @route('/shopify/<int:shop_id>/orders/create', type='json', auth='public', csrf=False, website=False, methods=['POST', 'GET'])
    def create_order_callback(self, shop_id=None, **post):
        try:
            order = request.jsonrequest
            if order.get('id'):
                list_order_product = []
                # todo: Search and Link or Create Customer in Odoo
                if 'customer' not in order:
                    search_customer = request.env['res.partner'].sudo().search(
                        [('name', '=', order['shipping_address']['name']),
                         ('phone', '=', order['shipping_address']['phone'])], limit=1)
                    if not search_customer:
                        request.env['res.partner'].create({
                            'company_type': 'person',
                            'name': order['shipping_address']['name'],
                            'phone': order['shipping_address']['phone'],
                            'address1': order['shipping_address']['address1'],
                            'city': order['shipping_address']['city'],
                            'shopify_user_id': shop_id,
                            'country': request.env['res.country'].sudo().search(
                                [('name', '=', order['shipping_address']['country'])], limit=1).id})
                create_time_order = (order['created_at'].split('+')[0])
                time_order = create_time_order.replace('T', ' ')
                link_partner = request.env['res.partner'].sudo().search(
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
                    'shopify_user_id': shop_id,
                    'date_order': datetime.strptime(time_order, '%Y-%m-%d %H:%M:%S'),
                    'partner_id': link_partner.id if 'customer' not in order else request.env[
                        'res.partner'].sudo().search([('shopify_customer_id', '=', order['customer']['id'])],
                                                     limit=1).id
                }
                new_record = request.env['sale.order'].sudo().create(order_vals)
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
                                        search_tax = request.env['account.tax'].sudo().search(
                                            [('amount', '=', float(product_tax['rate'] * 100)),
                                             ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')], limit=1)
                                        if search_tax:
                                            list_tax.append(search_tax.id)
                                        else:
                                            request.env['account.tax'].create({
                                                'amount': float(product_tax['rate'] * 100),
                                                'amount_type': 'percent',
                                                'type_tax_use': 'sale',
                                                'name': 'Tax ' + str(product_tax['rate'] * 100) + ' %',
                                                'active': True
                                            })
                                            search_tax_1 = request.env['account.tax'].sudo().search(
                                                [('amount', '=', float(product_tax['rate'] * 100)),
                                                 ('amount_type', '=', 'percent'), ('type_tax_use', '=', 'sale')],
                                                limit=1)
                                            list_tax.append(search_tax_1.id)
                                existing_products = request.env['product.template'].sudo().search(
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
                                return Response("OK", status=200)
                            else:
                                existing_products = request.env['product.template'].sudo().search(
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
                                return Response("OK", status=200)
                    else:
                        return Response("OK", status=200)
                else:
                    return Response("OK", status=200)
            else:
                return Response("OK", status=200)
        except Exception as e:
            raise ValidationError(str(e))

    @route('/shopify/<int:shop_id>/orders/updated', type='json', auth='public', csrf=False, website=False, methods=['POST', 'GET'])
    def update_order_callback(self, shop_id=None, **post):
        try:
            order = request.jsonrequest
            if order.get('id'):
                # todo: Search and Link or Create Customer in Odoo
                if 'customer' not in order:
                    search_customer = request.env['res.partner'].sudo().search(
                        [('name', '=', order['shipping_address']['name']),
                         ('phone', '=', order['shipping_address']['phone'])], limit=1)
                    if not search_customer:
                        request.env['res.partner'].create({
                            'company_type': 'person',
                            'name': order['shipping_address']['name'],
                            'phone': order['shipping_address']['phone'],
                            'address1': order['shipping_address']['address1'],
                            'city': order['shipping_address']['city'],
                            'shopify_user_id': shop_id,
                            'country': request.env['res.country'].sudo().search(
                                [('name', '=', order['shipping_address']['country'])], limit=1).id})
                create_time_order = (order['created_at'].split('+')[0])
                time_order = create_time_order.replace('T', ' ')
                link_partner = request.env['res.partner'].sudo().search(
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
                    'shopify_user_id': shop_id,
                    'date_order': datetime.strptime(time_order, '%Y-%m-%d %H:%M:%S'),
                    'partner_id': link_partner.id if order['customer'] else request.env[
                        'res.partner'].sudo().search([('shopify_customer_id', '=', order['customer']['id'])],
                                                     limit=1).id
                }
                search_order = request.env['sale.order'].sudo().search([('shopify_order_id', '=', order['id'])],
                                                                       limit=1)
                if search_order:
                    search_order.sudo().write(order_vals)
                    return Response("OK", status=200)
                else:
                    return Response("OK", status=200)
            else:
                return Response("OK", status=200)
        except Exception as e:
            raise ValidationError(str(e))
