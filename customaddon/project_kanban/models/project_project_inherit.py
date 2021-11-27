# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    stage_id = fields.Many2one('project.stage.test', store=True)
    stage_note = fields.Char(related='stage_id.stage_note', store=True)
    # project_follower_ids = fields.Many2many('res.partner', store=True)

    # def write(self, vals):
    #     res = super(ProjectProjectInherit, self).write(vals)
    #     if vals['message_follower_ids']:
    #         print(1111)
    #         for person in vals['message_follower_ids']:
    #             print(2222)
    #             if person.partner_id:
    #                 print(3333)
    #                 vals['project_follower_ids'] = [(4, person.partner_id.id)]
    #     return res


# class MailFollowersInherit(models.Model):
#     _inherit = 'mail.followers'
    # @api.constrains('project_follower_ids')
    # def _compute_link_followers(self):
    #     if self.message_follower_ids:
    #         print(1111)
    #         for person in self.message_follower_ids:
    #             print(2222)
    #             if person.partner_id:
    #                 print(3333)
    #                 self.project_follower_ids = [(4, person.partner_id.id)]

    # def unlink(self):
    #     for adyen_payout_id in self:
    #         adyen_payout_id.adyen_account_id._adyen_rpc('close_payout', {
    #             'accountCode': adyen_payout_id.code,
    #         })
    #     return super(MailFollowersInherit, self).unlink()

    # for order in self:
    #     if order.state not in ('draft', 'cancel'):
    #         raise UserError(
    #             _('You can not delete a sent quotation or a confirmed sales order. You must first cancel it.'))
    # return super(SaleOrder, self).unlink()

    # def create(self, vals):
    #     res = super(MailFollowersInherit, self).create(vals)
    #     if vals['message_follower_ids']:
    #         print(1111)
    #         for person in vals['message_follower_ids']:
    #             print(2222)
    #             if person.partner_id:
    #                 print(3333)
    #                 vals['project_follower_ids'] = [(4, person.partner_id.id)]
    #     return res