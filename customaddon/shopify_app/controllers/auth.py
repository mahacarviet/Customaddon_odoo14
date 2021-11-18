import os
import shopify
import json
from xero.auth import OAuth2Credentials
from xero.constants import XeroScopes
from odoo.http import request
from odoo.http import root
import logging
import traceback
_logger = logging.getLogger(__name__)


local_session = None
local_env = None

class AuthSession:
    data = {}

    def __init__(self, env=None):
        global local_env
        if env is not None:
            local_env = env

    def _set_data(self, key, value):
        self.data[key] = value
        self._save_session()

    def _get_data(self, key=None):
        if key is None:
            return self.data
        else:
            return self.data[key]

    def _clear_data(self, key=None):
        if key is None:
            self.data = None
        else:
            self.data[key] = None
        self._save_session()

    def _save_session(self):
        root.session_store.save(self._get_main_session())

    def _get_main_session(self):
        if request and hasattr(request, 'session'):
            session = request.session
        else:
            # create new session
            global local_session
            local_session = root.session_store.new()
            session = local_session
        return session

    def delete_session(self):
        root.session_store.delete(self._get_main_session())

    def get_env(self):
        global local_env
        if local_env is None and request and hasattr(request, 'env'):
            local_env = request.env
        if hasattr(local_env, 'cr') and local_env.cr.closed == True:
            local_env = request.env
        return local_env


class ShopifySession(AuthSession):
    shopify_store = None
    session = None

    def __init__(self, shop_url=None, token=None, *args, **kwargs):
        super(ShopifySession, self).__init__(*args, **kwargs)
        session = self._get_main_session()
        if 'shopify_xero' not in session:
            session['shopify_xero'] = {}
        self.data = session['shopify_xero']
        if shop_url is not None:
            self._set_data('shop_url', shop_url)
        if token is not None:
            self._set_data('token', token)
        self.session = ShopifyAuth(self._get_data('shop_url'), token=self._get_data('token'), env=self.get_env())
        shopify.ShopifyResource.activate_session(self.session)

    def get_shopify_store(self):
        if self.shopify_store is None:
            shop_url = self._get_data('shop_url')
            env = self.get_env()
            self.shopify_store = env['shopify.store'].sudo().search([('shopify_url', '=', shop_url)], limit=1)
        return self.shopify_store

    def get_session(self):
        return self.session

    def get_shop_url(self):
        return self._get_data('shop_url')

    def reset(self):
        shopify.Shop.clear_session()
        self.get_shopify_store().clear_shopify_token()
        self._clear_data()

    def check_access(self, raise_exception_on_failure=False):
        try:
            # ShopifySession()
            shopify.Shop.current()
            return True
        except Exception as e:
            self.reset()
            if raise_exception_on_failure:
                raise e
            else:
                return False

    def set_shopify_store_timezone(self):
        # if not self._get_data('timezone'):
        shop = shopify.Shop.current()
        # self.get_shopify_store().sudo().write({'timezone': shop.attributes['timezone']})
        self._set_data('timezone', shop.attributes['timezone'])
        return self._get_data('timezone')

class ShopifyAuth(shopify.Session):

    def __init__(self, shop_url, env, version=None, token=None):
        if version is None:
            version = env['ir.config_parameter'].sudo().get_param('shopify_xero.shopify_api_version')
        super(ShopifyAuth, self).__init__(shop_url, version, token)
        api_key = env['ir.config_parameter'].sudo().get_param('shopify_xero.shopify_api_key')
        shared_secret = env['ir.config_parameter'].sudo().get_param('shopify_xero.shopify_shared_secret')
        shopify.Session.setup(api_key=api_key, secret=shared_secret)


class XeroSession(AuthSession):

    def __init__(self, token=None, *args, **kwargs):
        super(XeroSession, self).__init__(*args, **kwargs)
        session = self._get_main_session()
        if 'xero' not in session:
            session['xero'] = {}
        self.data = session['xero']
        if token is not None:
            self.set_token(token)

    def get_xero_auth(self):
        token = self.get_token()
        auth = XeroAuth(token=token)
        try:                           # mb for invalid_grant
            if auth.expired():
                self.reload_token_from_db()
                if self._get_data('token'):
                    auth = XeroAuth(token=self.get_token())
                auth.refresh()
                self.set_token(auth.token)
                self.save_token_to_db()
            if not auth.tenant_id:
                auth.set_default_tenant()
        except Exception as e:
            shopify_session = ShopifySession()
            _logger.error('There was an error connecting to Xero. Shop url: %s' % shopify_session.get_shopify_store().shopify_url)
            self.reset()
            raise e
        return auth

    def get_xero_connector(self):
        from ..models.xero_connector import XeroConnect
        xero_auth = self.get_xero_auth()
        return XeroConnect(xero_auth)

    def save_token_to_db(self):
        shopify_session = ShopifySession()
        shopify_store = shopify_session.get_shopify_store()
        shopify_store.xero_token = json.dumps(self.get_token())

    def reload_token_from_db(self):
        shopify_session = ShopifySession()
        shopify_store = shopify_session.get_shopify_store()
        self.set_token(shopify_store.xero_token)

    def get_token(self):
        token = self._get_data('token')
        if type(token) == str:
            self.set_token(token)
        return self._get_data('token')

    def set_token(self, token):
        if type(token) == str:
            token = json.loads(token)
        self._set_data('token', token)

    def reset(self):
        shopify_session = ShopifySession()
        shopify_session.get_shopify_store().clear_xero_token()
        self._clear_data()


class XeroAuth(OAuth2Credentials):

    def __init__(
            self,
            client_id=None,
            client_secret=None,
            callback_uri=None,
            auth_state=None,
            auth_secret=None,
            token=None,
            scope=None,
            tenant_id=None,
            user_agent=None,
    ):
        from xero import __version__ as VERSION
        xero_session = XeroSession()
        env = xero_session.get_env()
        if client_id is None:
            client_id = env['ir.config_parameter'].sudo().get_param('shopify_xero.xero_client_id')
        if client_secret is None:
            client_secret = env['ir.config_parameter'].sudo().get_param('shopify_xero.xero_client_secret')
        if callback_uri is None:
            callback_uri = env['ir.config_parameter'].sudo().get_param('web.base.url') + '/xero/callback'
        if scope is None:
            scope = "email accounting.contacts.read accounting.settings accounting.contacts accounting.transactions.read profile accounting.settings.read openid offline_access accounting.transactions"
        super(XeroAuth, self).__init__(
            client_id,
            client_secret,
            callback_uri,
            auth_state,
            auth_secret,
            token,
            scope,
            tenant_id,
            user_agent
        )

    def verify(self, *args, **kwargs):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        super(XeroAuth, self).verify(*args, **kwargs)
        os.environ.pop('OAUTHLIB_INSECURE_TRANSPORT')
