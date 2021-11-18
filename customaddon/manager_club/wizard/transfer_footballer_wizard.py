from odoo import models, fields, api


class TransferFootballerWizard(models.TransientModel):
    _name = 'transfer.footballer.wizard'

    @api.model
    def _get_old_club_id(self):
        player_id = self.env.context.get('active_id', False)
        player = self.env['footballer'].browse(player_id)
        return player.club_id.id

    club_id = fields.Many2one('team.club', string='Club')
    old_club_id = fields.Many2one('team.club', string='Old Club', default=_get_old_club_id)

    def transfer(self):
        player_id = self.env.context.get('active_id', False)
        player = self.env['footballer'].browse(player_id)
        player.club_id = self.club_id.id
