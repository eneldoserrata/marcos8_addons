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

from datetime import datetime, timedelta
from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import except_orm, Warning, RedirectWarning


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends("parent_id")
    def _get_no_more_cn(self):
        ncs = self.parent_id.child_ids
        if ncs:
            self.parent_id.no_more_cn = sum(
                [nc.amount_untaxed for nc in ncs if nc.state not in ["cancel"]]) >= self.parent_id.amount_untaxed


    parent_id = fields.Many2one('account.invoice',
                                'Afecta',
                                readonly=True,
                                states={'draft': [('readonly', False)]},
                                help='Factura que afecta')
    child_ids = fields.One2many('account.invoice',
                                'parent_id',
                                u'Notas de credito',
                                readonly=True,
                                states={'draft': [('readonly', False)]},
                                help=u'Estas son todas las de credito para esta factura')
    no_more_cn = fields.Boolean(default=False, copy=False)
    parent_id_number = fields.Char(related="parent_id.number")

    def copy(self, cr, uid, id, default={}, context=None):
        """ Allows you to duplicate a record,
        child_ids, nro_ctrl and reference fields are
        cleaned, because they must be unique
        """
        if context is None:
            context = {}
        default.update({
            'child_ids': [],
        })
        return super(account_invoice, self).copy(cr, uid, id, default, context)

    def set_amount_untaxed(self, parent_id, vals):
        parent_invoice = self.browse(parent_id)
        if not vals.get("state", False) and len(vals) == 1:
            if vals.get("state", False) == "cancel":
                parent_invoice.no_more_cn = (sum([nc.amount_untaxed for nc in parent_invoice.child_ids if nc.state not in ["cancel"]]) - self.amount_untaxed) >= parent_invoice.amount_untaxed
            else:
                parent_invoice.no_more_cn = (sum([nc.amount_untaxed for nc in parent_invoice.child_ids if nc.state not in ["cancel"]]) + self.amount_untaxed) >= parent_invoice.amount_untaxed


    @api.multi
    def write(self, vals):
        if self.parent_id and self.type in ("in_refund", "out_refund"):
            if vals.get("state", False) == "cancel":
                self.parent_id.no_more_cn = (sum([nc.amount_untaxed for nc in self.parent_id.child_ids if nc.state not in ["cancel"]]) - self.amount_untaxed) == self.parent_id.amount_untaxed
            else:
                self.parent_id.no_more_cn = (sum([nc.amount_untaxed for nc in self.parent_id.child_ids if nc.state not in ["cancel"]]) + self.amount_untaxed) == self.parent_id.amount_untaxed

        # remove tax from out_refund if parent_id date_invoice > 30 days Dominican Rules
        if self.type == "out_refund" and (
                    vals.get("date_invoice", False) or self.date_invoice) and self.parent_id:
            date_invoice = vals.get("date_invoice", False) or self.date_invoice
            delta = datetime.strptime(self.parent_id.date_invoice, DEFAULT_SERVER_DATE_FORMAT) - datetime.strptime(
                date_invoice, DEFAULT_SERVER_DATE_FORMAT)
            if delta.days > 30:
                if vals.get("invoice_line", False):
                    for line in vals["invoice_line"]:
                        if line[2].get("invoice_line_tax_id", False):
                            del line[2]["invoice_line_tax_id"]
                for line in self.invoice_line:
                    if line.invoice_line_tax_id:
                        line.invoice_line_tax_id = False
                        self.tax_line = False

        return super(account_invoice, self).write(vals)



