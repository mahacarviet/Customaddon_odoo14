import base64

import requests
import json
import logging
from odoo import http, _
from datetime import datetime, timedelta
import werkzeug
from werkzeug.utils import redirect
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class XeroConnector(http.Controller):
    @http.route('/xero_connect', auth='public', type='http', website=True)
    def xero_connect(self, **kwarg):
        #   Login Xero Accounting
        xero_id = http.request.env['xero.app'].sudo().search([('xero_app_name', 'ilike', 'Odoo Integration')],
                                                             limit=1)
        if xero_id:
            redirect_uri = xero_id.xero_redirect_url
            scope = 'offline_access accounting.transactions openid profile email accounting.contacts accounting.settings'
            state = '123'
            url_1 = 'https://login.xero.com/identity/connect/authorize?response_type=code&client_id='
            url_2 = xero_id.xero_client_id + '&redirect_uri=' + redirect_uri + '&scope=' + scope + '&state=' + state
            xero_redirect = url_1 + url_2
            return werkzeug.utils.redirect(xero_redirect)

    @http.route('/xero/get_auth_code', type="http", auth="public", website=True)
    def get_auth_code(self, **kwarg):
        if kwarg.get('code'):
            access_token_url = 'https://identity.xero.com/connect/token'

            xero_id = http.request.env['xero.app'].sudo().search([('xero_app_name', 'ilike', 'Odoo Integration')],
                                                                 limit=1)
            if xero_id:
                #   Call Get Token
                data = xero_id.xero_client_id + ":" + xero_id.xero_client_secret
                encodedBytes = base64.b64encode(data.encode("utf-8"))
                encodedStr = str(encodedBytes, "utf-8")
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': "Basic " + encodedStr
                }
                data_token = {
                    'code': kwarg.get('code'),
                    'redirect_uri': xero_id.xero_redirect_url,
                    'grant_type': 'authorization_code'
                }
                access_token = requests.post(access_token_url, data=data_token, headers=headers, verify=False)
                if access_token:
                    parsed_token_response = json.loads(access_token.text)
                    shop_xero_id = http.request.env['xero.app'].sudo().search(
                        [('xero_app_name', 'ilike', 'Odoo Integration')], limit=1)
                    if parsed_token_response:
                        if shop_xero_id:
                            shop_xero_id.sudo().write({
                                'xero_access_token': parsed_token_response.get('access_token'),
                                'xero_refresh_token': parsed_token_response.get('refresh_token'),
                                'xero_token_type': parsed_token_response.get('token_type'),
                                'xero_id_token': parsed_token_response.get('id_token'),
                                'status': 'connected'
                            })

                    #   Get Tenant From Xero
                    header1 = {
                        'Authorization': "Bearer " + parsed_token_response.get('access_token'),
                        'Content-Type': 'application/json'
                    }

                    xero_tenant_response = requests.request('GET', 'https://api.xero.com/connections', headers=header1)

                    parsed_tenent = json.loads(xero_tenant_response.text)
                    list_tenant = []
                    if parsed_tenent:
                        for tenant in parsed_tenent:
                            if 'tenantId' in tenant:
                                list_tenant.append({
                                    'xero_id': tenant.get('tenantId'),
                                    'xero_tenant_name': tenant.get('tenantName'),
                                    'xero_tenant_type': tenant.get('tenantType'),
                                    'xero_auth_event_id': tenant.get('authEventId')
                                })
                                if list_tenant:
                                    shop_xero_id.xero_app_tenant_ids = [(0, 0, e) for e in list_tenant]
                                list_tenant = []

                        _logger.info(_("Authorization successfully!"))

            return werkzeug.utils.redirect('http://localhost:8069/web#cids=1&home=')

    # @http.route('/xero/<int:shop_id>/render', auth='public', type='http', website=True)
    # def xero_render(self, shop_id=None, **kwargs):
    #     a = request.search()
    #     return request.render("xero_integration.xero_main", {
    #         'sale_account': a
    #     })
