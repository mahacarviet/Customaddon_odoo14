from odoo import _, api, fields, models

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Text('Message', readonly=True)

    # @api.multi
    def action_ok(self):
        """ close wizard"""
        # return
        return {'type': 'ir.actions.act_window_close'}