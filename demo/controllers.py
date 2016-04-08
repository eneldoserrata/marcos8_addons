# -*- coding: utf-8 -*-
from openerp import http

# class Demo(http.Controller):
#     @http.route('/demo/demo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/demo/demo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('demo.listing', {
#             'root': '/demo/demo',
#             'objects': http.request.env['demo.demo'].search([]),
#         })

#     @http.route('/demo/demo/objects/<model("demo.demo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('demo.object', {
#             'object': obj
#         })