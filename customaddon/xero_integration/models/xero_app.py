# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import hashlib
import json
import requests
import calendar
import time
import base64


class XeroApp(models.Model):
    _name = 'xero.app'
    _description = 'xero_app'
    _rec_name = 'xero_app_name'

    xero_app_name = fields.Char(string='App Name')
    xero_client_id = fields.Char(string='Client ID')
    xero_client_secret = fields.Char(string='Client Secret')
    xero_redirect_url = fields.Char(string='Redirect URL')
    xero_scopes = fields.Char(string='Scopes')
    xero_state = fields.Char(default='123', string='State')
    xero_refresh_token = fields.Char(string='Refresh Token')
    xero_access_token = fields.Char(string='Access Token')
    xero_token_type = fields.Char(string='Token Type')
    xero_id_token = fields.Char(string='Token ID')
    status = fields.Selection([
        ('unconnected', 'Unconnected Xero'),
        ('connected', 'Connected Xero')
    ], string="Status", default="unconnected")

    xero_app_tenant_ids = fields.One2many('xero.tenant', 'xero_app_tenant')

    def action_connect_xero(self):
        return {
            'type': 'ir.actions.act_url',
            'url': 'http://localhost:8069/xero_connect',
            'target': 'new'
        }

    def refresh_token_xero(self):
        try:
            url = 'https://identity.xero.com/connect/token'
            data = self.xero_client_id + ":" + self.xero_client_secret
            encodedBytes = base64.b64encode(data.encode("utf-8"))
            encodedStr = str(encodedBytes, "utf-8")
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': "Basic " + encodedStr
            }
            data_token = {
                'grant_type': 'refresh_token',
                'token': self.xero_refresh_token
            }
            response = requests.post(url, data=data_token, headers=headers, verify=False)
            result = response.json()
            if 'id_token' in result:
                self.xero_refresh_token = result['refresh_token']
                self.xero_access_token = result['access_token']
                self.xero_token_type = result['token_type']
                self.xero_id_token = result['id_token']
        except Exception as e:
            raise ValidationError(str(e))

    def revoking_token_xero(self):
        try:
            url = 'https://identity.xero.com/connect/token'
            data = self.xero_client_id + ":" + self.xero_client_secret
            encodedBytes = base64.b64encode(data.encode("utf-8"))
            encodedStr = str(encodedBytes, "utf-8")
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': "Basic " + encodedStr
            }
            payload = {
                'token': self.xero_refresh_token
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            result = response.json()
            if result:
                self.xero_refresh_token = ''
                self.xero_access_token = ''
                self.xero_token_type = ''
                self.xero_id_token = ''
                self.status = 'unconnected'

            search_shop = self.env['xero.shop'].search([('xero_app_id', '=', self.id)])
            if search_shop:
                for shop in search_shop:
                    shop.xero_refresh_token = ''
                    shop.xero_access_token = ''
                    shop.xero_token_type = ''
                    shop.xero_id_token = ''
                    shop.status = 'unconnected'

        except Exception as e:
            raise ValidationError(str(e))


class XeroTenant(models.Model):
    _name = 'xero.tenant'
    _description = 'xero_tenant'
    _rec_name = 'xero_tenant_name'

    xero_id = fields.Char(string='Xero ID')
    xero_auth_event_id = fields.Char(string='Auth Event ID')
    xero_tenant_type = fields.Char(string='Tenant Type')
    xero_tenant_name = fields.Char(string='Tenant Name')

    xero_app_tenant = fields.Many2one('xero.app', string='App')
