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
import openerp.addons.decimal_precision as dp


class invoice_credit_apply(models.TransientModel):
    _name = "invoice.credit.apply"

    def _check_open_credit(self):
        sql = """
        SELECT
         "account_invoice"."date_invoice",
         "account_invoice"."number",
         "account_invoice"."residual",
         "account_invoice"."type"
        FROM "account_invoice"
        WHERE ( "residual" > 0.00 ) AND ( "account_invoice"."type" = 'out_refund' ) AND ("account_invoice"."partner_id" = %(partner_id)s)
        """
        self.env.cr.execute(sql, dict(partner_id=self._context.get("default_partner_id")))
        res = self.env.cr.fetchall()
        if res:
            return res

        return False

    def _default_open_credit(self):
        amount = 0.00
        if self._context:
            res = self._check_open_credit()
            if res:
                amount += sum([rec[2] for rec in res])

        return amount

    open_credit = fields.Float(u"Credito disponible", default=_default_open_credit, readonly=True, digits_compute=dp.get_precision('Account'))

    @api.multi
    def apply_credit(self):
        for invoice in self.env["account.invoice"].browse(self._context["active_id"]):
            if invoice.residual > 0.00:
                domain = [('partner_id', '=', invoice.partner_id.id), ('type', '=', 'out_refund'), ('residual', '>', 0.00)]
                open_credit = self.env["account.invoice"].search(domain, order="id")
                credit = invoice.residual
                active_ids = []
                for inv_move_line in invoice.move_id.line_id:
                    if inv_move_line.account_id.id == invoice.partner_id.property_account_receivable.id:
                        active_ids.append(inv_move_line.id)
                    else:
                        continue

                for nc in open_credit:
                    for nc_line in nc.move_id.line_id:
                        if nc_line.account_id.id == invoice.partner_id.property_account_receivable.id:
                            if credit > 0:
                                active_ids.append(nc_line.id)
                                self.pool.get("account.move.line.reconcile").trans_rec_reconcile_partial_reconcile(self.env.cr, self.env.uid, [], context={"active_ids": active_ids})
                                credit -= nc_line.credit
                        else:
                            continue