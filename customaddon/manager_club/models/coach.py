from odoo import models, fields, api
from datetime import *
from odoo.exceptions import UserError, ValidationError


class Coach(models.Model):
    _name = 'coach'

    name = fields.Char(string='Name', required=1)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    address = fields.Text(string='Address')
    date_of_birth = fields.Date(required=1)
    phone_number = fields.Char(string='Phone Number')
    nation = fields.Char(string='Nation', required=1)
    coaching_licence = fields.Selection([
        ('licence_a', 'UEFA A Licence'),
        ('licence_b', 'UEFA B Licence'),
        ('licence_c', 'UEFA C Licence'),
        ('licence_pro', 'UEFA Pro Licence')],
        string='UEFA Coaching Licence', default='licence_a')
    salary = fields.Integer(string='Salary', store='True')
    tax_salary = fields.Integer(string='Tax Salary', compute='_compute_tax', store='True')
    status = fields.Selection([
        ('free', 'Free'),
        ('in_club', 'In Club')],
        string='Status', compute='_compute_status')

    coach_team_club = fields.Many2many('team.club')
    coach_training_center = fields.Many2many('training.center')

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth < date.today():
                temp = (date.today() - rec.date_of_birth).days
                rec.age = temp // 365

    @api.constrains('age')
    def check_age(self):
        for rec in self:
            if rec.age <= 0:
                raise ValidationError(
                    'Date of birth need to be smaller today.',
                )

    @api.constrains('salary')
    def check_age(self):
        for rec in self:
            if rec.salary < 0:
                raise ValidationError(
                    'Salary need to be greater than 0.',
                )

    @api.depends('salary')
    def _compute_tax(self):
        for rec in self:
            if rec.salary > 15000000:
                rec.tax_salary = 0.1 * rec.salary
            else:
                rec.tax_salary = 0

    @api.depends('coach_team_club', 'coach_training_center')
    def _compute_status(self):
        for rec in self:
            if rec.coach_team_club or rec.coach_training_center:
                rec.status = 'in_club'
            else:
                rec.status = 'free'
