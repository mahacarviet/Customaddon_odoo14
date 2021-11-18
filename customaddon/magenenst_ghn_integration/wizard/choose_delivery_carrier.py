# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json

PHI_KHAI_GIA = 3000000  # GIAO HANG NHANH: khai gia tren 3.000.000  se tinh them phi khai gia
GHN_MAX_INSURANCE_FEE = 10000000  # GIAO HANG NHANH: gia tri hang hoa khong qua 10.000.000


class ChooseDeliveryCarrier(models.TransientModel):
    # _name = 'choose.delivery.carrier.inherit'
    _inherit = 'choose.delivery.carrier'

    weight = fields.Integer('Khối lượng(gram)', required=True, default=3, help='Tổng khối lượng sản phẩm')
    length = fields.Integer('Chiều dài(cm)', required=True, default=10)
    width = fields.Integer('Chiều rộng(cm)', required=True, default=10)
    height = fields.Integer('Chiều cao(cm)', required=True, default=10)
    required_note = fields.Selection([
        ('KHONGCHOXEMHANG', 'Không cho xem hàng'),
        ('CHOXEMHANGKHONGTHU', 'Cho xem không cho thử'),
        ('CHOTHUHANG', 'Cho thử hàng')
    ], string="Lưu ý giao hàng", default="KHONGCHOXEMHANG", required=True)
    payment_type = fields.Selection([
        ('1', 'Bên gửi trả phí'),
        ('2', 'Bên nhận trả phí'),
    ], string="Tùy chọn thanh toán", default="2", required=True)

    convert_volume = fields.Integer('Khối lượng quy đổi', required=True, default=0,
                                    help='Là khối lượng được tính dựa theo công thức (DxRxC/5000)')

    def product_sale_ok_amount_total(self):
        amount_total = 0
        for line in self.order_id.order_line:
            if line.product_id.product_tmpl_id.sale_ok:
                amount_total = amount_total + line.price_subtotal
        return amount_total

    @api.onchange('weight', 'length', 'width', 'height', 'carrier_id')
    def onchange_weight(self):

        # Check Information Parcels
        if self.weight <= 0:
            raise UserError(_('Khối lượng gói hàng phải lớn hơn 0.'))
        if self.weight > 1500000:
            raise UserError(_('Khối lượng gói hàng tối đa 1500kg.'))
        if self.length > 200:
            raise UserError(_('Chiều dài của đơn hàng tối đa 200cm.'))
        if self.width > 200:
            raise UserError(_('Chiều rộng của đơn hàng tối đa 200cm.'))
        if self.height > 200:
            raise UserError(_('Chiều cao của đơn hàng tối đa 200cm.'))
        if self.carrier_id.service:
            self.convert_volume = (self.height * self.width * self.length) / 5000
            available_service = self.ghn_available_service()
            match_service = False
            if 'data' in available_service:
                for data in available_service['data']:
                    if data['service_type_id'] == int(self.carrier_id.service):
                        match_service = True
            if match_service:
                calculate_fee = self.ghn_calculate_fee()
                if 'data' in calculate_fee:
                    if 'total' in calculate_fee['data']:
                        ghn_fee = calculate_fee['data']['total']
                        if ghn_fee:
                            amount_total = self.product_sale_ok_amount_total()
                            if amount_total > PHI_KHAI_GIA:
                                self.display_price = ghn_fee + (amount_total / 100) * 0.5
                            else:
                                self.display_price = ghn_fee
                        else:
                            self.display_price = ghn_fee
            else:
                raise UserError(
                    _('Phương thức vận chuyển này hiện chưa hỗ trợ cho địa điểm nhận hàng, Vui lòng chọn phương thức vận chuyển khác.'))
            self.order_id.write({
                'weight': self.weight,
                'length': self.length,
                'width': self.width,
                'height': self.height,
                'convert_volume': self.convert_volume,
            })

    def button_confirm(self):
        if self.weight <= 0:
            raise UserError(_('Khối lượng gói hàng phải lớn hơn 0.'))
        if self.weight and self.height and self.length and self.width:
            if not self.height and not self.length and not self.width:
                raise UserError(_('Vui lòng nhập đầy đủ thông tin kích thước hoặc khối lượng gói hàng.'))
            if self.carrier_id.service:
                calculate_fee = self.ghn_calculate_fee()
                ghn_fee = calculate_fee['data']['total']
                if ghn_fee:
                    # if 'insurance_fee' in calculate_fee['data']:
                    #     if calculate_fee['data']['insurance_fee'] > 0:
                    #         # service_fee = self.order_service_fee()
                    #         # reward_amount = self.order_reward_amount()
                    #         # amount_total = self.order_id.amount_total - service_fee + abs(reward_amount)
                    #         amount_total = self.calculate_final_amount_total()
                    amount_total = self.product_sale_ok_amount_total()
                    if amount_total > PHI_KHAI_GIA:
                        ghn_fee = ghn_fee + (amount_total / 100) * 0.5
                    self.order_id.set_delivery_line(self.carrier_id, ghn_fee)
                    self.order_id.write({
                        'recompute_delivery_price': False,
                        'delivery_message': self.delivery_message,
                        'required_note': self.required_note,
                        'payment_type': self.payment_type
                    })
            else:
                self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
                self.order_id.write({
                    'recompute_delivery_price': False,
                    'delivery_message': self.delivery_message,
                })
        else:
            self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
            self.order_id.write({
                'recompute_delivery_price': False,
                'delivery_message': self.delivery_message,
            })

    def ghn_available_service(self):
        try:
            request_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/available-services"
            ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
            if ghn_token:
                headers = {
                    'Content-type': 'application/json',
                    'Token': ghn_token,
                }
            else:
                raise UserError(_('Vui lòng kiểm tra lại thông tin token'))
            ghn_shop_id = self.order_id.warehouse_id.ghn_shop_id
            if not ghn_shop_id:
                raise UserError(_('Vui lòng kiểm tra lại thông tin ship_id'))
            from_district_id = self.order_id.warehouse_id.partner_id.district_id.ghn_district_id
            to_district_id = self.order_id.partner_shipping_id.district_id.ghn_district_id
            if from_district_id and to_district_id:
                data = {
                    "shop_id": int(ghn_shop_id),
                    "from_district": from_district_id,
                    "to_district": to_district_id
                }
            else:
                raise UserError(_('Vui lòng kiểm tra lại thông tin địa chỉ(Quận/Huyện) của bên gửi hàng/nhận hàng'))
            req = requests.post(request_url, data=json.dumps(data), headers=headers)
            # req.raise_for_status()
            content = req.json()
            if content['code'] == 200:
                if 'insurance_fee' in data:
                    content['data']['insurance_fee'] = data['insurance_fee']
                return content
            else:
                raise ValidationError(_(content['code_message_value']))
        except Exception as e:
            raise ValidationError(str(e))

    def ghn_calculate_fee(self):
        try:
            request_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee"
            ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
            if ghn_token:
                headers = {
                    'Content-type': 'application/json',
                    'Token': ghn_token,
                }
            else:
                raise UserError(_('Không tìm thấy giá trị token, Vui lòng kiểm tra lại'))
            if not self.height and not self.length and not self.width:
                raise UserError(_('Vui lòng nhập đầy đủ thông tin kích thước hoặc khối lượng gói hàng.'))

            from_district_id = self.order_id.warehouse_id.partner_id.district_id.ghn_district_id
            from_ward_id = self.order_id.warehouse_id.partner_id.ward_id.ghn_ward_id
            if not from_district_id and not from_ward_id:
                raise UserError(_('Vui lòng kiểm tra lại thông tin địa chỉ(quận/huyện, phường/xã) nhà kho .'))

            service_type_id = int(self.carrier_id.service)
            if not service_type_id:
                raise UserError(_('Vui lòng chọn kiểu vận chuyển.'))

            to_district_id = self.order_id.partner_shipping_id.district_id.ghn_district_id
            to_ward_code = self.order_id.partner_shipping_id.ward_id.ghn_ward_id
            if not to_district_id and not to_ward_code:
                raise UserError(_('Vui lòng kiểm tra lại thông tin địa chỉ(quận/huyện, phường/xã) khách hàng.'))
            if not self.required_note:
                raise UserError(_('Thông tin Lưu ý giao hàng là yêu cầu bắt buộc'))
            if not self.payment_type:
                raise UserError(_('Tùy chọn thanh toán là thông tin bắt buộc'))

            amount_total = self.product_sale_ok_amount_total()  # is total price of product's sale_ok

            if amount_total > GHN_MAX_INSURANCE_FEE:
                raise UserError(_('Chính sách của Giao hàng nhanh chỉ cho phép giá trị đơn hàng tối đa 10.000.000 đồng.'))

            data = {
                "from_district_id": from_district_id,
                "from_ward_id": from_ward_id,
                "service_type_id": service_type_id,
                "to_district_id": to_district_id,
                "to_ward_code": to_ward_code,
                "height": self.height,
                "length": self.length,
                "weight": self.weight,
                "width": self.width,
                "insurance_fee": int(amount_total),
                "coupon": None
            }
            req = requests.post(request_url, data=json.dumps(data), headers=headers)
            # req.raise_for_status()
            content = req.json()
            if content['code'] == 200:
                if 'insurance_fee' in data:
                    content['data']['insurance_fee'] = data['insurance_fee']
                return content
            else:
                raise ValidationError(_(content['code_message_value']))
        except Exception as e:
            raise ValidationError(str(e))

    # def order_service_fee(self):
    #     service_fee = 0.0
    #     for line in self.order_id.order_line:
    #         if line.is_delivery:
    #             service_fee = service_fee + line.price_subtotal
    #     return service_fee
    #
    # def order_reward_amount(self):
    #     reward_amount = 0.0
    #     for line in self.order_id.order_line:
    #         if line.is_reward_line:
    #             reward_amount = reward_amount + line.price_subtotal
    #     return reward_amount
