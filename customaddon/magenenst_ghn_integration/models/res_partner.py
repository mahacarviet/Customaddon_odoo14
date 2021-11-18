from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    district_id = fields.Many2one('res.district', string='District', domain="[('state_id', '=', state_id)]")
    ward_id = fields.Many2one('res.ward', string='Ward', domain="[('district_id', '=', district_id)]")

    @api.onchange('district_id')
    def onchange_district_id(self):
        self.city = self.district_id.name
