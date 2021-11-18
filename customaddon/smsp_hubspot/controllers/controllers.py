# -*- coding: utf-8 -*-
# from odoo import http


# class Addons/smspHubspot(http.Controller):
#     @http.route('/addons/smsp_hubspot/addons/smsp_hubspot/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/addons/smsp_hubspot/addons/smsp_hubspot/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('addons/smsp_hubspot.listing', {
#             'root': '/addons/smsp_hubspot/addons/smsp_hubspot',
#             'objects': http.request.env['addons/smsp_hubspot.addons/smsp_hubspot'].search([]),
#         })

#     @http.route('/addons/smsp_hubspot/addons/smsp_hubspot/objects/<model("addons/smsp_hubspot.addons/smsp_hubspot"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('addons/smsp_hubspot.object', {
#             'object': obj
#         })
