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
from openerp.tools.translate import _


class stock_return_picking(models.TransientModel):
    _inherit = 'stock.return.picking'

    afecta = fields.Char("Factura que afecta", size=19, readonly=True)
    invoice_state = fields.Selection([('2binvoiced', 'Si'), ('none', 'No')], string='Crear factura')
    # refund_state = fields.Selection([('2binvoiced', 'Si'), ('none', 'No')], string=u'Crear nota de crédito')
    # refund_type = fields.Selection([("client", "Cliente"), ("supplier", "Suplidor"), ("internal", "Internal")], "Type of refund", default="internal")

    @api.model
    def default_get(self, fields):

        res = super(stock_return_picking, self).default_get(fields)

        picking_id = self.env["stock.picking"].browse(self._context["active_id"])
        if picking_id.invoice_id or picking_id.group_id:
            if picking_id.invoice_id.number:
                res.update({"afecta": picking_id.invoice_id.number, "invoice_state": "2binvoiced"})

        return res

    @api.model
    def _create_returns(self):
        res = super(stock_return_picking, self)._create_returns()
        data = self.browse(self._ids[0])

        if data.afecta:
            afecta_invoice_id = self.env["account.invoice"].search([('number', '=', data.afecta)])
            picking = self.env["stock.picking"].browse(res[0])
            picking.write({"afecta": afecta_invoice_id.id, "invoice_id": False})

        return res

    @api.multi
    def create_returns(self):
        """
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """

        new_picking_id, pick_type_id = self._create_returns()
        # Override the context to disable all the potential filters that could have been set previously
        ctx = {
            'search_default_picking_type_id': pick_type_id,
            'search_default_draft': False,
            'search_default_assigned': False,
            'search_default_confirmed': False,
            'search_default_ready': False,
            'search_default_late': False,
            'search_default_available': False,
        }
        return {
            'domain': "[('id', 'in', [" + str(new_picking_id) + "])]",
            'name': _('Returned Picking'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': ctx,
        }
