from odoo import api, fields, models, _
import requests
import json
from odoo.exceptions import UserError, ValidationError


class ResWard(models.Model):
    _name = 'res.ward'
    _description = 'Res Ward'
    _order = 'state_id'

    name = fields.Char("Name", required=True, translate=True)
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', 'State', domain="[('country_id', '=', country_id)]")
    district_id = fields.Many2one('res.district', 'District', domain="[('state_id', '=', state_id)]")
    ghn_ward_id = fields.Char("GHN Ward Code", help='Mã phường/xã theo Giao hàng Nhanh')

    def get_district_id(self):
        search_district = self.env['res.district'].sudo().search([])
        for id in search_district:
            if id.ghn_district_id:
                self.create_ward_data(id.ghn_district_id)

    def create_ward_data(self, district_id):
        try:
            request_url = "https://online-gateway.ghn.vn/shiip/public-api/master-data/ward?district_id=" + str(
                district_id)
            ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
            headers = {
                'Content-type': 'application/json',
                'Token': ghn_token
            }
            req = requests.get(request_url, headers=headers)
            # req.raise_for_status()
            content = req.json()
            if content['code'] == 200:
                data = content['data']
                if data:
                    for rec in data:
                        if 'WardCode' in rec:
                            existed_district = self.env['res.district'].sudo().search(
                                [('ghn_district_id', '=', rec['DistrictID'])], limit=1)
                            if existed_district:
                                vals = {}
                                vals['state_id'] = existed_district.state_id.id
                                vals['country_id'] = existed_district.country_id.id
                                vals['district_id'] = existed_district.id
                                vals['name'] = rec['WardName']
                                vals['ghn_ward_id'] = rec['WardCode']

                                existed_ghn_ward = self.env['res.ward'].sudo().search(
                                    [('ghn_ward_id', '=', rec['WardCode'])], limit=1)
                                if existed_ghn_ward:
                                    existed_ghn_ward.sudo().write(vals)
                                else:
                                    self.env['res.ward'].sudo().create(vals)

                        search_ward = self.env['res.ward'].sudo().search([('name', 'ilike', 'Test')], limit=1)
                        if search_ward:
                            search_ward.unlink()
            else:
                raise ValidationError(_(content['code_message_value']))
        except Exception as e:
            raise ValidationError(str(e))
