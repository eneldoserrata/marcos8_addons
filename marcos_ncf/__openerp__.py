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
    'name': "Marcos NCF",

    'summary': """
        Administracion y generacion de comprobantes fiscales.
        """,

    'description': """

        Este modulo permite agilizar, configura y administrar los comprobantes fiscales (NCF) en los
        proceso de asignacion y configuracion por sucursales ademas de generar los reportes necesarios
        para la DGII 607 y 607.
    """,

    'author': "Marcos Organizador de Negocios SRL",
    'website': "http://marcos.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Extra Tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'account', 'marcos_l10n_do', 'debit_credit_note', 'account_voucher', 'account_check_writing', 'marcos_branding'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'account/shop_view.xml',
        'res_partner/res_partner_view.xml',
        'data.xml',
        'templates.xml',
        'account/account_invoice_view.xml',
        'res/res_users_view.xml',
        'dgii_compras/view.xml',
        'dgii_ventas/view.xml',
        'res/res_currency_view.xml',
        'account_voucher/account_voucher_view.xml',
        'wizard/invoice_credit_apply_view.xml'
    ],
    # 'js': ['static/src/js/ipf.js'],
    'qweb': [],
    # only loaded in demonstration mode
    # 'demo': [
    # ],
}