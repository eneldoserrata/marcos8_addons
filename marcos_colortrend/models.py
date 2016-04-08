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


class marcos_colortrend(models.Model):
    _name = 'marcos.colortrend.formula'

    @api.one
    def _color_cost(self):
        base = self.base.standard_price or 0.0
        col_one = (self.col_one.standard_price*self.col_one_qty)/1536 or 0.0
        col_two = (self.col_two.standard_price*self.col_two_qty)/1536 or 0.0
        col_tree = (self.col_tree.standard_price*self.col_tree_qty)/1536 or 0.0
        col_four = (self.col_four.standard_price*self.col_four_qty)/1536 or 0.0
        self.color_cost = base+col_one+col_two+col_tree+col_four

    @api.one
    def _get_rep(self):
        y, p = divmod(self.col_one_qty, 48)
        self.col_one_qty_rep = "%s - %sY" % (p, y)

    name = fields.Char("Formula")
    base = fields.Many2one("product.product", "Base", ondelete='set null', index=True)

    col_one = fields.Many2one("product.product", "Colorante 1", ondelete='set null', index=True)
    col_one_qty = fields.Float("Puntos para el colorante 1")
    col_one_qty_rep = fields.Char(compute="_get_rep", string="Puntos para el colorante 1")

    col_two = fields.Many2one("product.product", "Colorante 2", ondelete='set null', index=True)
    col_two_qty = fields.Float("Puntos para el colorante 2")

    col_tree = fields.Many2one("product.product", "Colorante 3", ondelete='set null', index=True)
    col_tree_qty = fields.Float("Puntos para el colorante 3")

    col_four = fields.Many2one("product.product", "Colorante 4", ondelete='set null', index=True)
    col_four_qty = fields.Float("Puntos para el colorante 4")

    color_cost = fields.Float(compute="_color_cost", string="Costo")
