from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import *


class TeamClub(models.Model):
    _name = 'team.club'

    name = fields.Char(string='Name', required=1)
    year_established = fields.Date(string='Year Established', required=1)
    address = fields.Char(string='Address')
    state = fields.Selection(
        selection=[('process', 'Processing'), ('dissolution', 'Dissolution')],
        string='Status', default='process')
    sum_footballer = fields.Integer(compute='_compute_count_footballer', string='Members', store=True)

    footballer_ids = fields.One2many(comodel_name='footballer', inverse_name='club_id', string='Footballer')
    team_club_coach = fields.Many2many('coach')

    @api.model
    def create(self, vals):
        name = vals.get('name', False)
        if name:
            vals['name'] = name.title()
        record = super(TeamClub, self).create(vals)
        return record

    def process_club(self):
        if self.state == 'draft':
            self.state = 'process'
        elif self.state == 'process':
            self.state = 'draft'

    @api.depends('footballer_ids')
    def _compute_count_footballer(self):
        for rec in self:
            rec.sum_footballer = len(rec.footballer_ids)

    @api.constrains('year_established')
    def check_age(self):
        for rec in self:
            if rec.year_established >= date.today():
                raise ValidationError(
                    'Year established need to be smaller today.',
                )
