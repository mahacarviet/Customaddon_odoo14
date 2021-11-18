# -*- coding: utf-8 -*-

from odoo import fields, models


class ApplicationReject(models.TransientModel):
    _name = 'application.reject'
    _description = 'Lựa chọn lý do từ chối'

    reject_reason_id = fields.Many2one(
        'application.reject.reason',
        string="Lý do",
        help="Lựa chọn lý do từ chối đơn đăng ký học.")

    def action_reject_reason_apply(self):
        """Write the reject reason of the application"""
        for rec in self:
            application = self.env['education.application'].browse(
                self.env.context.get('active_ids'))
            application.write({'reject_reason': rec.reject_reason_id.id})
            return application.reject_application()


class ApplicationRejectReason(models.Model):
    _name = 'application.reject.reason'
    _description = 'Lý do từ chối'

    name = fields.Char(string="Lý do", required=True,
                       help="Lý do từ chối đơn đăng ký học.")
