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

{
    "name": "Marcos Caja Chica",
    "version": "1.0",
    "description": """
        TODO
    """,
    "author": "Marcos Organizador de Negocios",
    "website": "http://marcos.do",
    "category": "Financial",
    "depends": [
        "base",
        "account",
        "account_voucher",
        "point_of_sale"
        ],
    "data": [
            "views/cjc_view.xml",
             "wizard/cjc_wizard_view.xml",
             "security/ir.model.access.csv"
    ],
    "demo_xml": [],
    "update_xml": [],
    "active": False,
    "installable": True,
    "certificate": "",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
