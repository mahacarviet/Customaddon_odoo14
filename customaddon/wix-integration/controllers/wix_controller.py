from odoo import http
import werkzeug
AUTH_PROVIDER_BASE_URL = 'https://www.wix.com/oauth/access'
import requests
import json


class WixGoogleFeed(http.Controller):
    @http.route('/login/', auth='public')
    def authenticate(self, **kw):
        authorizationCode = kw["code"]
        print(authorizationCode)
        payload = json.dumps({
            'code': authorizationCode,
            'client_secret': "e9069b79-c57b-46b4-98ae-40b5f99fb128",
            'client_id': "f3c5a023-63ea-4515-a056-75517b756f38",
            'grant_type': "authorization_code",
        })
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", AUTH_PROVIDER_BASE_URL, headers=headers, data=payload)
        dict_response = json.loads(response.content)
        refreshToken = dict_response['refresh_token']
        accessToken = dict_response['access_token']
        # accessToken để call api tiếp, nhưng nó có hạn, hết hạn phải dùng refresh_token để call api lấy access_token khác
        # get business info
        headers_2 = {
            'Authorization': accessToken
        }
        response_2 = requests.request("GET", "https://www.wixapis.com/site-properties/v4/properties", headers=headers_2, data={})
        dict_response_2 = json.loads(response_2.content)
        print(dict_response_2)
        # login
        email = False
        if "properties" in dict_response_2:
            if "email" in dict_response_2["properties"] and dict_response_2["properties"]['email']:
                email = dict_response_2["properties"]['email']
        if email:
            current_user = http.request.env['res.users'].sudo().search([('login', '=', email)],
                                                                       limit=1)
            if not current_user:
                current_user = http.request.env['res.users'].sudo().create({
                    'company_ids': [[6, 0, [1]]],
                    'company_id': 1,
                    'active': True,
                    'lang': 'en_US', 'tz': 'Europe/Brussels',
                    'image_1920': False, '__last_update': False,
                    'name': email,
                    'email': email,
                    'login': email,
                    'password': email,
                })
            home_url = "https://odoo.website/web#cids=1&home="
            return werkzeug.utils.redirect(home_url)
        else:
            return werkzeug.utils.redirect("https://www.google.com/")

    @http.route('/signup/', auth='public')
    def finalize(self, **kw):
        permissionRequestUrl = 'https://www.wix.com/app-oauth-installation/consent'
        appId = "f3c5a023-63ea-4515-a056-75517b756f38"
        redirectUrl = 'https://odoo.website/login/'
        token = kw["token"]
        permission_url = permissionRequestUrl + "?token=" + token + "&appId=" + appId + "&redirectUrl=" + redirectUrl
        return werkzeug.utils.redirect(permission_url)
