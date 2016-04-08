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

from openerp import models, fields, api


class product_uom(models.Model):
    _inherit = 'product.uom'

    can_retail = fields.Boolean("Unidad para detalle")
    fraction_line = fields.One2many("product.uom.fraction", "fraction_id")


class product_uom_unit_fraction(models.Model):
    _name = 'product.uom.fraction'

    fraction_id = fields.Many2one("product.uom")
    name = fields.Char(u"Descripción")
    fraction_package = fields.Many2one("product.product", "Envase")
    fraction_qty = fields.Float(u"Fracción")




