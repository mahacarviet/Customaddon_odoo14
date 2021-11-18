from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import *


class TrainingCenter(models.Model):
    _name = 'training.center'

    name = fields.Char(string='Name Training Center', required=1)
    address = fields.Char(string='Address', required=1)
    year_established = fields.Date(string='Year Established', required=1)
    state = fields.Selection(
        selection=[('process', 'Processing'), ('dissolution', 'Dissolution')],
        string='Status', default='process')

    training_center_ids = fields.Many2many(comodel_name='footballer', string='List Footballer')
    training_center_coach = fields.Many2many('coach')

    @api.model
    def create(self, vals):
        name = vals.get('name', False)
        if name:
            vals['name'] = name.title()
        record = super(TrainingCenter, self).create(vals)
        return record

    def process_training_center(self):
        if self.state == 'draft':
            self.state = 'process'
        elif self.state == 'process':
            self.state = 'draft'

    @api.constrains('year_established')
    def check_age(self):
        for rec in self:
            if rec.year_established >= date.today():
                raise ValidationError(
                    'Year established need to be smaller today.',
                )
