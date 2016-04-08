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
from openerp.exceptions import except_orm, Warning, RedirectWarning


class invoice_merge(models.TransientModel):
    _name = "invoice.merge"

    def all_same(self, items):
        return all(x == items[0] for x in items)

    def _invoice_check(self):

        invoices = self.env["account.invoice"].browse(self.env.context["active_ids"])
        if len(invoices) == 1:
            raise except_orm("Seleccion invalida", "Debe de seleccionar mas de una factura para esta funcion")

        for state in [inv.state for inv in invoices]:
            if not state == 'draft':
                raise except_orm(u"Seleccion invalida", u"No puede haber facturas confirmadas en la seleccion")

        if not self.all_same([inv.partner_id.id for inv in invoices]):
            raise except_orm(u"Seleccion invalida", u"Los clientes de las facturas seleccionadas no coinciden")

    @api.one
    def merge_invoices(self):
        self._invoice_check()
        inv_obj = self.env['account.invoice']
        mod_obj = self.env['ir.model.data']
        result = mod_obj._get_id('account', 'invoice_form')
        res_id = mod_obj.browse([result]).res_id
        ids = self.env.context.get('active_ids', [])
        new_invoice_id = inv_obj.do_merge()
        return {
            'domain': "[('id','in', [{}])]".format(new_invoice_id.id),
            'name': 'Partner Invoice',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'search_view_id': res_id
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
