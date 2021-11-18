# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AttendanceExplanation(models.Model):
    _inherit = 'hr.attendance'
    _description = 'Attendance Explanation'

    explanation = fields.Text('Explanation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('refused', 'Refused')], 'Status')
    user_is_approver = fields.Boolean(default=False, compute='_check_user_is_approver')
    approver = fields.Many2one('res.users', 'Approver')

    def _check_user_is_approver(self):
        for rec in self:
            if self.env.user.id == rec.approver.id:
                rec.user_is_approver = True
            elif self.env.user.id == 2:
                rec.user_is_approver = True
            else:
                rec.user_is_approver = False

    def approved_action(self):
        self.state = 'approved'

    def refused_action(self):
        self.state = 'refused'
