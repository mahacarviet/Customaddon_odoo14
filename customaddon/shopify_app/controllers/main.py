from odoo import http
from odoo.http import request
import werkzeug
import shopify
from .auth import ShopifySession, XeroSession, XeroAuth
from ..models.decorator import ensure_login
from profilehooks import profile
from datetime import datetime, timedelta, date
from urllib.parse import urlencode
import logging
import traceback
import json
_logger = logging.getLogger(__name__)


class MainController(http.Controller):

    # @check_connect
    @http.route('/index', auth='public', type='http', csrf=False)
    def index(self, **kw):
        try:
            sale_accounts = []
            payment_accounts = []
            shipping_accounts = []
            shopify_session = ShopifySession()
            shopify_store = shopify_session.get_shopify_store()
            shop_url = shopify_session.get_shop_url()
            xero_session = XeroSession()
            xero_auth = xero_session.get_xero_auth()
            organisation_name = xero_auth.get_tenants()[0]['tenantName']
            xero = xero_session.get_xero_connector()
            accounts = xero.accounts.filter(Status='ACTIVE')
            for account in accounts:
                if account['Type'] in ['SALES', 'REVENUE']:
                    sale_accounts.append({
                        'name': account['Code'] + ' - ' + account['Name'],
                        'code': account['Code'],
                    })
                    shipping_accounts.append({
                        'name': account['Code'] + ' - ' + account['Name'],
                        'code': account['Code'],
                    })
                if account['Type'] == 'BANK' or account['EnablePaymentsToAccount']:
                    payment_accounts.append({
                        'name': account['Code'] + ' - ' + account['Name'],
                        'code': account['Code'],
                    })
            if not shopify_store.sale_account:
                shopify_store.sale_account = sale_accounts[0]['code']
            if not shopify_store.shipping_account:
                shopify_store.shipping_account = shipping_accounts[0]['code']
            if not shopify_store.payment_account:
                shopify_store.payment_account = payment_accounts[0]['code']
            if not shopify_store.auto_sync:
                shopify_store.auto_sync = True
            plans = request.env['app.plan'].sudo().search([])
            logs = request.env['app.log'].sudo().search([('shopify_store', '=', shopify_store.id)], limit=10, order='create_date desc')
            message = request.params.get('message')
            shopify_store_dict = {
                "sale_account": shopify_store.sale_account if shopify_store.sale_account else '',
                "shipping_account": shopify_store.shipping_account if shopify_store.shipping_account else '',
                "payment_account": shopify_store.payment_account if shopify_store.payment_account else '',
                "auto_sync": 1 if shopify_store.auto_sync else 0,
                "store_plan_order_number": shopify_store.plan.order_number,
                "store_plan_is_unlimited": 1 if shopify_store.plan.is_unlimited else 0,
                "store_plan_id": shopify_store.plan.id,
                "orders_synced": shopify_store.orders_synced,
                "timezone": shopify_store.timezone if shopify_store.timezone else '',
            }
            plans_list = []
            for plan in plans:
                plan_dict = {
                    "plan_id": plan.id,
                    "plan_name": plan.name,
                    "plan_interval_number": plan.interval_number,
                    "plan_cost": plan.cost,
                    "plan_order_number": plan.order_number,
                }
                plans_list.append(plan_dict)
            log_list = []
            for log in logs:
                log_vals = [
                    shopify_store.convert_to_shop_timezone(log.execution_time).strftime("%Y-%m-%d %H:%M:%S") if log.execution_time else '',
                    shopify_store.convert_to_shop_timezone(log.finish_time).strftime("%Y-%m-%d %H:%M:%S") if log.execution_time else '',
                    log.status,
                    log.message,
                ]
                log_list.append(log_vals)
            context = {
                'shop_url': shop_url,
                # 'shopify_store': shopify_store,
                'shopify_store': shopify_store_dict,
                # 'accounts': accounts,
                'sale_accounts': sale_accounts,
                'shipping_accounts': shipping_accounts,
                'payment_accounts': payment_accounts,
                'plans': plans_list,
                'logs': log_list,
                'organisation_name': organisation_name,
                'message': message,
            }
            return request.render('shopify_app.index', context)
        except Exception as e:
            _logger.error(traceback.format_exc())
            return werkzeug.utils.redirect('/reset')

    @http.route('/reset', auth='public', type='http', csrf=False)
    def reset(self, **kw):
        try:
            xero_session = XeroSession()
            shopify_session = ShopifySession()
            url = redirect_admin_app_page()
            xero_session.reset()
            shopify_session.reset()
            # request.session.pop('shopify_xero', None)
            # request.session.pop('xero', None)
        except Exception as e:
            _logger.error(traceback.format_exc())
        return request.render('shopify_app.redirect_top', {
            'redirect_url': url
        })

    @http.route('/save_settings', auth='public', type='http', csrf=False)
    def save_settings(self, **kw):
        try:
            ensure_login()
            shopify_session = ShopifySession()
            shopify_store = shopify_session.get_shopify_store()
            sale_account = shopify_store.sale_account
            if 'sale_account' in kw:
                sale_account = kw['sale_account']
            shipping_account = shopify_store.shipping_account
            if 'shipping_account' in kw:
                shipping_account = kw['shipping_account']
            payment_account = shopify_store.payment_account
            if 'payment_account' in kw:
                payment_account = kw['payment_account']
            auto_sync = False
            if 'auto_sync' in kw:
                if kw['auto_sync']:
                    auto_sync = True

            vals = {
                'sale_account': sale_account,
                'shipping_account': shipping_account,
                'payment_account': payment_account,
                'auto_sync': auto_sync,
            }
            shopify_store.sudo().write(vals)
            message = 'Settings was saved'
        except Exception as e:
            _logger.error(traceback.format_exc())
            message = 'Save Settings Error: please contact to Admin to get infomation'
        return werkzeug.utils.redirect('/index?' + urlencode({'message': message}))

    @profile(immediate=True)
    @http.route('/sync_to_xero', auth='public', type='http', csrf=False)
    def sync_to_xero(self, **kw):
        try:
            import pytz  # $ pip install pytz
            ensure_login()
            shopify_session = ShopifySession()
            shopify_store = shopify_session.get_shopify_store()
            account = shopify_store.check_account()
            if not account:
                return werkzeug.utils.redirect('/index?' + urlencode({'message': 'Please save your settings.'}))
            from_date, to_date = self.get_date_params(kw=kw)
            date_valid = self.is_date_valid(from_date,to_date)
            if not date_valid:
                return werkzeug.utils.redirect('/index?' + urlencode({'message': 'Invalid Date.'}))
            else:
                log = {'shopify_store': shopify_store.id,}
                try:
                    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    from_date ,to_date = self.convert_date_format(from_date=from_date,to_date=to_date)
                    shopify_store.add_filter('updated_at_min', from_date)
                    shopify_store.add_filter('updated_at_max', to_date)
                    shopify_store.sync_data()
                    finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log['execution_time'] = execution_time
                    log['finish_time'] = finish_time
                    log['status'] = "Success"
                    log['message'] = "Ok"
                    request.env['app.log'].sudo().create(log)
                except Exception as e:
                    log['status'] = "Failed"
                    log['message'] = "Error: " + str(e)
                    log['stack_trace'] = traceback.format_exc()
                    request.env['app.log'].sudo().create(log)
                message = 'Synd data successfully'
        except Exception as e:
            _logger.error(traceback.format_exc())
            message = 'Save Settings Error: please contact to Admin to get infomation'
        return werkzeug.utils.redirect('/index?' + urlencode({'message': message}))
        # return request.render('shopify_app.redirect_top', {
        #     'redirect_url': str(redirect_admin_app_page()) + '?' + urlencode({'message': message})
        # })

    @http.route('/disconnect', auth='public', type='http', csrf=False)
    def disconnect_xero(self, **kw):
        try:
            ensure_login()
            xero_session = XeroSession()
            xero_session.reset()
            request.session.pop('xero', None)
        except Exception as e:
            _logger.error(traceback.format_exc())
        return werkzeug.utils.redirect('/shopify')

    @http.route('/sign_up/<int:plan_id>', auth='public', type='http', csrf=False)
    def sign_up_plan(self, plan_id, **kw):
        try:
            ensure_login()
            ShopifySession()
            plan = request.env['app.plan'].sudo().search([('id', '=', plan_id)])
            if plan:
                plan_data = {
                        "name": plan.name,
                        'price': plan.cost,
                        "return_url": request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/approve',
                        "test": True
                    }
                shop_new_plan = shopify.RecurringApplicationCharge.create(plan_data)
                return werkzeug.utils.redirect(shop_new_plan.confirmation_url)
        except Exception as e:
            _logger.error(traceback.format_exc())
            return werkzeug.utils.redirect('/index?' + urlencode({'message': str(e)}))

            # return request.render('shopify_app.redirect_top', {
            #     'redirect_url': redirect_admin_app_page() + '?' + urlencode({'message': str(e)})
            # })

    @http.route('/approve', auth='public', type='http', csrf=False)
    def approve(self, **kw):
        try:
            ensure_login()
            shopify_session = ShopifySession()
            shopify_store = shopify_session.get_shopify_store()
            charge = shopify.RecurringApplicationCharge.find(kw['charge_id'])
            shopify.RecurringApplicationCharge.activate(charge)
            plan_id = request.env['app.plan'].sudo().search([('name', 'like', charge.name),('cost', '=', charge.price)], limit=1).id
            if plan_id:
                shopify_store.sudo().write({
                    'plan': plan_id,
                    'charge_id': charge.id,
                })
                return request.render('shopify_app.redirect_top', {
                    'redirect_url': str(redirect_admin_app_page()) + '?' + urlencode({'message': 'You have successfully subscribed to a new plan.'})
                })
        except Exception as e:
            _logger.error(traceback.format_exc())
            return request.render('shopify_app.redirect_top', {
                'redirect_url': str(redirect_admin_app_page()) + '?' + urlencode({'message': str(e)})
            })

    def get_date_params(self, kw):
        from_date = ''
        to_date = ''
        if 'from_date' in kw:
            from_date = kw['from_date']
        if 'to_date' in kw:
            to_date = kw['to_date']
        return from_date, to_date

    def is_date_valid(self,from_date,to_date):
        date_format = "%m/%d/%Y"
        a = datetime.strptime(from_date, date_format)
        b = datetime.strptime(to_date, date_format)
        delta = b - a
        if delta.days < 0:
            return False
        else:
            return True

    def convert_date_format(self, from_date, to_date):
        date_format = "%m/%d/%Y"
        from_date = datetime.strptime(from_date, date_format)
        from_date = from_date.strftime('%Y-%m-%d')
        to_date = datetime.strptime(to_date, date_format)
        # add 1 more day to to_date for call api
        to_date += timedelta(days=1)
        to_date = to_date.strftime('%Y-%m-%d')
        return from_date,to_date

def redirect_admin_app_page(shop_url=None):
    if not shop_url:
        shop_url = ShopifySession().get_shop_url()
    if shop_url:
        api_key = request.env['ir.config_parameter'].sudo().get_param('shopify_xero.shopify_api_key')
        url = 'https://%s/admin/apps/%s' % (shop_url, api_key)
        return url
