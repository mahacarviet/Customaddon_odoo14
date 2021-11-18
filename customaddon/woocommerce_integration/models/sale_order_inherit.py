
import requests
import json
from datetime import *
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    check_woo_customer = fields.Boolean(store=True)


#       Class Inherit Sale Order
class SaleOrderInherit(models.Model):
    _inherit = "sale.order"
    _description = "Sync Order Woocommerce"

    woo_order_number = fields.Char()
    woo_order_status = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('on-hold', 'On-hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
        ('trash', 'Trash')], string='Order Status')

    woo_payment_method = fields.Char(string='Payment Method')

    #       Sync Database for Woocommerce Order to Sale Order
    def get_list_order_woo(self):
        try:
            current_seller = self.env['woocommerce.seller'].sudo().search([])[0]
            url = str(current_seller.link_website) + "/wp-json/wc/v3/orders?consumer_key=" + str(
                current_seller.consumer_key) + "&consumer_secret=" + str(current_seller.consumer_secret)
            payload = {}
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)

            result_list_order = response.json()

            if "code" in result_list_order:
                raise ValidationError(_(result_list_order["message"]))
            elif result_list_order[0]["id"]:
                list_product = []
                for data in result_list_order:
                    customesr = data["billing"]
                    #   Get Information Customer
                    vals_customesr = {
                        'name': customesr['last_name'] + customesr['first_name'],
                        'phone': customesr['phone'],
                        'mobile': customesr['phone'],
                        'email': customesr['email'],
                        'company_type': 'person',
                        'type': 'contact',
                        'street': customesr['address_1'],
                        'comment': 'Sync By Call Woocommerce API',
                        'check_woo_customer': True
                    }

                    #   Check Customer
                    existing_customer = self.env['res.partner'].sudo().search(
                        ['&', ('phone', '=', customesr['phone']),
                         ('email', '=', customesr['email'])], limit=1)
                    if len(existing_customer) < 1:
                        self.env['res.partner'].create(vals_customesr)

                        # Get Information Order
                        vals_order = {
                            'woo_order_number': data['number'],
                            'name': data['number'],
                            'woo_order_status': data['status'],
                            'woo_payment_method': data['payment_method_title'],
                            'amount_total': float(data['total']),
                            'date_order': data['date_created'].replace('T',' '),
                            'partner_id': existing_customer.id
                        }

                        #   Check Order In Database
                        existing_orders = self.env['sale.order'].sudo().search(
                            [('woo_order_number', '=', str(data['number']))], limit=1)
                        if len(existing_orders) < 1:
                            new_record = self.env['sale.order'].create(vals_order)
                            if new_record:
                                if "line_items" in data:
                                    vals_product = data["line_items"]
                                    for product in vals_product:
                                        existing_products = self.env['product.template'].sudo().search(
                                            [('woo_product_id', '=', product['product_id'])], limit=1)
                                        if existing_products:
                                            list_product.append({
                                                'product_id': existing_products.product_variant_id.id,
                                                'product_uom_qty': product['quantity'],
                                                'price_unit': float(product['price'])
                                            })
                                            if list_product:
                                                new_record.order_line = [(0, 0, e) for e in list_product]
                                            list_product = []
                        else:
                            existing_orders.sudo().write(vals_order)
                    else:
                        # Get Information Order
                        vals_order = {
                            'woo_order_number': data['number'],
                            'name': data['number'],
                            'woo_order_status': data['status'],
                            'woo_payment_method': data['payment_method_title'],
                            'amount_total': float(data['total']),
                            'date_order': data['date_created'].replace('T', ' '),
                            'partner_id': existing_customer.id

                        }

                        #   Check Order In Database
                        existing_orders = self.env['sale.order'].sudo().search(
                            [('woo_order_number', '=', str(data['number']))], limit=1)
                        if len(existing_orders) < 1:
                            new_record = self.env['sale.order'].create(vals_order)
                            if new_record:
                                if "line_items" in data:
                                    vals_product = data["line_items"]
                                    for product in vals_product:
                                        existing_products = self.env['product.template'].sudo().search(
                                            [('woo_product_id', '=', product['product_id'])], limit=1)
                                        if existing_products:
                                            list_product.append({
                                                'product_id': existing_products.product_variant_id.id,
                                                'product_uom_qty': product['quantity'],
                                                'price_unit': float(product['price'])
                                            })
                                            if list_product:
                                                new_record.order_line = [(0, 0, e) for e in list_product]
                                            list_product = []
                        else:
                            existing_orders.sudo().write(vals_order)
            else:
                raise ValidationError(_('Sync List Order From Woocommerce Fail.'))
        except Exception as e:
            raise ValidationError(str(e))