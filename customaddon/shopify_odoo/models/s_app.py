# -*- coding: utf-8 -*-
from odoo import models, fields, api
import hashlib
import json
import requests
import calendar
import time


class SApp(models.Model):
    _name = 's.app'
    _description = 's_app'
    _rec_name = 'app_name'

    api_key = fields.Char()
    secret_key = fields.Char()
    api_version = fields.Char()
    app_name = fields.Char()
    link_script_tag = fields.Char(default="https://odoo.website/shopify_odoo/static/src/js/main.js")

    def change_script_tag(self):
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        for rec in self:
            rec.link_script_tag = "https://odoo.website/shopify_odoo/static/src/js/main.js?v=" + str(int(ts))
