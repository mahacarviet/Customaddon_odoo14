# -*- coding: utf-8 -*-
# from odoo import http


# class InternTest1(http.Controller):
#     @http.route('/intern_test_1/intern_test_1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/intern_test_1/intern_test_1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('intern_test_1.listing', {
#             'root': '/intern_test_1/intern_test_1',
#             'objects': http.request.env['intern_test_1.intern_test_1'].search([]),
#         })

#     @http.route('/intern_test_1/intern_test_1/objects/<model("intern_test_1.intern_test_1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('intern_test_1.object', {
#             'object': obj
#         })
