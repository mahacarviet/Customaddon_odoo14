# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json


class SShop(models.Model):
    _name = 's.shop'
    _description = 's_shop'
    _rec_name = 'shop_owner'

    shop_base_url = fields.Char()
    shop_owner = fields.Char()
    shop_user = fields.Char()
    shop_password = fields.Char()
    shop_currency = fields.Char()
    shop_user_id = fields.Integer()

    shop_app_ids = fields.Many2many('s.app', string='App Shopify')
    shopify_shop_product_temp = fields.One2many('product.template', 'shopify_shop_id')

    @api.onchange('shop_user_id')
    def _add_shop_user_id(self):
        for rec in self:
            rec.shop_user_id = self.env.uid
