# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
#    Write by Eneldo Serrata (eneldo@marcos.do)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import http

# class MarcosReport(http.Controller):
#     @http.route('/marcos_report/marcos_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/marcos_report/marcos_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('marcos_report.listing', {
#             'root': '/marcos_report/marcos_report',
#             'objects': http.request.env['marcos_report.marcos_report'].search([]),
#         })

#     @http.route('/marcos_report/marcos_report/objects/<model("marcos_report.marcos_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('marcos_report.object', {
#             'object': obj
#         })