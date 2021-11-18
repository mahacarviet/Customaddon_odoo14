from odoo import models, fields, api
from datetime import *
from odoo.exceptions import UserError, ValidationError


class Footballer(models.Model):
    _name = 'footballer'
    _inherit = ['ir.needaction_mixin']

    name = fields.Char(string='Name', required=1)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    address = fields.Text(string='Address')
    date_of_birth = fields.Date(required=1)
    nation = fields.Char(string='Nation', required=1)
    phone_number = fields.Char(string='Phone Number')
    salary = fields.Float(string='Salary', store='True')
    tax_salary = fields.Float(string='Tax Salary', compute='_compute_tax', store='True')
    status = fields.Selection([
        ('free', 'Free'),
        ('in_club', 'In Club')],
        string='Status', compute='_compute_status')

    club_id = fields.Many2one(comodel_name='team.club', string='Club')
    training_center_ids = fields.Many2many(comodel_name='training.center', string='Training Center')

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
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

    @api.depends('club_id')
    def _compute_status(self):
        for rec in self:
            if rec.club_id:
                rec.status = 'in_club'
            else:
                rec.status = 'free'

    @api.model
    def create(self, vals):
        name = vals.get('name', False)
        if name:
            vals['name'] = name.title()
        record = super(Footballer, self).create(vals)
        return record

    # @api.model
    # def _needaction_domain_get(self):
    #     return False
    #
    # @api.model
    # def _needaction_count(self, domain=None):
    #     return self.search_count(domain)
