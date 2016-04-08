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
    'name': "Libro de ventas para impresoras fiscales",

    'summary': """
        Este modulo permite conectarse a varias impresoras conectadas a la red
        por medio a los print server de Marcos""",

    'description': """
        Se configuran sucursales que tienen N cantidad de impresoras por medio a la ip
        en la se encuentres los print server de Marcos
    """,

    'author': "Marcos Organizador de Negocios SRL",
    'website': "http://marcos.do",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'marcos_ipf'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'book_view.xml',
        'wizard/book_generator_view.xml',
        # 'templates.xml'
    ],
}