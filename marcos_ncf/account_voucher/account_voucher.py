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

from openerp.osv import osv, fields
from number_to_letter import to_word as amount_to_text
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class account_voucher(osv.Model):
    _inherit = 'account.voucher'

    def _get_journal(self, cr, uid, context=None):
        return super(account_voucher, self)._get_journal(cr, uid, context=context)


    _columns = {
        "authorized": fields.boolean("Authorized?", help="Voucher must be authorized before been validated."),
    }

    _defaults = {
        'journal_id': _get_journal
    }

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date,
                        payment_rate_currency_id, company_id, context=None):
        """ Inherited - add amount_in_word and allow_check_writting in returned value dictionary """
        if not context:
            context = {}
        default = super(account_voucher, self).onchange_amount(cr, uid, ids, amount, rate, partner_id, journal_id,
                                                               currency_id, ttype, date, payment_rate_currency_id,
                                                               company_id, context=context)
        if 'value' in default:
            amount = 'amount' in default['value'] and default['value']['amount'] or amount

            # Currency complete name is not available in res.currency model
            # Exceptions done here (EUR, USD, BRL) cover 75% of cases
            # For other currencies, display the currency code
            currency = self.pool['res.currency'].browse(cr, uid, currency_id, context=context)
            if currency.name.upper() == 'EUR':
                currency_name = 'Euro'
            elif currency.name.upper() == 'USD':
                currency_name = 'Dollars'
            elif currency.name.upper() == 'BRL':
                currency_name = 'reais'
            else:
                currency_name = currency.name
            # TODO : generic amount_to_text is not ready yet, otherwise language (and country) and currency can be passed
            # amount_in_word = amount_to_text(amount, context=context)
            amount_in_word = amount_to_text(amount, "pesos")
            default['value'].update({'amount_in_word': amount_in_word})
            if journal_id:
                allow_check_writing = self.pool.get('account.journal').browse(cr, uid, journal_id,
                                                                              context=context).allow_check_writing
                default['value'].update({'allow_check': allow_check_writing})
        return default

    def action_authorize(self, cr, uid, ids, context=None):
        """
        This function will mark the voucher as authorized for validation.

        """

        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        voucher = self.pool.get('account.voucher').browse(cr, uid, ids, context)[0]
        voucher.write({'authorized': True}, context=context)
        return True

    def print_receipt(self, cr, uid, ids, context=None):
        """
        This function prints the customer receipt.

        """

        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        datas = {
                 'model': 'account.voucher',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'marcos.customer.receipt', 'datas': datas, 'nodestroy': True}

    def print_check_request(self, cr, uid, ids, context=None):
        """
        This function prints the check request.

        """

        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        datas = {
                 'model': 'account.voucher',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'marcos.check.request', 'datas': datas, 'nodestroy': True}

    def print_check(self, cr, uid, ids, context=None):
        if not ids:
            raise osv.except_osv(_('Printing error'), _('No check selected '))

        data = {
            'id': ids and ids[0],
            'ids': ids,
        }

        return self.pool['report'].get_action(
            cr, uid, [], 'account_check_writing.report_check', data=data, context=context
        )

    def remove_auto_paymment(self, cr, uid, ids, context=None):
            voucher_line_obj = self.pool.get("account.voucher.line")
            lines_dr = [line.id for line in self.browse(cr, uid, ids[0]).line_dr_ids]
            lines_cr = [line.id for line in self.browse(cr, uid, ids[0]).line_cr_ids]
            voucher_line_obj.write(cr, uid, lines_dr+lines_cr, {"amount": 0.00, "reconcile": False}, context=context)
            return True

    def action_move_line_create(self, cr, uid, ids, context=None):
        voucher_line_obj = self.pool.get("account.voucher.line")
        line_to_remove_ids = []
        for line in self.browse(cr, uid, ids[0]).line_dr_ids+self.browse(cr, uid, ids[0]).line_cr_ids:
            if line.amount == 0:
                line_to_remove_ids.append(line.id)
        voucher_line_obj.unlink(cr, uid, line_to_remove_ids)
        return super(account_voucher, self).action_move_line_create(cr, uid, ids, context=context)

    def cancel_voucher(self, cr, uid, ids, context=None):
        lines_obj = self.pool.get("account.voucher.line")
        line_ids = lines_obj.search(cr, uid, [("voucher_id", "in", ids)])
        if line_ids:
            lines_obj.unlink(cr, uid, line_ids)

        return super(account_voucher, self).cancel_voucher(cr, uid, ids, context=context)