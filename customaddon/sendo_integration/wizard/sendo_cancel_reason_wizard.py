# -*- coding: utf-8 -*-

import requests
import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SendoCancelReasonWizard(models.TransientModel):
    _name = 'sendo.cancel.reason.wizard'
    _description = 'Get Sendo Cancel Reason'

    sendo_cancel_reason_wizard_id = fields.Many2one('sendo.cancel.reason', string='Cancel Reason')

    sendo_order_status = fields.Selection([
        ('3', 'Đang xử lý'),
        ('7', 'Đã giao hàng'),
        ('13', 'Hủy')], string='Sendo Order Status')
    sale_order_sendo_cancel_reason_id = fields.Many2one('sale.order', string='Quotation ID')

    #   Get Sendo Cancel Reason Order

    def update_order_status_from_odoo_to_sendo(self):
        if self.sendo_order_status == '13':

            try:
                current_seller = self.env['sendo.seller'].sudo().search([])[0]
                url = "https://open.sendo.vn/api/partner/salesorder"

                payload = json.dumps({
                    "order_number": str(self.sale_order_sendo_cancel_reason_id.sendo_order_number),
                    "order_status": int(self.sendo_order_status),
                    "cancel_order_reason": str(self.sendo_cancel_reason_wizard_id.sendo_cancel_code)
                })
                headers = {
                    'cache-control': 'no-cache',
                    'Authorization': 'Bearer ' + current_seller.token_connection,
                    'Content-Type': 'application/json'
                }

                response = requests.request("PUT", url, headers=headers, data=payload)
                update_order_status = response.json()

                if "exp" in response.json():
                    raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
                elif update_order_status["success"]:
                    existed_name_sendo_cancel_reason = self.env['sendo.cancel.reason'].search(
                        [('sendo_cancel_code', '=', self.sendo_cancel_reason_wizard_id.sendo_cancel_code)], limit=1)
                    val = {
                        'sendo_cancel_name': str(existed_name_sendo_cancel_reason.sendo_cancel_name),
                        'sendo_order_status': str(self.sendo_order_status)
                    }
                    existed_sendo_cancel_reason = self.env['sale.order'].search(
                        [('sendo_order_number', '=', str(self.sale_order_sendo_cancel_reason_id.sendo_order_number))],
                        limit=1)
                    if len(existed_sendo_cancel_reason) < 1:
                        self.env['sale.order'].create(val)
                    else:
                        existed_sendo_cancel_reason.write(val)
                else:
                    raise ValidationError(_(update_order_status['error']['message']))
            except Exception as e:
                raise ValidationError(str(e))
        elif (self.sendo_order_status == '3') or (self.sendo_order_status == '7'):
            try:
                current_seller = self.env['sendo.seller'].sudo().search([])[0]
                url = "https://open.sendo.vn/api/partner/salesorder"

                payload = json.dumps({
                    "order_number": str(self.sale_order_sendo_cancel_reason_id.sendo_order_number),
                    "order_status": int(self.sendo_order_status),
                    "cancel_order_reason": None
                })
                headers = {
                    'cache-control': 'no-cache',
                    'Authorization': 'Bearer ' + current_seller.token_connection,
                    'Content-Type': 'application/json'
                }

                response = requests.request("PUT", url, headers=headers, data=payload)
                update_order_status = response.json()

                if "exp" in response.json():
                    raise ValidationError(_('My Token is expired, Please connect Sendo API.'))
                elif update_order_status["success"]:
                    val = {
                        'sendo_order_status': str(self.sendo_order_status)
                    }
                    existed_sendo_cancel_reason = self.env['sale.order'].search(
                        [('sendo_order_number', '=', str(self.sale_order_sendo_cancel_reason_id.sendo_order_number))],
                        limit=1)
                    if len(existed_sendo_cancel_reason) < 1:
                        self.env['sale.order'].create(val)
                    else:
                        existed_sendo_cancel_reason.write(val)
                else:
                    raise ValidationError(_(update_order_status['error']['message']))
            except Exception as e:
                raise ValidationError(str(e))
        else:
            raise ValidationError(_('Order Is Updated If Only It Is In Status PROCESSING Or DELIVERED Or CANCEL'))
