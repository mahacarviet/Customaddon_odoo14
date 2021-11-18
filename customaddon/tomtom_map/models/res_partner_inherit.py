# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    _description = 'tomtom_map.tomtom_map'

    calculate_route_ids = fields.One2many('result.tomtom.map', 'result_tomtom_map_res_partner', string='Appointment')

    def action_return_information_address(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Map Integration Odoo',
            'view_mode': 'form',
            'res_model': 'calculate.route.wizard',
            'target': 'new',
            'context': {
                'default_calculate_route_res_partner_id': self.id,
                'default_tomtom_starting_point': self.street + ", " + self.city + ", " + self.state_id.name + ", " + self.country_id.name,
            }
        }
