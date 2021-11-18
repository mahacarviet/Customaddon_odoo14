# -*- coding: utf-8 -*-
# from odoo import http


# class PlanSaleTest(http.Controller):
#     @http.route('/plan_sale_test/plan_sale_test/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plan_sale_test/plan_sale_test/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('plan_sale_test.listing', {
#             'root': '/plan_sale_test/plan_sale_test',
#             'objects': http.request.env['plan_sale_test.plan_sale_test'].search([]),
#         })

#     @http.route('/plan_sale_test/plan_sale_test/objects/<model("plan_sale_test.plan_sale_test"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plan_sale_test.object', {
#             'object': obj
#         })
