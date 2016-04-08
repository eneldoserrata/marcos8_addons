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

{   'name': 'Dominican Republic - Accounting - Custom',
    'version': '1.0',
    'category': 'Localization/Account Charts',
    'description': """
This is the base module to manage the accounting chart for Dominican Republic.
==============================================================================

* Chart of Accounts.
* The Tax Code Chart for Domincan Republic
* The main taxes used in Domincan Republic
* Fiscal position for local
    """,
    'author': 'Eneldo Serrata - Marcos Organizador de Negocios, SRL.',
    'website': 'http://marcos.do',
    'depends': ['base',
                'account',
                'account_voucher',
                'account_cancel'],
    'data': [
        # basic accounting data
        # 'data/ir_sequence_type.xml',
        'data/ir_sequence.xml',
        'data/account_journal.xml',
        'data/account.account.type.csv',
        'data/account.account.template.csv',
        'data/account.tax.code.template.csv',
        'data/account_chart_template.xml',
        'data/account.tax.template.csv',
        'data/l10n_do_base_data.xml',
        # Adds fiscal position
        'data/account.fiscal.position.template.csv',
        'data/account.fiscal.position.tax.template.csv',
        # configuration wizard, views, reports...
        'data/l10n_do_wizard.xml',
        'account/account_view.xml',
        'data/report_paperformat.xml'
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
