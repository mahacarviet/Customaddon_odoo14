# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import requests
import json
import datetime


class XeroShop(models.Model):
    _name = 'xero.shop'
    _description = 'xero_shop'
    _rec_name = 'shopify_shop_id'

    xero_refresh_token = fields.Char(string='Refresh Token')
    xero_access_token = fields.Char(string='Access Token')
    xero_token_type = fields.Char(string='Token Type')
    xero_id_token = fields.Char(string='Token ID')
    status = fields.Selection([
        ('unconnected', 'Unconnected Xero'),
        ('connected', 'Connected Xero')
    ], string="Status", default="unconnected")
    shop_user_id = fields.Integer()
    xero_tenant_name = fields.Char(string='Tenant Name')
    xero_tenant_id = fields.Char(string='Tenant ID')
    test_datetime = fields.Datetime(string='Date Time', default=datetime.datetime.now())

    xero_app_id = fields.Many2one("xero.app", string='Xero App')
    shopify_shop_id = fields.Many2one("s.shop", string='Shopify Shop')

    # xero_tenant_id_ids = fields.One2many('xero.tenant')

    @api.onchange('shop_user_id')
    def _add_shop_user_id(self):
        search_user = self.env['res.users'].search([('login', '=', self.shopify_shop_id.shop_base_url)], limit=1)
        if search_user:
            self.shop_user_id = int(search_user.id)
        else:
            self.shop_user_id = 0

    def action_connect_shop_xero(self):
        self.status = 'connected'
        self.xero_id_token = self.xero_app_id.xero_id_token
        self.xero_token_type = self.xero_app_id.xero_token_type
        self.xero_access_token = self.xero_app_id.xero_access_token
        self.xero_refresh_token = self.xero_app_id.xero_refresh_token

    def action_disconnect_shop_xero(self):
        self.xero_id_token = ''
        self.xero_token_type = ''
        self.xero_access_token = ''
        self.xero_refresh_token = ''
        self.status = 'unconnected'

    def get_contacts_xero(self):
        try:
            self.xero_app_id.refresh_token_xero()
            search_tenant = self.env['xero.tenant'].sudo().search([])
            if search_tenant:
                for tenant in search_tenant:
                    if tenant.xero_tenant_name and self.xero_tenant_name in ('ilike', '=ilike', 'like', '=like'):
                        self.xero_tenant_id = tenant.xero_id
                        break

            url = "https://api.xero.com/api.xro/2.0/Contacts"

            payload = {}
            headers = {
                'xero-tenant-id': self.xero_tenant_id if self.xero_tenant_id else None,
                'Authorization': 'Bearer ' + self.xero_app_id.xero_access_token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()
            if 'id' in result:
                if len(result['Contacts']) > 0:
                    for contact in result['Contacts']:
                        search_tenant_core = self.env['res.partner'].sudo().search(
                            ['xero_ContactID', '=', contact['ContactID']])
                        vals = {}
                        if search_tenant_core:
                            vals['company_type'] = 'person'
                            vals['name'] = contact['Name']
                            # vals['street'] = contact['ContactID']
                            # vals['street2'] = contact['ContactID']
                            # vals['city'] = contact['ContactID']
                            vals['xero_check_customer'] = True
                            vals['email'] = contact['EmailAddress'] if contact['EmailAddress'] else None
                            vals['xero_ContactID'] = contact['ContactID']
                            self.env['res.partner'].sudo().create(vals)
                        else:
                            search_tenant_core.sudo().write(vals)
            else:
                ValidationError('Error')
        except Exception as e:
            raise ValidationError(str(e))

    def get_invoices_xero(self):
        try:
            self.xero_app_id.refresh_token_xero()
            search_tenant = self.env['xero.tenant'].sudo().search([])
            if search_tenant:
                for tenant in search_tenant:
                    if tenant.xero_tenant_name and self.xero_tenant_name in ('ilike', '=ilike', 'like', '=like'):
                        self.xero_tenant_id = tenant.xero_id
                        break

            url = "https://api.xero.com/api.xro/2.0/Invoices"

            payload = {}
            headers = {
                'xero-tenant-id': self.xero_tenant_id if self.xero_tenant_id else None,
                'Authorization': 'Bearer ' + self.xero_app_id.xero_access_token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            result = response.json()
            if 'id' in result:
                if len(result['Invoices']) > 0:
                    for contact in result['Invoices']:
                        search_tenant_core = self.env['res.partner'].sudo().search(
                            ['xero_ContactID', '=', contact['ContactID']])
                        vals = {}
                        if search_tenant_core:
                            vals['company_type'] = 'person'
                            vals['name'] = contact['Name']
                            # vals['street'] = contact['ContactID']
                            # vals['street2'] = contact['ContactID']
                            # vals['city'] = contact['ContactID']
                            vals['xero_check_customer'] = True
                            vals['email'] = contact['EmailAddress'] if contact['EmailAddress'] else None
                            vals['xero_ContactID'] = contact['ContactID']
                            self.env['res.partner'].sudo().create(vals)
                        else:
                            search_tenant_core.sudo().write(vals)
            else:
                ValidationError('Error')
        except Exception as e:
            raise ValidationError(str(e))


