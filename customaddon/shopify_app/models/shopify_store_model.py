from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
import calendar
import maya
import logging
from profilehooks import profile
import requests
import json
import traceback
from ..controllers.auth import ShopifySession, XeroSession
import shopify
from .xero_sync_models import XeroContact, XeroProduct, XeroOrder
_logger = logging.getLogger(__name__)


class ShopifyStore(models.Model):
    _name = 'shopify.store'
    _description = 'Shopify Store'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'shopify_url'

    def _default_plan(self):
        return self.env['app.plan'].search([('cost', '=', 0)], limit=1).id

    shopify_token = fields.Char(string="Shopify Token", index=True)
    shopify_url = fields.Char(string="Shopify URL", index=True)
    xero_token = fields.Text(string="Xero Token")
    orders_synced = fields.Integer(string="Orders Synced This Month", default=0)
    charge_id = fields.Char(string="Shopify Charge ID")

    sale_account = fields.Char(string="Xero Sale Account")
    shipping_account = fields.Char(string="Xero Shipping Account")
    payment_account = fields.Char(string="Xero Payment Account")
    auto_sync = fields.Boolean(string='Automatically Sync', index=True)
    plan = fields.Many2one('app.plan',string='Current Plan', default=_default_plan)
    timezone = fields.Char('Shopify Store Time Zone')
    xero_session = None
    shopify_session = None
    filters = {}

    def add_filter(self, field, value):
        if type(field) == dict:
            for k,v in field.items():
                self.filters[k] = v
        else:
            self.filters[field] = value

    def has_filter(self):
        return self.filters is not None

    def sync_to_xero_cron(self):
        _logger.info('Start Sync data to Xero')
        shops = self.search([('auto_sync', '=', True), ('xero_token','!=', False),('shopify_token','!=', False)])
        for shop in shops:
            shop._init_access()  # creat shopifysession xerosession
            shop.shopify_session.check_access(raise_exception_on_failure=True)
            last_sync = self.env['app.log'].sudo().search([('shopify_store', '=',shop.id),('execution_time', '!=', False)],order='execution_time desc', limit=1).execution_time
            if not last_sync:
                last_sync = shop.get_now_shop_timezone()
            else:
                last_sync = shop.convert_to_shop_timezone(last_sync)

            interval_number = int(shop.plan.interval_number)
            next_call = (last_sync + timedelta(hours=interval_number))
            now = shop.get_now_shop_timezone()
            if now >= next_call:
            # if now < next_call:  # for test
                log = {'shopify_store': shop.id,
                       'is_cron': True}
                try:
                    has_account = shop.check_account()
                    if not has_account:
                        raise Exception('Accounts is missing')
                    shop._init_access()  # creat shopifysession xerosession
                    shop.shopify_session.check_access(raise_exception_on_failure=True)
                    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    to_date = (last_sync + timedelta(days=1)).strftime('%Y-%m-%d')
                    from_date = last_sync.strftime('%Y-%m-%d')
                    shop.add_filter('updated_at_min', from_date)
                    shop.add_filter('updated_at_max', to_date)
                    shop.sync_data()
                    finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log['execution_time'] = execution_time
                    log['finish_time'] = finish_time
                    log['status'] = "Success"
                    log['message'] = "Ok"
                    self.env['app.log'].sudo().create(log)
                    shop.shopify_session.delete_session()
                except Exception as e:
                    log['status'] = "Failed"
                    log['message'] = "Error: "+ str(e)
                    log['stack_trace'] = traceback.format_exc()
                    self.env['app.log'].sudo().create(log)
                    shop.shopify_session.delete_session()
        _logger.info('Stop Sync data to Xero')

    def sync_data(self):
        self.ensure_one()
        self.sync_contact()
        self.sync_product()
        self.sync_order()

    def sync_contact(self):
        self.ensure_one()
        if self.has_filter():
            XeroContact().add_filter(self.filters)
        XeroContact().sync()

    def sync_product(self):
        self.ensure_one()
        if self.has_filter():
            XeroProduct().add_filter(self.filters)
        XeroProduct().sync()

    def sync_order(self):
        self.ensure_one()
        if self.has_filter():
            XeroOrder().add_filter(self.filters)
        XeroOrder().sync()

    def check_account(self):
        if not self.sale_account or not self.payment_account or not self.shipping_account:
            return False
        else:
            return True

    def check_shop_plan_cron(self):
        _logger.info('Start checking plan Xero Shopify')
        shops = self.search([('shopify_token', '!=', False), ('xero_token', '!=', False)])
        for shop in shops:
            log = {'shopify_store': shop.id,
                   'is_cron': True}
            try:
                shop._init_access() #creat shopifysession xerosession
                shop.shopify_session.check_access(raise_exception_on_failure=True)
                execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                shop.check_current_plan()
                finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log['execution_time'] = execution_time
                log['finish_time'] = finish_time
                log['status'] = "Success"
                log['message'] = "Ok(1)"
                self.env['app.log'].sudo().create(log)
                shop.shopify_session.delete_session()
            except Exception as e:
                log['status'] = "Failed"
                log['message'] = "Error (1): " + str(e)
                log['stack_trace'] = traceback.format_exc()
                self.env['app.log'].sudo().create(log)
                shop.shopify_session.delete_session()
        _logger.info('Stop checking plan Xero Shopify')

    def check_current_plan(self):
        current_plan = shopify.RecurringApplicationCharge.current()
        if not current_plan:
            default_plan_id = self.env['app.plan'].sudo().search([], order='cost asc', limit=1).id
            self.plan = default_plan_id
            self.charge_id = None
            return
        else:
            if self.plan.cost != current_plan.price or not self.plan:
                plan_id = self.env['app.plan'].sudo().search([('cost', '=', current_plan.price)], limit=1).id
                self.plan = plan_id
                self.charge_id = current_plan.id
                return

    def clear_shopify_token(self):
        self.shopify_token = None

    def clear_xero_token(self):
        self.xero_token = None

    def _init_access(self):
        self._init_shopify_access()
        self._init_xero_access()

    def _init_shopify_access(self):
        if not self.shopify_token:
            raise Exception('Shopify Token is missing')
        self.shopify_session = ShopifySession(shop_url=self.shopify_url, token=self.shopify_token, env=self.env)

    def _init_xero_access(self):
        if not self.xero_token:
            raise Exception('Xero Token is missing')
        self.xero_session = XeroSession(token=self.xero_token, env=self.env)

    def convert_to_shop_timezone(self, utc_dt):
        import pytz
        timezone = self.timezone
        return utc_dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(timezone))
        # timezone = self.timezone.split(' ')
        # local_dt = utc_dt.replace().astimezone()
        # return timezone.normalize(local_dt)

    def get_now_shop_timezone(self):
        import pytz
        timezone = self.timezone
        return datetime.now(pytz.timezone(timezone))