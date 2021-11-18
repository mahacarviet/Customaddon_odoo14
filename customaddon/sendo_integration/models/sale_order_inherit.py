import requests
import json
from datetime import *
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    check_sendo_customer = fields.Boolean(store=True)


#       Class Inherit Sale Order
class ApiSendoSaleOrderInherit(models.Model):
    _inherit = "sale.order"

    sendo_order_number = fields.Char()
    sendo_order_status = fields.Selection([
        ('2', 'Mới'),
        ('3', 'Đang xử lý'),
        ('6', 'Đang vận chuyển'),
        ('7', 'Đã giao hàng'),
        ('8', 'Đã hoàn tất'),
        ('10', 'Đóng'),
        ('11', 'Yêu cầu hoãn'),
        ('12', 'Đang hoãn'),
        ('13', 'Hủy'),
        ('14', 'Yêu cầu tách'),
        ('15', 'Chờ tách'),
        ('19', 'Chờ gộp'),
        ('21', 'Đang đổi trả'),
        ('22', 'Đổi trả thành công'),
        ('23', 'Chờ Sendo xử lý')], string='Order Status')
    sendo_payment_status = fields.Selection([
        ('1', 'Chưa thanh toán'),
        ('2', 'Đã thanh toán COD'),
        ('3', 'Đã thanh toán'),
        ('4', 'Hoàn tất'),
        ('5', 'Đã hoàn tiền'),
        ('6', 'Đợi xác nhận'),
        ('7', 'Từ chối'),
        ('14', 'Đã thanh toán một phần'),
        ('15', 'Đã hoàn tiền một phần')], string='Payment Status')
    sendo_payment_method = fields.Selection([
        ('1', 'Thanh toán khi nhận hàng'),
        ('2', 'Thanh toán trực tuyến'),
        ('4', 'Thanh toán kết hợp'),
        ('5', 'Thanh toán trả sau')], string='Payment Method')
    sendo_cancel_name = fields.Char(string='Cancel Reason')

    def action_return_information_sendo_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Company',
            'view_mode': 'form',
            'res_model': 'sendo.cancel.reason.wizard',
            'target': 'new',
            'context': {
                'default_sale_order_sendo_cancel_reason_id': self.id,
            }
        }

    #       Sync Database for Sendo Order to Sale Order
    def get_list_order_sendo_to_product_template(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]
            if current_seller.sendo_order_date_from:
                if (current_seller.sendo_order_date_from + timedelta(days=300)) < date.today():
                    current_seller.sendo_order_date_to = current_seller.sendo_order_date_from + timedelta(days=300)
                else:
                    current_seller.sendo_order_date_to = date.today()
            else:
                current_seller.sendo_order_date_from = current_seller.date_startup
                if (current_seller.sendo_order_date_from + timedelta(days=300)) < date.today():
                    current_seller.sendo_order_date_to = current_seller.sendo_order_date_from + timedelta(days=300)
                else:
                    current_seller.sendo_order_date_to = date.today()

            url = "https://open.sendo.vn/api/partner/salesorder/search"
            payload = json.dumps({
                "page_size": 50,
                "order_status": None,
                "order_date_from": current_seller.sendo_order_date_from.strftime("%Y-%m-%d"),
                "order_date_to": current_seller.sendo_order_date_to.strftime("%Y-%m-%d"),
                "order_status_date_from": None,
                "order_status_date_to": None,
                "token": None
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            seller_products = response.json()
            if "exp" in response.json():
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif seller_products["success"]:
                current_seller.sendo_order_date_from = current_seller.sendo_order_date_to
                list_order = seller_products["result"]["data"]

                val = {}
                list_product = []
                val_customer = {}
                for rec in list_order:
                    if 'sales_order' in rec:
                        val_order = rec['sales_order']

                        #   Get Information Customer
                        val_customer['name'] = val_order['receiver_name']
                        val_customer['phone'] = val_order['buyer_phone']
                        val_customer['mobile'] = str(val_order['buyer_phone'])
                        val_customer['email'] = val_order['receiver_email']
                        val_customer['company_type'] = 'person'
                        val_customer['type'] = 'contact'
                        val_customer['street'] = val_order['receiver_full_address']
                        val_customer['comment'] = 'Sync By Call Sendo API'
                        val_customer['check_sendo_customer'] = True

                        #   Check Customer
                        existed_customer = self.env['res.partner'].sudo().search(
                            ['&', ('phone', '=', str(val_order['buyer_phone'])),
                             ('street', '=', val_order['receiver_full_address'])], limit=1)
                        if len(existed_customer) < 1:
                            self.env['res.partner'].create(val_customer)
                            get_customer = self.env['res.partner'].sudo().search(
                                ['&', ('phone', '=', str(val_order['buyer_phone'])),
                                 ('street', '=', val_order['receiver_full_address'])], limit=1)

                            # Get Information Order
                            val['sendo_order_number'] = str(val_order['order_number'])
                            val['name'] = str(val_order['order_number'])
                            val['sendo_order_status'] = str(val_order['order_status'])
                            val['sendo_payment_status'] = str(val_order['payment_status'])
                            val['sendo_payment_method'] = str(val_order['payment_method'])
                            val['amount_total'] = val_order['total_amount']
                            val['amount_untaxed'] = val_order['sub_total']
                            val['date_order'] = datetime.fromtimestamp(val_order['order_date_time_stamp'])
                            val['partner_id'] = get_customer.id

                            #   Check Order In Database
                            existed_order = self.env['sale.order'].sudo().search(
                                [('sendo_order_number', '=', str(val_order['order_number']))], limit=1)
                            if len(existed_order) < 1:
                                new_record = self.env['sale.order'].create(val)
                                if new_record:
                                    if 'sku_details' in rec:
                                        val_product = rec['sku_details']
                                        for product in val_product:
                                            existed_product_sendo = self.env['product.template'].sudo().search(
                                                [('sendo_product_id', '=', product['product_variant_id'])], limit=1)
                                            if existed_product_sendo:
                                                list_product.append({
                                                    'product_id': existed_product_sendo.product_variant_id.id,
                                                    'product_uom_qty': product['quantity'],
                                                    'price_unit': product['price']
                                                })
                                                if list_product:
                                                    new_record.order_line = [(0, 0, e) for e in list_product]
                                                list_product = []
                            else:
                                existed_order.sudo().write(val)
                        else:
                            # Get Information Order
                            val['sendo_order_number'] = str(val_order['order_number'])
                            val['name'] = str(val_order['order_number'])
                            val['sendo_order_status'] = str(val_order['order_status'])
                            val['sendo_payment_status'] = str(val_order['payment_status'])
                            val['sendo_payment_method'] = str(val_order['payment_method'])
                            val['amount_total'] = val_order['total_amount']
                            val['amount_untaxed'] = val_order['sub_total']
                            val['date_order'] = datetime.fromtimestamp(val_order['order_date_time_stamp'])
                            val['partner_id'] = existed_customer.id
                            val_customer['check_sendo_customer'] = True

                            #   Check Order In Database
                            existed_order = self.env['sale.order'].sudo().search(
                                [('sendo_order_number', '=', str(val_order['order_number']))], limit=1)
                            if len(existed_order) < 1:
                                new_record = self.env['sale.order'].create(val)
                                if new_record:
                                    if 'sku_details' in rec:
                                        val_product = rec['sku_details']
                                        for product in val_product:
                                            existed_product_sendo = self.env['product.template'].sudo().search(
                                                [('sendo_product_id', '=', product['product_variant_id'])], limit=1)
                                            if existed_product_sendo:
                                                list_product.append({
                                                    'product_id': existed_product_sendo.product_variant_id.id,
                                                    'product_uom_qty': product['quantity'],
                                                    'price_unit': product['price']
                                                })
                                                if list_product:
                                                    new_record.order_line = [(0, 0, e) for e in list_product]
                                                list_product = []
                            else:
                                existed_order.sudo().write(val)

            else:
                raise ValidationError(_('Sync List Order From Sendo Fail.'))
        except Exception as e:
            raise ValidationError(str(e))


class SendoCancelReason(models.Model):
    _name = "sendo.cancel.reason"
    _description = "Sendo Cancel Reason Queue"
    _rec_name = 'sendo_cancel_name'

    sendo_cancel_code = fields.Char(string='Code')
    sendo_cancel_name = fields.Char(string='Name')

    #   Get Cancel Reason Collection

    def get_cancel_reason_collection(self):
        try:
            current_seller = self.env['sendo.seller'].sudo().search([])[0]
            url = "https://open.sendo.vn/api/partner/salesorder/reason-collection"

            payload = {}
            headers = {
                'Authorization': 'Bearer ' + current_seller.token_connection
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result_cancel_sendo = response.json()

            if "exp" in result_cancel_sendo:
                raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
            elif result_cancel_sendo["success"]:
                list_reason = result_cancel_sendo["result"]

                val = {}
                for reason in list_reason:
                    if 'code' in reason:
                        val['sendo_cancel_code'] = reason['code']
                        val['sendo_cancel_name'] = reason['name']
                        existed_cancel_sendo = self.env['sendo.cancel.reason'].search(
                            [('sendo_cancel_code', '=', reason['code'])], limit=1)
                        if len(existed_cancel_sendo) < 1:
                            self.env['sendo.cancel.reason'].create(val)
                        else:
                            existed_cancel_sendo.write(val)

        except Exception as e:
            raise ValidationError(str(e))
