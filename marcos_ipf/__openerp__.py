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
    'name': "Marcos IPF",

    'summary': """
        Este modulo permite utilizar la impresora fiscal requerida por la DGII en la
        Republica Dominicana
        """,

    'description': """
        Mediante este modulo se puede configurar una
        impresora fiscal utilizando la interface de Marcos_IPF
    """,

    'author': "Eneldo Serrata",
    'website': "http://marcos.do",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'DGII',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'marcos_ncf'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'templates.xml',
        'marcos_ipf_views.xml'
    ]
    # only loaded in demonstration mode
    # 'demo': [
        # 'demo.xml',
    # ],
}