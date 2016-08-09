# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Open Business Solutions (<http://www.obsdr.com>)
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd(<http://www.cozybizs.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'l10n Check printing',
    'version': '1.0',
    'author' : 'Naresh Soni',
    'website' : 'http://www.cozybizs.com',
    'category': 'Localization',

    'summary': 'Permite configurar desde los diarios las plantillas para impresion de chques.',
    'description': """
        Este módulo permite configurar sus cheques de pagos en el papel de verificación pre-impreso.
        Puede configurar la salida (distribución, información trozos, etc.) en los entornos de la empresa, y gestionar el
        cheques de numeración (si utiliza cheques preimpresos sin números) en la configuración de diario.
    """,
    'depends' : ['account_check_writing'],
    'data': [
        'report/paper_data.xml',
        'report/report_data.xml',
        'data/l10n_do_check_printing_data.xml',
        'report/report_template.xml',
        'views/account_view.xml',
        'views/check_report_config_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
