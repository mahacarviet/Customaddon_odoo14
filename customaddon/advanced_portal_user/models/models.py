# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api


class AdvancedPortal(models.Model):
    _inherit = 'res.users'
    _description = 'Add check Portal User'

    employee_related = fields.Many2one('hr.employee', 'Employee Related')


class UserEmployeeAttendance(models.Model):
    _inherit = 'hr.attendance'

    user_id = fields.Many2one(string='User', comodel_name='res.users')
