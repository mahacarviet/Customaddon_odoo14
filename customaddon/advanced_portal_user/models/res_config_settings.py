from odoo import fields, models, api


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    has_setting_portal = fields.Boolean("Setting Time Check Portal", store=True)
    portal_time_in = fields.Char(string='Time In', config_parameter='advanced_portal_user.time_in')
    portal_time_out = fields.Char(string='Time Out', config_parameter='advanced_portal_user.time_out')