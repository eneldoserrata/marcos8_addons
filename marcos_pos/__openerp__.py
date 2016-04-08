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
{   'name': 'Marcos Point of Sale features',
    'version': '1.0',
    'category': 'Point of Sale',
    'description': """
This module add new features to the POS
==============================================================================

* Chart of Accounts.
* The Tax Code Chart for Domincan Republic
* The main taxes used in Domincan Republic
* Fiscal position for local
    """,
    'author': 'Eneldo Serrata - Marcos Organizador de Negocios, SRL.',
    'website': 'http://marcos.do',
    'depends': ['base', 'point_of_sale', 'marcos_stock', 'marcos_ipf', 'hw_proxy'],

    # always loaded
    'data': [
        # 'security/pos_discount_security.xml',
        'security/ir.model.access.csv',
        'templates.xml',
        'wizard/marcos_pos_wizard.xml',
        'point_of_sale/point_of_sale_view.xml',
        'pos_manager/pos_manager_view.xml',
        'account/pos_journal_sequence_view.xml',
        'point_of_sale_workflow.xml'
    ],
    # only loaded in demonstration mode
    'qweb': [
        'static/src/xml/pos.xml',
        'static/src/xml/notes.xml'
    ],
    'demo': [
        'demo.xml',
    ],
}