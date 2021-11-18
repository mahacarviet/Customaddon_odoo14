# -*- coding: utf-8 -*-
# from odoo import http


# class LazadaIntegration(http.Controller):
#     @http.route('/lazada_integration/lazada_integration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lazada_integration/lazada_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lazada_integration.listing', {
#             'root': '/lazada_integration/lazada_integration',
#             'objects': http.request.env['lazada_integration.lazada_integration'].search([]),
#         })

#     @http.route('/lazada_integration/lazada_integration/objects/<model("lazada_integration.lazada_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lazada_integration.object', {
#             'object': obj
#         })
