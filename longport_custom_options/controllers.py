# -*- coding: utf-8 -*-
from openerp import http

# class LongportCustomOptions(http.Controller):
#     @http.route('/longport_custom_options/longport_custom_options/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/longport_custom_options/longport_custom_options/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('longport_custom_options.listing', {
#             'root': '/longport_custom_options/longport_custom_options',
#             'objects': http.request.env['longport_custom_options.longport_custom_options'].search([]),
#         })

#     @http.route('/longport_custom_options/longport_custom_options/objects/<model("longport_custom_options.longport_custom_options"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('longport_custom_options.object', {
#             'object': obj
#         })