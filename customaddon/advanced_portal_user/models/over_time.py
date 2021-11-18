# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class OverTime(models.Model):
    _name = 'hr.over.time'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'New model for sign over time'
    _rec_name = 'employee_id'

    user_id = fields.Many2one('res.users')
    employee_id = fields.Many2one('hr.employee')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('refused', 'Refused')], 'Status', default="draft")
    description = fields.Text('Description')

    user_is_approver = fields.Boolean(default=False, compute='_check_user_is_approver')
    time_from = fields.Datetime(string='Time From')
    time_to = fields.Datetime(string='Time To')
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
        message = self.env.user.name + ' ' + 'approved the overtime request of ' + self.employee_id.name
        self.message_post(body=message, subject='Over Time Approving',
                          message_type='notification',
                          subtype_xmlid='mail.mt_comment',
                          approved_ids=self.user_id.id)

    def refused_action(self):
        self.state = 'refused'
        message = self.env.user.name + ' ' + 'refused the overtime request of ' + self.employee_id.name
        self.message_post(body=message, subject='Over Time Refusing',
                          message_type='notification',
                          subtype_xmlid='mail.mt_comment',
                          approved_ids=self.user_id.id)
