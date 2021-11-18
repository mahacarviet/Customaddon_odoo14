from odoo import api, fields, models, _
import requests
import json
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_id = fields.Many2one(related="group_id.sale_id", string="Sales Order", store=True, readonly=False)
    ghn_order_status = fields.Char('GHN order status', readonly=True, help='Trạng thái đơn hàng của Giao hàng nhanh.')
    ghn_order_code = fields.Char('GHN Order Code', related='sale_id.ghn_order_code', store=True)
    ghn_leadtime = fields.Date('GHN Ngày giao dự kiến', readonly=True)

    def action_cancel(self):
        super(StockPicking, self).action_cancel()
        self.ghn_cancel_order()
        return True

    def check_ghn_order_status(self):
        pickings = self.env['stock.picking'].search([('state', 'not in', ['draft', 'done', 'cancel'])])
        for picking in pickings:
            if picking.ghn_order_code:
                order_info = picking.ghn_order_info(picking.ghn_order_code)
                if 'leadtime' in order_info['data']:
                    leadtime = order_info['data']['leadtime']
                    if leadtime:
                        picking.ghn_leadtime = leadtime
                if 'status' in order_info['data']:
                    status = order_info['data']['status']
                    # status = 'delivered'
                    if status:
                        picking.ghn_order_status = status
                    if status == 'delivered':
                        is_availability = picking.action_assign()
                        if is_availability:
                            for move_line in picking.move_line_ids:
                                move_line.qty_done = move_line.product_uom_qty
                        else:
                            raise UserError(_('Số lượng trong kho không đủ đáp ứng.'))
                        picking.button_validate()

    def check_single_ghn_order_status(self):
        if self.state not in ['draft', 'done', 'cancel']:
            if self.ghn_order_code:
                order_info = self.ghn_order_info(self.ghn_order_code)
                if 'leadtime' in order_info['data']:
                    leadtime = order_info['data']['leadtime']
                    if leadtime:
                        self.ghn_leadtime = leadtime
                # if 'log' in order_info['data']:
                #     logs = order_info['data']['log']
                #     if logs:
                #         for log in logs:
                #             status = 'GHN Status: ' + log['status'].upper() +'<br>'
                #             message_body = status + 'Updated_date: ' + log['updated_date']
                #             self.message_post(body=message_body)
                if 'status' in order_info['data']:
                    status = order_info['data']['status']
                    # status = 'delivered'
                    if status:
                        self.ghn_order_status = status
                    if status == 'delivered':
                        is_availability = self.action_assign()
                        if is_availability:
                            for move_line in self.move_line_ids:
                                move_line.qty_done = move_line.product_uom_qty
                        else:
                            raise UserError(_('Số lượng trong kho không đủ đáp ứng.'))
                        self.button_validate()

    def ghn_order_info(self, order_code):
        try:
            request_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/detail"
            headers = {
                'Content-type': 'application/json',
                'Token': self.env['ir.config_parameter'].sudo().get_param('ghn_token'),
            }

            data = {
                "order_code": order_code,
            }
            req = requests.post(request_url, data=json.dumps(data), headers=headers)
            # req.raise_for_status()
            content = req.json()
            if content['code'] == 200:
                return content
            else:
                raise ValidationError(_(content['code_message_value']))
        except Exception as e:
            raise ValidationError(str(e))

    def ghn_cancel_order(self):
        try:
            request_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/switch-status/cancel"
            ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
            ghn_shop_id = self.sale_id.warehouse_id.ghn_shop_id
            if ghn_shop_id and ghn_token:
                headers = {
                    'Content-type': 'application/json',
                    'Token': ghn_token,
                    'ShopId': ghn_shop_id
                }
            else:
                raise UserError(_('Vui lòng kiểm tra lại thông tin token hoặc ship_id'))

            data = {
                "order_codes": [self.sale_id.ghn_order_code],
            }
            req = requests.post(request_url, data=json.dumps(data), headers=headers)
            # req.raise_for_status()
            content = req.json()
            if content['code'] == 200:
                return content
            else:
                raise ValidationError(_(content['code_message_value']))
        except Exception as e:
            raise ValidationError(str(e))

# class StockMoveLine(models.Model):
#     _inherit = 'stock.move.line'

# def auto_set_qty_done(self):
#     product = self.env['product.product'].browse(self.product_id.id)
#     available_qty = product.qty_available
#     if self.product_uom_qty > available_qty:
#         raise UserError(_('Số lượng trong kho không đủ đáp ứng.'))
#     else:
#         self.qty_done = self.product_uom_qty
