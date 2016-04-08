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
from openerp.osv import fields, orm
from openerp import netsvc
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm

class account_cash_statement(orm.Model):
    _inherit = "account.bank.statement"

    def _all_lines_reconciled(self, cr, uid, ids, name, args, context=None):

        res = super(account_cash_statement, self)._all_lines_reconciled(cr, uid, ids, name, args, context=None)
        if context.get("journal_type", False) == "cash" and res:
            for key in res.keys():
                res[key] = True
        return res

    def journal_id_change(self, cr, uid, ids, journal_id):
        is_cjc = self.pool.get("account.journal").browse(cr, uid, journal_id).is_cjc
        return {"value": {"is_cjc": is_cjc}}

    _columns = {
        "is_cjc": fields.boolean("Control de caja chica", readonly=False),
        'all_lines_reconciled': fields.function(_all_lines_reconciled, string='All lines reconciled', type='boolean'),
    }

    def create_invoice_wizard(self, cr, uid, ids, context=None):
        view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'marcos_cjc', 'cjc_wizard_view_form')[1]
        wizard = {
            'name': 'Gasto de caja chica',
            'view_mode': 'form',
            'view_id': False,
            'views': [(view_id, 'form')],
            'view_type': 'form',
            'res_model': 'cjc.invoice.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }
        return wizard

    def button_confirm_cash(self, cr, uid, ids, context=None):
        statement = self.browse(cr, uid, ids)[0]
        if statement.journal_id.is_cjc and context:
            wf_service = netsvc.LocalService("workflow")
            # invoiced = []
            uninvoiced = []
            for statement in self.browse(cr, uid, ids):
                for line in statement.line_ids:
                    # if line.invoice_id:
                    #     invoiced.append(line.invoice_id.id)
                    if not line.invoice_id and line.amount < 0:
                        uninvoiced.append(line)

            # for inv_id in invoiced:
            # wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)

            journal = statement.journal_id
            minor_journal = journal.gastos_journal_id
            minor_partner = minor_journal.special_partner
            minor_product = minor_journal.special_product

            vals = {}
            vals.update({
                u'account_id': journal.default_credit_account_id.id,
                u'check_total': 0,
                u'child_ids': [[6, False, []]],
                u'comment': "Gasto menor generado por caja chica",
                u'company_id': 1,
                u'currency_id': journal.company_id.currency_id.id,
                u'date_due': False,
                u'date_invoice': statement.date,
                u'fiscal_position': minor_partner.property_account_position.id,
                u'internal_number': False,
                u'journal_id': minor_journal.id,
                u'message_follower_ids': False,
                u'message_ids': False,
                u'name': False,
                u'ncf_required': False,
                u'origin': statement.name,
                u'parent_id': False,
                u'partner_bank_id': False,
                u'partner_id': minor_partner.id,
                u'payment_term': False,
                u'period_id': statement.period_id.id,
                u'reference': False,
                u'reference_type': "02",
                u'supplier_invoice_number': False,
                u'tax_line': [],
                u'user_id': uid,
                u'pay_to': statement.journal_id.pay_to.id,
                u'invoice_line': []
            })
            if uninvoiced:
                if not minor_product.property_account_expense.id and statement.journal_id.is_cjc:
                    raise ValidationError(u"En el diario de gasto menor seleccionado para esta caja chica "
                                          u"el producto {} utilizado por defecto no tiene la cuenta de gasto asignada!".format(
                        minor_product.name))
                line_ids = []

                for line in uninvoiced:
                    line.account_id = journal.default_credit_account_id
                    line_ids.append(line.id)
                    line_list = [0, False]
                    line_dict = {}
                    line_dict.update({
                        u'account_analytic_id': False,
                        u'account_id': minor_product.property_account_expense.id,
                        u'asset_category_id': False,
                        u'discount': 0,
                        u'invoice_line_tax_id': [[6, False, [t.id for t in minor_product.supplier_taxes_id]]],
                        u'name': line.name,
                        u'price_unit': abs(line.amount),
                        u'product_id': minor_product.id,
                        u'quantity': 1,
                        u'uos_id': 1
                    })
                    line_list.append(line_dict)
                    vals["invoice_line"].append(line_list)

                if statement.journal_id.is_cjc:
                    context = {u'default_type': u'in_invoice', u'journal_type': u'purchase', u"minor": True}
                inv_id = self.pool.get("account.invoice").create(cr, uid, vals, context=context)
                inv = self.pool.get("account.invoice").browse(cr, uid, inv_id)
                inv.check_total = inv.amount_total
                wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
                self.pool.get("account.bank.statement.line").write(cr, uid, line_ids, {"invoice_id": inv_id, "partner_id": minor_partner.id, "ref": inv.number})

        res = super(account_cash_statement, self).button_confirm_bank(cr, uid, ids, context=context)
        if statement.journal_id.is_cjc and context:
            for move in statement.move_line_ids:
                if move.credit > 0:
                    self.pool.get("account.move.line").write(cr, uid, move.id,
                                                             {"partner_id": statement.journal_id.pay_to.id})

            for statement in self.browse(cr, uid, ids):
                for line in statement.line_ids:

                    number = line.invoice_id.number
                    account_id = line.account_id.id
                    partner_id = line.partner_id.id
                    cjc_journal = line.journal_id.id
                    inv_journal = line.invoice_id.journal_id.id
                    move_line_ids = []
                    move_line_ids += self.pool.get("account.move.line").search(cr, uid, [('ref', '=', number),
                                                                                        ('account_id', '=', account_id),
                                                                                        ('partner_id', '=', partner_id),
                                                                                        ('journal_id', '=', cjc_journal),
                                                                                        ('debit', '>', 0)
                                                                                        ])
                    move_line_ids += self.pool.get("account.move.line").search(cr, uid, [('ref', '=', number),
                                                                                        ('account_id', '=', account_id),
                                                                                        ('partner_id', '=', partner_id),
                                                                                        ('journal_id', '=', inv_journal),
                                                                                        ('credit', '>', 0)
                                                                                        ])


                    try:
                        self.pool.get("account.move.line.reconcile").trans_rec_reconcile_full(cr, uid, ids, {"active_ids": move_line_ids})
                    except except_orm as e:
                        if e.value.startswith("El apunte ya est"):
                            pass
                        else:
                            raise e

        return res


class account_bank_statement_line(orm.Model):
    _inherit = "account.bank.statement.line"

    _columns = {
        "invoice_id": fields.many2one("account.invoice", "Factura", copy=False)
    }

    # def unlink(self, cr, uid, ids, context=None):
    #     context = context or {}
    #     for line in self.browse(cr, uid, ids):
    #         if context.get("journal_type", False) == "cash" and line.invoice_id:
    #             self.pool.get("account.invoice").unlink(cr, uid, [line.invoice_id.id], context=context)
    #
    #     return super(account_bank_statement_line, self).unlink(cr, uid, ids, context=context)

    def view_invoice(self, cr, uid, ids, context=None):
        """
        Method to open create customer invoice form
        """

        record = self.browse(cr, uid, ids, context=context)

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
        view_id = view_ref[1] if view_ref else False

        res = {
            'type': 'ir.actions.act_window',
            'name': 'Supplier Invoice',
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            "res_id": record.invoice_id.id,
        }

        return res
