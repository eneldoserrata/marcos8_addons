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
    'name': 'Marcos Account Invoice Merge Wizard',
    'version': '1.0',
    'category': 'Finance',
    'description': """
Este módulo añade una acción en las facturas listas para fusionar las facturas. Éstos son la condición para permitir la fusión:
- Tipo debe ser la misma (la factura del cliente, factura del proveedor, cliente o proveedor de reembolso)
- Socio debe ser el mismo
- Moneda debe ser el mismo
- Cuenta por cobrar cuenta, tiene que ser el mismo
    """,
    'author': 'Eneldo Serrata',
    'website': 'http://marcos.do',
    'depends': ['account'],
    'data': [
        'wizard/invoice_merge_view.xml',
    ],
    'test': [
    ],
    'demo': [],
    'installable': True,
    'active': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
