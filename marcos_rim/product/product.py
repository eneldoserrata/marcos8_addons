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

from openerp.osv import fields, osv
from openerp import api
import openerp.addons.decimal_precision as dp


class product_template(osv.Model):
    _inherit = 'product.template'

    CLASIFICATION = [
        ("p", "PLATINUM"),
        ("g", "GOLD"),
        ("s", "SILVER"),
        ("b", "BRONZE")
    ]

    def _product_valuation(self, cr ,uid ,ids , field, arg, context=None):
        res = {}
        for prod in self.browse(cr, uid, ids, context=context):
            res[prod.id] = prod.qty_available * prod.standard_price
        return res

    _columns = {
        'clasification': fields.selection(CLASIFICATION, "Clasification"),
        'total_valuation': fields.function(_product_valuation, type='float', digits_compute=dp.get_precision('Account'),
                                     string='Total'),
    }

    _defaults = {
        'sale_delay': 0,
    }