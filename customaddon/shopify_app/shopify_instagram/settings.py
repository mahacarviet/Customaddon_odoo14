import traceback
from urllib.parse import urlencode

from odoo import http, fields
from .auth import ShopifySession
from ..models.decorators import ensure_shop_login
import logging
from odoo.http import request
from werkzeug.utils import redirect
from .main import get_base_url
from .auth import InstagramSession

_logger = logging.getLogger(__name__)
import json


class Settings(http.Controller):

    @http.route('/instagram/settings', type='http', auth='public')
    def settings_index(self):
        try:
            ensure_shop_login()
            shopify_session = ShopifySession()
            shop_model = shopify_session.get_shop_model()
            message = request.params.get('message')
            instagram_session = InstagramSession()
            shop_model.add_section_template_to_shop()
            if shop_model.instagram_token:
                instagram_session.check_token()
            shopify_api_key = request.env['ir.config_parameter'].sudo().get_param('shopify_instagram.shopify_api_key')
            shop_origin = shop_model.shop
            return request.render('shopify_instagram.instagram_settings_index', {
                'message': message,
                'connect_instagram_url': instagram_session.get_auth_url(),
                'instagram_username': shop_model.instagram_username if shop_model.instagram_username else '',
                'api_key': shopify_api_key,
                'shop_origin': shop_origin,
                'app_origin': get_base_url(),
                'current_plan': shop_model.get_current_plan().name,
                'live_support': shop_model.get_current_plan().live_support,
                'slider_settings': json.dumps(shop_model.get_instagram_feed_settings())
            })
        except Exception as e:
            _logger.error(traceback.format_exc())
            return request.render('shopify_instagram.instagram_exception', {
                'reset_action': '/instagram/reset'
            })

    @http.route('/instagram/reset', type='http', auth='public', methods=['POST'])
    def reset(self):
        shop_url = ''
        try:
            instagram_session = InstagramSession()
            shopify_session = ShopifySession()
            shop_url = shopify_session.get_shop_url()
            shopify_session.reset()
            instagram_session.reset()
        except Exception as e:
            _logger.error(traceback.format_exc())
        return redirect('/instagram?' + urlencode({'shop': shop_url}))

    @http.route('/instagram/hotspot/save', type='json', auth='public', methods=['POST'], csrf=False)
    def save_hotspot(self):
        try:
            ensure_shop_login()
            params = request.params
            shopify_session = ShopifySession()
            shop_model = shopify_session.get_shop_model()
            media_params = params.get('media')
            product_params = params.get('product')
            if not shop_model:
                raise Exception('Invalid session.')
            if not media_params:
                raise Exception('Media Params missing.')
            if product_params:
                image_params = product_params.get('images')
                request.env['instagram.media.hotspot'].sudo().create({
                    'shop_id': shop_model.id,
                    'media_id': media_params.get('id'),
                    'top_percent': params.get('top_perc'),
                    'left_percent': params.get('left_perc'),
                    'product_name': product_params.get('title'),
                    'product_url': 'https://' + shop_model.shop + '/products/' + product_params.get('handle'),
                    'product_handle': product_params.get('handle'),
                    'product_image_url': image_params[0].get('originalSrc') if image_params else ''
                })
            elif params.get('id'):
                hotspot = request.env['instagram.media.hotspot'].sudo().search([('id', '=', params.get('id'))], limit=1)
                if hotspot and hotspot.shop_id.id == shop_model.id and hotspot.media_id.id == media_params.get('id'):
                    if params.get('delete'):
                        hotspot.unlink()
                    else:
                        hotspot.top_percent = float(params.get('top_perc'))
                        hotspot.left_percent = float(params.get('left_perc'))
                else:
                    return 'Could not find the hotspot, please refresh your browser and try again!'
            media = request.env['instagram.media'].sudo().search([('id', '=', media_params.get('id'))], limit=1)
            return media.get_hotspots()
        except Exception as e:
            _logger.error(traceback.format_exc())
            return str(e)

    @http.route('/instagram/media/toggle_display', type='json', auth='public', methods=['POST'], csrf=False)
    def toggle_display_media(self):
        try:
            ensure_shop_login()
            params = request.params
            shopify_session = ShopifySession()
            shop_model = shopify_session.get_shop_model()
            media_id = params.get('media_id')
            if not shop_model.plan.select_display:
                raise Exception('Invalid Plan.')
            if not shop_model:
                raise Exception('Invalid session.')
            if not media_id:
                raise Exception('Media ID missing.')

            media = request.env['instagram.media'].sudo().search([('id', '=', media_id)], limit=1)
            media.show = not media.show
            return media.show
        except Exception as e:
            _logger.error(traceback.format_exc())
            return str(e)

    @http.route('/instagram-feed-settings', type='http', auth='public', methods=['GET'], cors='*')
    def get_instagram_settings(self):
        try:
            params = request.params
            shop = params.get('shop')
            if not shop:
                raise Exception('Missing shop parameter')
            product_handle = params.get('product_handle')
            shop_model = request.env['shopify.instagram.shop'].get_shop_by_origin(shop)
            is_backend = bool(params.get('backend'))
            if not shop_model:
                raise Exception('Could not find settings for the requested origin.')
            try:
                if hasattr(request, 'httprequest') and hasattr(request.httprequest, 'referrer'):
                    referrer_url = request.httprequest.referrer
                    if referrer_url and referrer_url.find(get_base_url()) == -1:
                        request.env['instagram.frontend.request.log'].sudo().create({
                            'shop_id': shop_model.id,
                            'request_time': fields.Datetime.now()
                        })
            except Exception as e:
                _logger.error(traceback.format_exc())
            return json.dumps({
                'medias': shop_model.get_saved_medias(product_handle=product_handle, limit=128, is_backend=is_backend),
                'slider_settings': shop_model.get_instagram_feed_settings()
            })
        except Exception as e:
            _logger.error(traceback.format_exc())
            return str(e)

    @http.route('/instagram/settings/save', type='http', auth='public', methods=['POST'], csrf=False)
    def settings_save(self):
        try:
            ensure_shop_login()
            shopify_session = ShopifySession()
            shop_model = shopify_session.get_shop_model()
            params = request.params
            shop_model.instagram_enable_popup = bool(int(params.get('enable_popup'))) if params.get('enable_popup') else False
            shop_model.instagram_feed_label = params.get('feed_label')
            shop_model.instagram_feed_slides_per_row = params.get('slides_per_row')
            shop_model.instagram_feed_rows = params.get('rows')
            shop_model.instagram_feed_width = params.get('width')
            shop_model.instagram_button_color = params.get('button_color')
            shop_model.instagram_feed_layout = int(params.get('feed_layout')) if params.get('feed_layout') else False
            return redirect('/instagram')
        except Exception as e:
            _logger.error(traceback.format_exc())
            return request.render('shopify_instagram.instagram_exception', {
                'reset_action': '/instagram/reset'
            })

    @http.route('/instagram/plan/charge', type='http', auth='public', methods=['POST'], csrf=False)
    def plan_charge(self):
        try:
            if 'plan' not in request.params:
                raise Exception('Missing plan parameter. Please try again!')
            plan = request.env['shopify.instagram.plan'].sudo().get_plan_by_name(request.params['plan'])
            if not plan:
                raise Exception('Could not find the plan you were looking for. Please try again!')
            shopify_session = ShopifySession()
            charge_url = plan.get_charge_url()

            return request.render('shopify_instagram.shopify_connect', {
                'auth_url': charge_url
            })
        except Exception as e:
            _logger.error(traceback.format_exc())
            return redirect('/instagram/settings?' + urlencode({'message': str(e)}))

    @http.route('/instagram/plan/accept', type='http', auth='public')
    def plan_accept(self):
        try:
            if not 'charge_id' in request.params:
                raise Exception('Missing charge ID. Please try again')
            shopify_session = ShopifySession()
            plan = request.env['shopify.instagram.plan']
            charge = plan.activate_plan(request.params['charge_id'])

            return redirect('/instagram/settings?' + urlencode({'message': 'You have successfully subscribed to a new plan.'}))
        except Exception as e:
            _logger.error(traceback.format_exc())
            return redirect('/instagram/settings?' + urlencode({'message': str(e)}))

    @http.route('/instagram/analytic/add_to_card', type='json', auth='public', methods=['POST'], csrf=False)
    def analytic_add_to_cart(self):
        try:
            ensure_shop_login()
            params = request.params
            print(params)
            shop = ShopifySession().shop_model()
            hour = shop.convert_to_shop_timezone().time().hour()
            request.env['instagram.add.to.cart'].sudo().create({
                'shop': shop.id,
                'media': media_id,
                'product_id': product_id,
                'ip_user': ip_user,
                'date': datetime.now(),
                'hour': hour,
            })
            # product_has_variants = ShopifySession().check_varaints() # front-end
            if has_variants:
                return redirect('link_choose_product_variant')
            else:
                return redirect('')
        except Exception as e:
            _logger.error(traceback.format_exc())
            return str(e)