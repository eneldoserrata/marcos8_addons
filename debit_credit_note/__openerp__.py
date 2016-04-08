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
{   'name': 'Dominican Republic - Notas de credito y Debito',
    'version': '1.0',
    'category': 'Localization/Account Charts',
    'description': """
Este modulo ajusta el uso de las notas de credito
=================================================

    """,
    'author': 'Eneldo Serrata - Marcos Organizador de Negocios, SRL.',
    'website': 'http://marcos.do',
    "depends": [
        "base", 
        "account"
    ], 
    "demo": [], 
    "data": [
        # "wizard/account_invoice_debit_view.xml",
        "wizard/account_invoice_parent_view.xml",
        "wizard/accout_refund_reconcilie_view.xml",
        "wizard/account_invoice_refund_view.xml",
        "account_invoice_view.xml"
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}