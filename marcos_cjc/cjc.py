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
from openerp import fields, models


class marcos_cjc_concept(models.Model):
    _name = "marcos.cjc.concept"

    name = fields.Char(u"Descripción", size=50, required=True)
    supplier_taxes_id = fields.Many2many('account.tax', 'cjc_supplier_taxes_rel', 'prod_id', 'tax_id', 'Impuestos',
                                         required=True, domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['purchase', 'all'])])
    account_expense = fields.Many2one('account.account', "Cuenta de gasto", required=True)

        # "product_id": fields.many2one("product.product", string="Producto", required=True),

