# -*- coding: utf-8 -*-
# from odoo import http


# class InternTest2(http.Controller):
#     @http.route('/intern_test_2/intern_test_2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/intern_test_2/intern_test_2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('intern_test_2.listing', {
#             'root': '/intern_test_2/intern_test_2',
#             'objects': http.request.env['intern_test_2.intern_test_2'].search([]),
#         })

#     @http.route('/intern_test_2/intern_test_2/objects/<model("intern_test_2.intern_test_2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('intern_test_2.object', {
#             'object': obj
#         })
