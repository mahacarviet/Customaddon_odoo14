from odoo import models, fields, api


class TransferCoachWizard(models.TransientModel):
    _name = 'transfer.coach.wizard'

    @api.model
    def _get_old_old_coach_team_club(self):
        player_id = self.env.context.get('active_id', False)
        player = self.env['coach'].browse(player_id)
        return player.coach_team_club.id

    @api.model
    def _get_old_coach_training_center(self):
        player_id = self.env.context.get('active_id', False)
        player = self.env['coach'].browse(player_id)
        return player.coach_training_center.id

    def transfer(self):
        player_id = self.env.context.get('active_id', False)
        player = self.env['coach'].browse(player_id)
        if self.input_option == 'club':
            player.coach_team_club = self.coach_team_club.id
        if self.input_option == 'training_center':
            player.coach_training_center = self.coach_training_center.id

    input_option = fields.Selection([
        ('draft', 'Draft'),
        ('club', 'Club'),
        ('training_center', 'Training Center')],
        string='Club or Training Center Transfer', default='draft')

    coach_team_club = fields.Many2one('team.club', string='Club')
    old_coach_team_club = fields.Many2one('team.club', string='Old Club', default=_get_old_old_coach_team_club)
    coach_training_center = fields.Many2one('training.center', string='Training Center')
    old_coach_training_center = fields.Many2one('training.center', string='Old Club', default=_get_old_coach_training_center)
