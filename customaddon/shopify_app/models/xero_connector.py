from ..controllers.auth import ShopifySession
import json
from xero import Xero
from xero.manager import Manager
from xero.auth import OAuth2Credentials
from xero.exceptions import (
    XeroBadRequest,
    XeroExceptionUnknown,
    XeroForbidden,
    XeroInternalError,
    XeroNotAvailable,
    XeroNotFound,
    XeroNotImplemented,
    XeroRateLimitExceeded,
    XeroTenantIdNotSet,
    XeroUnauthorized,
)
from six.moves.urllib.parse import parse_qs
import requests
from xml.parsers.expat import ExpatError
from .log_models import RequestLog
from odoo.http import request


class XeroConnect(Xero):

    def __init__(self, credentials, unit_price_4dps=False, user_agent=None):
        super(XeroConnect, self).__init__(credentials, unit_price_4dps=False, user_agent=None)
        for name in self.OBJECT_LIST:
            setattr(
                self,
                name.lower(),
                XeroManager(name, credentials, unit_price_4dps, user_agent),
            )


class XeroManager(Manager):

    def _get_data(self, func):
        """ This is the decorator for our DECORATED_METHODS.
        Each of the decorated methods must return:
            uri, params, method, body, headers, singleobject
        """

        def wrapper(*args, **kwargs):
            timeout = kwargs.pop("timeout", None)

            uri, params, method, body, headers, singleobject = func(*args, **kwargs)

            if headers is None:
                headers = {}

            if isinstance(self.credentials, OAuth2Credentials):
                if self.credentials.tenant_id:
                    headers["Xero-tenant-id"] = self.credentials.tenant_id
                else:
                    raise XeroTenantIdNotSet

            # Use the JSON API by default, but remember we might request a PDF (application/pdf)
            # so don't force the Accept header.
            if "Accept" not in headers:
                headers["Accept"] = "application/json"

            # Set a user-agent so Xero knows the traffic is coming from pyxero
            # or individual user/partner
            headers["User-Agent"] = self.user_agent

            response = getattr(requests, method)(
                uri,
                data=body,
                headers=headers,
                auth=self.credentials.oauth,
                params=params,
                timeout=timeout,
            )
            data = {
                'request_url': uri,
                'request_headers': headers,
                'request_body': body,
                'request_params': params,
                'response_code': response.status_code,
                'response_body': response.text,
            }
            self.log_request(data)
            if response.status_code == 200:
                # If we haven't got XML or JSON, assume we're being returned a
                # binary file
                if not response.headers["content-type"].startswith("application/json"):
                    return response.content

                return self._parse_api_response(response, self.name)

            elif response.status_code == 204:
                return response.content

            elif response.status_code == 400:
                try:
                    raise XeroBadRequest(response)
                except (ValueError, ExpatError):
                    raise XeroExceptionUnknown(
                        response, msg="Unable to parse Xero API response"
                    )

            elif response.status_code == 401:
                raise XeroUnauthorized(response)

            elif response.status_code == 403:
                raise XeroForbidden(response)

            elif response.status_code == 404:
                raise XeroNotFound(response)

            elif response.status_code == 500:
                raise XeroInternalError(response)

            elif response.status_code == 501:
                raise XeroNotImplemented(response)

            elif response.status_code == 503:
                # Two 503 responses are possible. Rate limit errors
                # return encoded content; offline errors don't.
                # If you parse the response text and there's nothing
                # encoded, it must be a not-available error.
                payload = parse_qs(response.text)
                if payload:
                    raise XeroRateLimitExceeded(response, payload)
                else:
                    raise XeroNotAvailable(response)
            else:
                raise XeroExceptionUnknown(response)

        return wrapper


    def log_request(self, data):
        shop_url = ShopifySession().get_shop_url()
        shopify_store = ShopifySession().get_shopify_store()
        # if shop_url:
        #     shopify_store = self.env['request.log'].sudo().search([('shopify_url', '=', shop_url)])
        if shopify_store:
            log = {
                'shopify_store': shopify_store.id,
                }
            log.update(data)
            shopify_store.env['request.log'].sudo().create(log)
            # print('abc')