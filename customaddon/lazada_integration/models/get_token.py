# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ..python import lazop
import json
import requests


class GetTokenLazada(models.Model):
    _name = 'get.token.lazada'

    url = 'https://api.lazada.vn/rest'
    appkey = 102554
    appSecret = 'WiwfDkCjn6VyA2RGUXlcaPrsHPISOqyM'

    client = lazop.LazopClient(url, appkey , appSecret)
    request = lazop.LazopRequest('/auth/token/create')
    request.add_api_param('code', '0_2DL4DV3jcU1UOT7WGI1A4rY91')
    request.add_api_param('uuid', '38284839234')
    response = client.execute(request)
    print(response.type)
    print(response.body)