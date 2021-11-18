from odoo import api, fields, models, _
import requests
import json
import os
from os import listdir
from odoo.exceptions import UserError, ValidationError


class ProviderAhamove(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('aha_move', 'AhaMove')], ondelete={'aha_move': 'cascade'})
    aha_token = fields.Char(string="AhaMove Token")
    aha_refresh_token = fields.Char(string="AhaMove Refresh Token")

    # def aha_move_rate_shipment(self, order):
    #     try:
    #         carrier = self._match_address(order.partner_shipping_id)
    #
    #         search_token = self.env['delivery.carrier'].sudo().search([('delivery_type', '=', 'aha_move')], limit=1)
    #         if search_token:
    #             if not search_token.aha_token:
    #                 raise ValidationError('Please Get Token From AhaMove To Odoo Before')
    #
    #         address_from = order.warehouse_id.partner_id
    #         address_to = order.partner_id
    #         address_sender = str(address_from.street) + ', ' + str(address_from.city) + ', ' + str(
    #             address_from.state_id.name) + ', ' + str(address_from.country_id.name)
    #         address_receiver = str(address_to.street) + ', ' + str(address_to.city) + ', ' + str(
    #             address_to.state_id.name) + ', ' + str(address_to.country_id.name)
    #
    #         # Get Address of User. That's address of Company
    #         url_1 = 'https://apistg.ahamove.com/v1/order/estimated_fee?token='
    #         # rail = '&service_id=' + ma dich vu + '&requests=[]'
    #         rail = '&service_id=HAN-BIKE&&requests=[]'
    #         # add_sender = '{"address"' + ":" + '"' + self.warehouse_id.partner_id.street + self.order_id. + '"' + '}'
    #         # add_receiver = '{"address"' + ":" + '"' + self.order_id. + '"' + '}'
    #         add_sender = '{"address"' + ":" + '"' + '1 La Thành, Ô Chợ Dừa, Đống Đa, Hà Nội' + '"' + '}'
    #         add_receiver = '{"address"' + ":" + '"' + '170 La Thành, Ô Chợ Dừa, Đống Đa, Hà Nội' + '"' + '}'
    #
    #         # Post Url to get rate
    #         url = url_1 + search_token.aha_token + f'&order_time=0&path=[{add_sender},{add_receiver}]' + rail
    #         payload = {}
    #         headers = {
    #             'cache-control': 'no-cache',
    #             'Accept': '*/*'
    #         }
    #         response = requests.request("GET", url, headers=headers, data=payload)
    #         content = response.json()
    #         if not 'code' in content:
    #             self.display_price = 10000
    #         else:
    #             if ('description' in content) and ('title' in content):
    #                 raise_error = str(content['title']) + "/" + str(content['title'])
    #                 raise ValidationError(raise_error)
    #             if 'description' in content:
    #                 raise ValidationError(content['description'])
    #             if 'title' in content:
    #                 raise ValidationError(content['title'])
    #     except Exception as e:
    #         raise ValidationError(str(e))


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    aha_check_shipping = fields.Boolean(default=False)
    aha_code_shipping = fields.Char()

    # def action_confirm_1(self):
    #     # super(SaleOrderInherit, self).action_confirm()
    #     ahamove_delivery = False
    #     for line in self.order_line:
    #         if line.is_delivery:
    #             ahamove_delivery = True
                # print(self.order_line.recompute_delivery_price)
                # print(self.order_line.qty_delivered)
                # print(self.order_line.qty_delivered_manual)
                # print(self.order_line.qty_to_deliver)
                # print(self.order_line.qty_delivered_method)
        # if ahamove_delivery:

    def aha_move_confirm_order(self, order):
        try:
            carrier = self._match_address(order.partner_shipping_id)

            # Get address of warehouse
            search_address_aha = self.env['sale.order'].search([], limit=1)
            address_warehouse = []
            for name in search_address_aha:
                if name.warehouse_id.partner_id.street:
                    address_warehouse.append(name.warehouse_id.partner_id.street)

            # Get Token Of Delivery Order
            search_token_aha = self.env['delivery.carrier'].search([])
            list_token_aha = []
            for i in search_token_aha:
                if i.carrier_id.token_aha:
                    list_token_aha.append(i.carrier_id.token_aha)

            # Get Address of User. That's address of Company
            header = 'https://apistg.ahamove.com/v1/order/create?token='
            # rail = '&service_id=' + ma dich vu + '&requests=[]&payment_method=CASH'
            rail = '&service_id=HAN-BIKE&&requests=[]&payment_method=CASH'
            token = list_token_aha[-1]
            # add_sender = '{"address"' + ":" + '"' + address_warehouse[0] + '"' + '}'
            # add_receiver = '{"address"' + ":" + '"' + order.partner_shipping_id.street + '"' + '}'
            add_sender = '{"address"' + ":" + '"' + '1 La Thành, Ô Chợ Dừa, Đống Đa, Hà Nội' + '"' + '}'
            add_receiver = '{"address"' + ":" + '"' + '170 La Thành, Ô Chợ Dừa, Đống Đa, Hà Nội' + '"' + '}'

            # Post Url to get rate
            url = header + token + f'&order_time=0&path=[{add_sender},{add_receiver}]' + rail
            res = requests.post(url)
            content = res.json()
            load_json_response = json.loads(res.text)
            print('json.loads(res.text)', json.loads(res.text))
            if res.status_code == 200:
                self.display_price = float(load_json_response['order']['total_pay'])
            else:
                raise ValidationError(content['description'])

        except Exception as e:
            raise ValidationError(str(e))


class ChooseDeliveryCarrierInherit(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    def update_price(self):
        if self.carrier_id.delivery_type == 'aha_move':
            try:
                search_token = self.env['delivery.carrier'].sudo().search([('delivery_type', '=', 'aha_move')], limit=1)
                if search_token:
                    if not search_token.aha_token:
                        raise ValidationError('Please Get Token From AhaMove To Odoo Before')
                address_from = self.order_id.warehouse_id.partner_id
                address_to = self.order_id.partner_id
                address_sender = str(address_from.street) + ', ' + str(address_from.city) + ', ' + str(
                    address_from.state_id.name) + ', ' + str(address_from.country_id.name)
                address_receiver = str(address_to.street) + ', ' + str(address_to.city) + ', ' + str(
                    address_to.state_id.name) + ', ' + str(address_to.country_id.name)

                # Get Address of User. That's address of Company
                url_1 = 'https://apistg.ahamove.com/v1/order/estimated_fee?token='
                # rail = '&service_id=' + ma dich vu + '&requests=[]'
                rail = '&service_id=HAN-BIKE&&requests=[]'
                # add_sender = '{"address"' + ":" + '"' + self.warehouse_id.partner_id.street + self.order_id. + '"' + '}'
                # add_receiver = '{"address"' + ":" + '"' + self.order_id. + '"' + '}'
                add_sender = '{"address"' + ":" + '"' + '1 La Thành, Ô Chợ Dừa, Đống Đa, Hà Nội' + '"' + '}'
                add_receiver = '{"address"' + ":" + '"' + '170 La Thành, Ô Chợ Dừa, Đống Đa, Hà Nội' + '"' + '}'

                # Post Url to get rate
                url = url_1 + search_token.aha_token + f'&order_time=0&path=[{add_sender},{add_receiver}]' + rail
                payload = {}
                headers = {
                    'cache-control': 'no-cache',
                    'Accept': '*/*'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                content = response.json()
                if not 'code' in content:
                    self.delivery_price = float(content['total_price'])
                    self.display_price = float(content['total_price'])
                else:
                    if ('description' in content) and ('title' in content):
                        raise_error = str(content['title']) + "/" + str(content['title'])
                        raise ValidationError(raise_error)
                    if 'description' in content:
                        raise ValidationError(content['description'])
                    if 'title' in content:
                        raise ValidationError(content['title'])
                return {
                    'name': _('Add a shipping method'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'choose.delivery.carrier',
                    'res_id': self.id,
                    'target': 'new',
                }
            except Exception as e:
                raise ValidationError(str(e))
        else:
            vals = self._get_shipment_rate()
            if vals.get('error_message'):
                raise UserError(vals.get('error_message'))
            return {
                'name': _('Add a shipping method'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'choose.delivery.carrier',
                'res_id': self.id,
                'target': 'new',
            }



