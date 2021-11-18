from odoo import api, fields, models, _

class AppPlan(models.Model):
    _name = 'app.plan'
    _description = 'Application Plans'

    name = fields.Char(string='Name')
    order_number = fields.Integer(string='Order Number')
    interval_number = fields.Char(string='Interval Number')
    sync_giftcard = fields.Boolean(string='Sync Gift Card')
    sync_refund = fields.Boolean(string='Sync Refund Order')
    is_unlimited = fields.Boolean(string='Is Unlimited')
    cost = fields.Float(string='Plan Cost')
