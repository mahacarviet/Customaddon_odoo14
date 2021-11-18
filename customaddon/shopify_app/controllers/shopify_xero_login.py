from odoo import http
from odoo.http import request, Response
from werkzeug.http import dump_cookie
from odoo.service import security
import shopify
import werkzeug
import json
from ..models.decorator import check_xero_login, check_shopify_login
from .auth import ShopifyAuth, ShopifySession, XeroSession, XeroAuth
from .main import redirect_admin_app_page
import logging
import traceback
_logger = logging.getLogger(__name__)

class Root(http.Root):
    def get_response(self, httprequest, result, explicit_session):
        if isinstance(result, Response) and result.is_qweb:
            try:
                result.flatten()
            except Exception as e:
                if request.db:
                    result = request.registry['ir.http']._handle_exception(e)
                else:
                    raise

        if isinstance(result, (bytes, str)):
            response = Response(result, mimetype='text/html')
        else:
            response = result

        save_session = (not request.endpoint) or request.endpoint.routing.get('save_session', True)
        if not save_session:
            return response

        if httprequest.session.should_save:
            if httprequest.session.rotate:
                self.session_store.delete(httprequest.session)
                httprequest.session.sid = self.session_store.generate_key()
                if httprequest.session.uid:
                    httprequest.session.session_token = security.compute_session_token(httprequest.session, request.env)
                httprequest.session.modified = True
            self.session_store.save(httprequest.session)
        # We must not set the cookie if the session id was specified using a http header or a GET parameter.
        # There are two reasons to this:
        # - When using one of those two means we consider that we are overriding the cookie, which means creating a new
        #   session on top of an already existing session and we don't want to create a mess with the 'normal' session
        #   (the one using the cookie). That is a special feature of the Session Javascript class.
        # - It could allow session fixation attacks.
        if not explicit_session and hasattr(response, 'set_cookie'):
            cookie = dump_cookie('session_id', request.session.sid, max_age=90 * 24 * 60 * 60, secure=True,
                                 httponly=True)
            cookie = "{}; {}".format(cookie, b'SameSite=None'.decode('latin1'))
            response.headers.add('Set-Cookie', cookie)

        return response


http.Root.get_response = Root.get_response

class ShopifyController(http.Controller):

    @http.route('/shopify', type='http', auth="public")
    def index(self):
        @check_shopify_login
        @check_xero_login
        def view():
            return werkzeug.utils.redirect('/index')
        return view()

    @http.route('/index1', type='http', auth="public")
    def index1(self):
        return request.render('shopify_app.index1')

    @http.route('/shopify/login', auth='public', type='http')
    def shopify_login(self,**kw):
        shop_url = kw['shop']
        if not shop_url:
            raise Exception('Missing shop url parameter')
        session = ShopifyAuth(shop_url=shop_url, env=request.env)
        redirect_uri = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/shopify/callback'
        scope = [
            "read_inventory","read_customers", "write_customers", "write_products", "read_products","write_price_rules"
        , "read_price_rules", "read_script_tags","read_discounts","write_discounts",
            "read_draft_orders" ,"write_script_tags", "read_orders", "read_checkouts"
        ]
        permission_url = session.create_permission_url(redirect_uri=redirect_uri,scope=scope)
        return request.render('shopify_app.redirect_top',{'redirect_url':permission_url})

    @http.route('/shopify/callback', auth='public', type='http')
    def shopify_callback(self, **kw):
        shop_url = kw['shop']
        if not shop_url:
            raise Exception('Missing shop url parameter')
        session = ShopifyAuth(shop_url=shop_url, env=request.env)
        token = session.request_token(kw)
        try:
            if token:
                shopify_session = ShopifySession(shop_url=shop_url, token=token)
                timezone = shopify_session.set_shopify_store_timezone().split(' ')
                timezone = timezone[1]
                store_vals = {
                    'shopify_token': token,
                    'shopify_url': shop_url,
                    'timezone': timezone
                }
                shopify_store = request.env['shopify.store'].sudo().search([('shopify_url','=',shop_url)],limit=1)
                if not shopify_store:
                    shopify_store = request.env['shopify.store'].sudo().create(store_vals)
                else:
                    shopify_store.sudo().write(store_vals)

        except Exception as e:
            _logger.error(traceback.format_exc())
            shopify_session = ShopifySession(shop_url=shop_url)
            shopify_session.get_shopify_store().clear_shopify_token()
            shopify_session._clear_data()
            return e.__class__.__name__ + ': ' + str(e) + ' .Please try again!'
        URL = redirect_admin_app_page(shop_url=shop_url)
        return werkzeug.utils.redirect(URL)

    @http.route('/shopify/customer_data_request', type='json', auth="public", csrf=False)
    def customer_data_request(self, **kw):
        return 'Done'

    @http.route('/shopify/customer_redact', type='json', auth="public", csrf=False)
    def customer_redact(self, **kw):
        return 'Done'

    @http.route('/shopify/shop_redact', type='json', auth="public", csrf=False)
    def shop_react(self, **kw):
        try:
            if 'shop_domain' in kw:
                shop_model = request.env['shopify.shop'].sudo().search([('shop', '=', kw['shop_domain'])],
                                                                       limit=1)
                if shop_model:
                    shop_model.sudo().write({
                        'shopify_token': None,
                        'xero_token': None
                    })
        except Exception as e:
            _logger.error(traceback.format_exc())
        return 'Done'


class XeroController(http.Controller):

    @http.route('/xero_connect', auth='public', type='http')
    def xero_connect(self, *ar, **kw):
        try:
            auth = XeroAuth()
            url = auth.generate_url()
            return werkzeug.utils.redirect(url)
        except Exception as e:
            _logger.error(traceback.format_exc())
            return e.__class__.__name__ + ': '+ str(e)


    @http.route('/xero/callback', auth='public', type='http')
    def xero_callback(self, *ar, **kw):
        auth = XeroAuth()
        try:
            auth.verify(request.httprequest.url)
            if auth.token:
                XeroSession().set_token(token=auth.token)
                xero_session = XeroSession().get_xero_auth()
                shopify_store = ShopifySession().get_shopify_store()
                if shopify_store:
                    shopify_store.xero_token = json.dumps(auth.token)
                else:
                    raise Exception('Shop not found')

                # api_key = request.env['ir.config_parameter'].sudo().get_param('shopify_xero.shopify_api_key')
                URL = redirect_admin_app_page()
                return werkzeug.utils.redirect(URL)
        except Exception as e:
            _logger.error(traceback.format_exc())
            request.session.pop('xero', None)
            return e.__class__.__name__ + ': '+ str(e)




