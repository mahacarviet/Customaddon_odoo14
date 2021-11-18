import requests
from odoo import fields, models, api
from odoo.http import request


class SellerConnectWizard(models.TransientModel):
    _name = 's.fetch.information'
    _description = 'Fetch Product, Order In Shopify'

    secret = fields.Char(string='Connection parameters')
    user_agent = fields.Selection([
        ('chrome', 'Chrome'),
        ('edge', 'Edge'),
        ('firefox', 'Firefox')], string='User Agent')






