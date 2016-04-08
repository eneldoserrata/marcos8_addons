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

from openerp import models, fields, api, exceptions
from openerp import netsvc
from openerp.osv.orm import browse_record, browse_null


class account_invoice(models.Model):
    _inherit = "account.invoice"

    def _create_line_to_meger_list(self, line):

        invoice_line_tax_id = [tax.id for tax in line.invoice_line_tax_id]
        line_dict = {'account_analytic_id': line.account_analytic_id.id,
                    'account_id': line.account_id.id,
                    'company_id': line.company_id.id,
                    'discount': line.discount,
                    # 'invoice_id': False,
                    'invoice_line_tax_id': [(6, 0, invoice_line_tax_id)],
                    'name': line.name,
                    'origin': line.origin,
                    'partner_id': line.partner_id.id,
                    'price_unit': line.price_unit,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'sequence': line.sequence,
                    'uos_id': line.uos_id.id}
        return line_dict

    def do_merge(self):
        invoice_lines = []
        invoice_ids = self.env.context["active_ids"]
        invoices = self.browse(invoice_ids)
        origins = [inv.origin for inv in invoices]
        for invoice in invoices:
            for line in invoice.invoice_line:
                invoice_lines.append((0, 0, self._create_line_to_meger_list(line)))
        default = {"invoice_line": invoice_lines,
                   "origin": origins,
                   "journal_id": self._get_partner_journal(invoices[0].fiscal_position, invoices[0].shop_ncf_config_id)}

        new_invoice = invoice[0].copy(default)
        for invoice in invoices:
            invoice.unlink()
        new_invoice.button_reset_taxes()
        return new_invoice


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
