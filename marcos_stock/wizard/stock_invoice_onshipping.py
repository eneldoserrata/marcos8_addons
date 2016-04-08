# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import models, api


class stock_invoice_onshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"


    @api.multi
    def create_invoice(self):

        res = super(stock_invoice_onshipping, self).create_invoice()

        picking_id = self.env["stock.picking"].browse(self._context["active_id"])
        if picking_id.afecta:
            self.env["account.invoice"].browse(res).write({"parent_id": picking_id.afecta.id})

        return res

