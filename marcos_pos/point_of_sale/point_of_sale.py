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

__author__ = 'eneldoserrata'

from openerp import models, fields, api, exceptions
from openerp.osv import osv, fields as old_fields
from openerp import tools
import openerp
import logging
import time
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime
import threading


_logger = logging.getLogger(__name__)


class pos_config(models.Model):
    _inherit = 'pos.config'

    def check_config_for_sale(self, config):
        if config.payment_pos:
            return True
        return False

    default_partner_id = fields.Many2one("res.partner", "Cliente de contado", help="Asigna este cliente si no hay seleccionado ninguno, siempre para facturas de contado")
    payment_pos = fields.Many2one("pos.config", u"Sesión de pago", help="Elimina las opciones de pago en el POS y envia la factura a la session de pago")
    manager_ids = fields.Many2many("res.users", string="Supervisores", help="Define los usuario que puedes autorizar en el POS")
    pos_cashier = fields.Boolean("Cajero en el POS", help="Permite a la cajera cobrar desde la terminal del POS")
    ipf_printer = fields.Boolean("Utiliza impresora fiscal via chrome plugin", help="Indica que utiliza impresora fiscal via el plugin de chrome")
    ipf_odoo = fields.Boolean("Impresora fiscal via proxy", help="Indica que utiliza impresora fiscal vie el proxy de odoo")
    ipf_host = fields.Many2one("ipf.printer.config", string="IP de la impresora fiscal", help="Indica la ip donde se encuentra la impresora fiscal")
    ipf_ip = fields.Char("Impresora fiscal", related="ipf_host.host", help="Indica la ip donde se encuentra la impresora fiscal")
    iface_orderline_notes = fields.Boolean('Orderline Notes', help='Allow custom notes on Orderlines')

class pos_session(osv.Model):
    _inherit = 'pos.session'

    _columns = {
        "ipf_print": old_fields.related('config_id', 'ipf_printer', readonly=True, type='boolean', relation='pos.config',  string='IPF')
    }

    def _confirm_orders(self, cr, uid, ids, context=None):
        account_move_obj = self.pool.get('account.move')
        pos_order_obj = self.pool.get('pos.order')
        for session in self.browse(cr, uid, ids, context=context):
            local_context = dict(context or {}, force_company=session.config_id.journal_id.company_id.id)
            order_ids = [order.id for order in session.order_ids if order.state == 'paid']

            if not session.config_id.payment_pos:
                move_id = account_move_obj.create(cr, uid,
                                                  {'ref': session.name,
                                                   'journal_id': session.config_id.journal_id.id, },
                                                  context=local_context)

                pos_order_obj._create_account_move_line(cr, uid, order_ids, session, move_id, context=local_context)

                for order in session.order_ids:
                    if order.state == 'done':
                        continue
                    if order.state not in ('paid', 'invoiced', 'cancel', 'refund'):
                        raise osv.except_osv(
                            _('Error!'),
                            _("You cannot confirm all orders of this session, because they have not the 'paid' status"))
                        # pos_order_obj.signal_workflow(cr, uid, [order.id], 'cancel')
                    else:
                        pos_order_obj.signal_workflow(cr, uid, [order.id], 'done')
        return True

    def create(self, cr, uid, values, context=None):
        context = dict(context or {})
        config_id = values.get('config_id', False) or context.get('default_config_id', False)
        if not config_id:
            raise osv.except_osv(_('Error!'),
                                 _("You should assign a Point of Sale to your session."))

        # journal_id is not required on the pos_config because it does not
        # exists at the installation. If nothing is configured at the
        # installation we do the minimal configuration. Impossible to do in
        # the .xml files as the CoA is not yet installed.
        jobj = self.pool.get('pos.config')
        pos_config = jobj.browse(cr, uid, config_id, context=context)
        context.update({'company_id': pos_config.company_id.id})

        if not pos_config.journal_id and not pos_config.payment_pos:
            jid = jobj.default_get(cr, uid, ['journal_id'], context=context)['journal_id']
            if jid:
                jobj.write(cr, openerp.SUPERUSER_ID, [pos_config.id], {'journal_id': jid}, context=context)
            else:
                raise osv.except_osv(_('error!'),
                                     _(
                                         "Unable to open the session. You have to assign a sale journal to your point of sale."))

        # define some cash journal if no payment method exists
        if not pos_config.journal_ids and not pos_config.payment_pos:

            journal_proxy = self.pool.get('account.journal')
            cashids = journal_proxy.search(cr, uid, [('journal_user', '=', True), ('type', '=', 'cash')],
                                           context=context)
            if not cashids:
                cashids = journal_proxy.search(cr, uid, [('type', '=', 'cash')], context=context)
                if not cashids:
                    cashids = journal_proxy.search(cr, uid, [('journal_user', '=', True)], context=context)

            journal_proxy.write(cr, openerp.SUPERUSER_ID, cashids, {'journal_user': True})
            jobj.write(cr, openerp.SUPERUSER_ID, [pos_config.id], {'journal_ids': [(6, 0, cashids)]})

        pos_config = jobj.browse(cr, uid, config_id, context=context)
        bank_statement_ids = []
        for journal in pos_config.journal_ids:
            bank_values = {
                'journal_id': journal.id,
                'user_id': uid,
                'company_id': pos_config.company_id.id
            }
            statement_id = self.pool.get('account.bank.statement').create(cr, uid, bank_values, context=context)
            bank_statement_ids.append(statement_id)

        values.update({
            'name': self.pool['ir.sequence'].get(cr, uid, 'pos.session'),
            'statement_ids': [(6, 0, bank_statement_ids)],
            'config_id': config_id
        })

        return super(osv.osv, self).create(cr, uid, values, context=context)

    def open_cb(self, cr, uid, ids, context=None):
        this_record = self.browse(cr, uid, ids[0], context=context)
        res = super(pos_session, self).open_cb(cr, uid, ids, context=None)
        if not this_record.config_id.payment_pos:
            if not this_record.config_id.pos_cashier:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "pos.order",
                    "views": [[False, "tree"], [False, "form"]],
                    "domain": [("session_id", "=", this_record.id), ("state","=","draft")],
                    "target": "target",
                    "context": context or {},
                    "view_mode": "tree",
                    "view_id": 903
                }
            else:
                return res
        else:
            return res


class pos_order(osv.Model):
    _inherit = "pos.order"

    def _order_fields(self, cr, uid, ui_order, context=None):
        return {
            'name':         ui_order['name'],
            'user_id':      ui_order['user_id'] or False,
            'session_id':   ui_order['pos_session_id'],
            'lines':        ui_order['lines'],
            'pos_reference':ui_order['name'],
            'partner_id':   ui_order['partner_id'] or False,
            'credit_paid':  ui_order.get("credit_paid", 0.00),
            'get_credit_note_ncf': ui_order.get("get_credit_note_ncf", False)
            # 'to_invoice': ui_order.get("to_invoice", False)
        }

    def get_days_between_datetime(self, date1, date2):
        dt1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')
        delta = dt2 - dt1
        return delta.days

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_paid': 0.0,
                'amount_return':0.0,
                'amount_tax':0.0,
            }
            val1 = val2 = 0.0
            cur = order.pricelist_id.currency_id
            for payment in order.statement_ids:
                res[order.id]['amount_paid'] +=  payment.amount
                res[order.id]['amount_return'] += (payment.amount < 0 and payment.amount or 0)
            for line in order.lines:
                val1 += line.price_subtotal_incl
                val2 += line.price_subtotal

            # Dominican rule do not return tax on invoce more than 30 days
            if not order.type == "refund":
                res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val1-val2)
                res[order.id]['amount_total'] = cur_obj.round(cr, uid, cur, val1)
            else:
                days = self.get_days_between_datetime(order.origin.date_order, order.date_order)
                if days > 30:
                    res[order.id]['amount_tax'] = 0
                    res[order.id]['amount_total'] = cur_obj.round(cr, uid, cur, val2)
                else:
                    res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val1-val2)
                    res[order.id]['amount_total'] = cur_obj.round(cr, uid, cur, val1)
        return res

    def _use_ifp_print(self, cr, uid, ids, field, arg, context=None):
        res = {}

        ipf_print = self.browse(cr, uid, ids[0], context=context).session_id.config_id.ipf_printer
        if ipf_print:
            for id in ids:
                res[id] = ipf_print
        else:
            res = False
        return res

    def _default_session(self, cr, uid, context=None):
        so = self.pool.get('pos.session')
        session_ids = so.search(cr, uid, [('state','=', 'opened'), ('user_id','=',uid)], context=context)
        pos_session = so.browse(cr, uid, session_ids, context=context)
        if pos_session.config_id.payment_pos:
            session_ids = so.search(cr, uid, [('state','=', 'opened'), ('config_id','=',pos_session.config_id.payment_pos.id)], context=context)
            return session_ids and session_ids[0] or False

        return super(pos_order, self)._default_session(cr, uid, context=None)

    def _default_pricelist(self, cr, uid, context=None):
        return super(pos_order, self)._default_pricelist(cr, uid, context=None)

    _columns = {
        'amount_tax': old_fields.function(_amount_all, string='Taxes', digits_compute=dp.get_precision('Account'), multi='all'),
        'amount_total': old_fields.function(_amount_all, string='Total', digits_compute=dp.get_precision('Account'),  multi='all'),
        'amount_paid': old_fields.function(_amount_all, string='Paid', states={'draft': [('readonly', False)]}, readonly=True, digits_compute=dp.get_precision('Account'), multi='all'),
        'amount_return': old_fields.function(_amount_all, 'Returned', digits_compute=dp.get_precision('Account'), multi='all'),
        'origin': old_fields.many2one("pos.order", "Orden que afecta", clone=False, readonly=True),
        'state': old_fields.selection([('draft', 'New'),
                                       ('cancel', 'Cancelled'),
                                       ('paid', 'Paid'),
                                       ('done', 'Posted'),
                                       ('invoiced', 'Invoiced'),
                                       ('refund', 'Devuelto')],
                                      'Status', readonly=True, copy=False),
        "ipf_print": old_fields.function(_use_ifp_print, type='boolean'),
        'type': old_fields.selection([('order', 'Order'), ('receipt', 'Receipt'), ('refund', 'Refund')], 'Type',
                                     copy=False, default="order"),
        'credit_paid': old_fields.float(u"Pagado con notas de crédito", readonly=True, copy=False, digits_compute=dp.get_precision('Account'), default=0.00),
        'get_credit_note_ncf': old_fields.char(size=19),
        "nif": old_fields.related("invoice_id", "nif", type="char", string="NIF")
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'state': 'draft',
        'name': '/',
        'date_order': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'nb_print': 0,
        'sequence_number': 1,
        'session_id': _default_session,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'pricelist_id': _default_pricelist,
    }

    def _process_order(self, cr, uid, order, context=None):
        context = context or {}
        if context.get("to_update", False) == True and context.get("order_id", False):

            try:
                pos_statement_ids = self.pool.get("account.bank.statement.line").search(cr, uid, [("pos_statement_id", "=", context.get("order_id", False))])
                self.pool.get("account.bank.statement.line").unlink(cr, uid, pos_statement_ids)
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            order_id = context.get("order_id")[0]
            for payments in order['statement_ids']:
                self.add_payment(cr, uid, order_id, self._payment_fields(cr, uid, payments[2], context=context),
                                 context=context)

            session = self.pool.get('pos.session').browse(cr, uid, order['pos_session_id'], context=context)
            if session.sequence_number <= order['sequence_number']:
                session.write({'sequence_number': order['sequence_number'] + 1})
                session.refresh()

            if order['amount_return']:
                cash_journal = session.cash_journal_id
                if not cash_journal:
                    cash_journal_ids = filter(lambda st: st.journal_id.type == 'cash', session.statement_ids)
                    if not len(cash_journal_ids):
                        raise osv.except_osv(_('error!'),
                                             _("No cash statement found for this session. Unable to record returned cash."))
                    cash_journal = cash_journal_ids[0].journal_id
                self.add_payment(cr, uid, order_id, {
                    'amount': -order['amount_return'],
                    'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'payment_name': _('return'),
                    'journal': cash_journal.id,
                }, context=context)
            return order_id
        elif not order['statement_ids']:
            values = self._order_fields(cr, uid, order, context=context)
            order_id = self.create(cr, uid, values, context)
            if order.get("credit_paid") and order.get("to_invoice") not in ["print_quotation", "send_quotation"]:
                try:
                    self.signal_workflow(cr, uid, [order_id], 'paid')
                except Exception as e:
                    _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

        else:
            return super(pos_order, self)._process_order(cr, uid, order, context=context)

    def create_refund_from_ui(self, cr, uid, tmp_order, context=None):
        context = context or {}
        if tmp_order["data"].get("refund_order_id", False):
            context.update({"type": "refund_form_ui", "order_from_ui": tmp_order})
            context.update({"pos_reference": tmp_order["data"]["name"]})
            result = self.refund(cr, uid, tmp_order["data"]["refund_order_id"], context=context)
            self.signal_workflow(cr, uid, result, 'refund')
            return result


    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders
        context = context or {}
        submitted_references = [o['data']['name'] for o in orders]
        existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
        existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        orders_to_update = [o for o in orders if o['data']['name'] in existing_references]

        order_ids = []

        for tmp_order in orders_to_save:
            payment_session = self.check_payment_session(cr, uid, tmp_order["data"]["pos_session_id"])
            if payment_session:
                tmp_order["data"]["pos_session_id"] = payment_session

            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']

            if tmp_order["data"].get("type", False) == "refund":
                order_id = self.create_refund_from_ui(cr, uid, tmp_order, context=context)
            else:
                order_id = self._process_order(cr, uid, order, context=context)

            order_ids.append(order_id)

            try:
                self.signal_workflow(cr, uid, [order_id], 'paid')
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice == True:
                self.action_invoice(cr, uid, [order_id], context)
                order_obj = self.browse(cr, uid, order_id, context)
                self.pool['account.invoice'].signal_workflow(cr, uid, [order_obj.invoice_id.id], 'invoice_open')

        for tmp_order in orders_to_update:

            order_id = self.search(cr, uid, [('pos_reference', '=', "Pedido "+tmp_order["id"])])
            context.update(dict(to_update=True, order_id=order_id))
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            order_id = self._process_order(cr, uid, order, context=context)
            order_ids.append(order_id)

            try:
                self.signal_workflow(cr, uid, [order_id], 'paid')
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice == True:
                self.action_invoice(cr, uid, [order_id], context)
                order_obj = self.browse(cr, uid, order_id, context)
                self.pool['account.invoice'].signal_workflow(cr, uid, [order_obj.invoice_id.id], 'invoice_open')

        return order_ids

    def check_payment_session(self, cr, uid, pos_session_id, context=None):
        pos_session = self.pool.get("pos.session").browse(cr, uid, pos_session_id)

        if pos_session.config_id.payment_pos:
            payment_pos_id = pos_session.config_id.payment_pos.id
            payment_pos_open = self.pool.get("pos.session").search(cr, uid, [('config_id', '=', payment_pos_id),
                                                                             ('state', '=', 'opened')])
            if payment_pos_open:
                return payment_pos_open[0]
            else:
                raise osv.except_osv(_('Error!'),
                                     _("You should assign a Point of Sale to your session."))
        else:
            return False

    def action_quotation(self, cr, uid, order, context=None):
        context = context or {}
        sale_ref = self.pool.get('sale.order')
        sale_line_ref = self.pool.get('sale.order.line')
        product_obj = self.pool.get('product.product')
        order_ids = []
        session_id = self.pool.get("pos.session").browse(cr, uid, order["pos_session_id"], context=context)
        partner_id = self.pool.get("res.partner").browse(cr, uid, order["partner_id"], context=context)

        order_dict = {'company_id': session_id.config_id.company_id.id,
                      'partner_id': partner_id.id
        }

        order_dict.update(sale_ref.onchange_partner_id(cr, uid, [], order["partner_id"], context=context)['value'])

        order_id = sale_ref.create(cr, uid, order_dict, context=context)

        order_ids.append(order_id)
        for line in order["lines"]:
            product_id = product_obj.browse(cr, uid, line[2]["product_id"], context=context)
            order_line = {
                'order_id': order_id,
                'product_id': product_id.id,
            }

            order_line.update(sale_line_ref.product_id_change_with_wh(cr, uid, [], partner_id.id, False,
                                                                      qty=line[2]["qty"],
                                                                      uom=False, qty_uos=0,
                                                                      uos=False, name='',
                                                                      partner_id=partner_id.id,
                                                                      lang=False,
                                                                      update_tax=True,
                                                                      date_order=False,
                                                                      packaging=False,
                                                                      fiscal_position=False,
                                                                      flag=False,
                                                                      warehouse_id=False,
                                                                      context=None)["value"])
            # order_line['product_uom_qty'] = line[2]["qty"]
            order_line['price_unit'] = line[2]["price_unit"]
            order_line['discount'] = line[2]["discount"]
            sale_line_ref.create(cr, uid, order_line, context=context)

        sale_ref.button_dummy(cr, uid, [order_id], context=context)
        if context.get("action", False) == "print_quotation":
            return sale_ref.print_quotation(cr, uid, [order_id], context=context)
        else:
            action = sale_ref.action_quotation_send(cr, uid, [order_id], context=context)
            return action

    def action_paid(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'paid'}, context=None)
        self.action_invoice(cr, uid, ids, context=context)
        self.create_picking(cr, uid, ids, context=context)
        self.create_statment_move_per_order(cr, uid, ids, context=context)
        return True

    def fiscal_print(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.session_id.config_id.ipf_printer:
                fiscal_interface = self.pool.get("ipf.printer.config")
                fiscal_interface.ipf_print(cr, uid, order.invoice_id.number, context=context)

    def create_statment_move_per_order(self, cr, uid, ids, context=None):
        # 'credit_paid':  ui_order.get("credit_paid", 0.00),
        # 'get_credit_note_ncf': ui_order.get("get_credit_note_ncf", False)
        for order in self.browse(cr, uid, ids, context=context):
            if order.credit_paid > 0.00:
                if order.get_credit_note_ncf:
                    domain = [('number', '=', order.get_credit_note_ncf), ('partner_id', '=', order.partner_id.id), ('type', '=', 'out_refund'), ('residual', '>', 0.00)]
                else:
                    domain = [('partner_id', '=', order.partner_id.id), ('type', '=', 'out_refund'), ('residual', '>', 0.00)]

                if not order.statement_ids:
                    order.credit_paid = order.amount_total

                open_credit_ids = self.pool.get("account.invoice").search(cr, uid, domain)
                open_credit = self.pool.get("account.invoice").browse(cr, uid, open_credit_ids[::-1], context=context)
                credit = order.credit_paid
                active_ids = []
                for inv_move_line in order.invoice_id.move_id.line_id:
                    if inv_move_line.account_id.id == order.partner_id.property_account_receivable.id:
                        active_ids.append(inv_move_line.id)
                    else:
                        continue

                for nc in open_credit:
                    for nc_line in nc.move_id.line_id:
                        if nc_line.account_id.id == order.partner_id.property_account_receivable.id:
                            if credit > 0:
                                active_ids.append(nc_line.id)
                                self.pool.get("account.move.line.reconcile").trans_rec_reconcile_partial_reconcile(cr, uid,
                                    [], context={"active_ids": active_ids})
                                credit -= nc_line.credit
                        else:
                            continue

            for st_line in order.statement_ids:
                move_ids = []
                if not st_line.amount:
                    continue
                if st_line.account_id and not st_line.journal_entry_id.id:
                    cxc_account_id = st_line.pos_statement_id.invoice_id.account_id.id
                    invoice_move_id = st_line.pos_statement_id.invoice_id.move_id.id
                    counterpart_domain = [("move_id", "=", invoice_move_id), ("account_id", "=", cxc_account_id)]
                    counterpart = self.pool.get("account.move.line").search(cr, uid, counterpart_domain)
                    vals = {
                        'debit': st_line.amount < 0 and -st_line.amount or 0.0,
                        'credit': st_line.amount > 0 and st_line.amount or 0.0,
                        'account_id': st_line.account_id.id,
                        'name': st_line.name,
                        'counterpart_move_line_id': counterpart[0]
                    }
                    self.pool.get('account.bank.statement.line').process_reconciliation(cr, uid, st_line.id, [vals],
                                                                                        context={})
                elif not st_line.journal_entry_id.id:
                    raise osv.except_osv(_('Error!'), _(
                        'All the account entries lines must be processed in order to close the statement.'))
                move_ids.append(st_line.journal_entry_id.id)
                if move_ids:
                    self.pool.get('account.move').post(cr, uid, move_ids, context={})

    def action_invoice(self, cr, uid, ids, context=None):
        context = context or {}
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        inv_ids = []

        for order in self.pool.get('pos.order').browse(cr, uid, ids, context=context):

            invoice_type = 'out_invoice'
            state = "invoiced"
            if order.amount_total < 0:
                invoice_type = 'out_refund'
                state = "refund"

            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue

            if not order.partner_id:
                raise osv.except_osv(_('Error!'), _('Please provide a partner for the sale.'))

            acc = order.partner_id.property_account_receivable.id

            inv = {
                'name': order.name,
                'origin': order.name,
                'account_id': acc,
                # 'journal_id': order.sale_journal.id or None,
                'type': invoice_type,
                'reference': "PTV",
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'currency_id': order.pricelist_id.currency_id.id,  # considering partner's sale pricelist's currency
                'parent_id': order.origin.invoice_id.id or False
            }

            inv.update(inv_ref.onchange_partner_id(cr, uid, [], invoice_type, order.partner_id.id)['value'])
            if not inv.get('account_id', None):
                inv['account_id'] = acc

            invoice_lines = []
            for line in order.lines:
                inv_line = {
                    # 'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty if line.qty > 0 else line.qty * -1,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'origin': line.id
                }
                # inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.product_id.id,
                                                               line.product_id.uom_id.id,
                                                               line.qty, partner_id=order.partner_id.id,
                                                               fposition_id=order.partner_id.property_account_position.id)['value'])
                if not inv_line.get('account_analytic_id', False):
                    inv_line['account_analytic_id'] = self._prepare_analytic_account(cr, uid, line,context=context)

                # inv_line['name'] = inv_name

                if not line.order_id.type == "refund":
                    inv_line['invoice_line_tax_id'] = [(6, 0, [x.id for x in line.product_id.taxes_id] )]
                elif line.order_id.type == "refund":
                    days = self.get_days_between_datetime(line.order_id.origin.date_order, line.order_id.date_order)
                    if days > 30:
                        inv_line['invoice_line_tax_id'] = False
                    else:
                        inv_line['invoice_line_tax_id'] = [(6, 0, [x.id for x in line.product_id.taxes_id] )]

                invoice_lines.append((0,False, inv_line))
                # inv_line_ref.create(cr, uid, inv_line, context=context)
            inv.update({"invoice_line": invoice_lines})
            inv_id = inv_ref.create(cr, uid, inv, context=context)
            order.sale_journal = inv_ref.browse(cr, uid, inv_id).journal_id.id
            inv_ref.button_reset_taxes(cr, uid, [inv_id], context=context)
            self.signal_workflow(cr, uid, [order.id], 'invoice')
            inv_ref.signal_workflow(cr, uid, [inv_id], 'validate')
            inv_ref.signal_workflow(cr, uid, [inv_id], 'invoice_open')
            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': state}, context=context)
            inv_ids.append(inv_id)


        if not inv_ids: return {}

        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False

        res = {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'account.invoice',
            'context': "{'type': %s}" % invoice_type,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': inv_ids and inv_ids[0] or False,
        }

        return res

    def refund(self, cr, uid, ids, context=None):
        """Create a copy of order  for refund order"""
        clone_list = []
        line_obj = self.pool.get('pos.order.line')

        for order in self.browse(cr, uid, ids, context=context):
            if order.amount_total <= 0 and not context.get("type", False) == "refund_form_ui":
                raise osv.except_osv(_('Advertencia!'), _(
                    u'Esta acción no esta permitida! no puede hacer una devolución a una nota de crédito.'))

            current_session_ids = self.pool.get('pos.session').search(cr, uid, [
                ('state', '!=', 'closed'),
                ('user_id', '=', uid)], context=context)
            if not current_session_ids:
                raise osv.except_osv(_('Warning!'), _(
                    'To return product(s), you need to open a session that will be used to register the refund.'))

            clone_id = self.copy(cr, uid, order.id, {
                'name': order.name + ' REFUND',  # not used, name forced by create
                'session_id': current_session_ids[0],
                'date_order': time.strftime('%Y-%m-%d %H:%M:%S'),
                'origin': order.id,
                'type': 'refund',
                'lines': False,
                'pos_reference': context.get("pos_reference", False)
            }, context=context)
            clone_list.append(clone_id)

            refund_lines = []
            if context.get("type", False) == "refund_form_ui":
                for line in context["order_from_ui"]["data"]["lines"]:
                    refund_lines.append((0,0, {
                        "product_id": line[2]["product_id"],
                        "price_unit": line[2]["price_unit"],
                        "qty": line[2]["qty"]*-1,
                        "discount": line[2]["discount"],
                        "order_id": clone_id,
                        "origin": line[2]["origin_id"]
                    }))
            else:
                for line in order.lines:
                    if line.qty-line.return_qty == 0:
                        continue
                    refund_lines.append((0,0, {
                        "notice": line.notice,
                        "product_id": line.product_id.id,
                        "price_unit": line.price_unit,
                        "qty": (line.qty-line.return_qty)*-1,
                        "discount": line.discount,
                        "order_id": clone_id,
                        "origin": line.id
                    }))

        if refund_lines:
            self.write(cr, uid, clone_list, {"lines": refund_lines}, context=context)
        else:
            raise exceptions.Warning("Los productos de esta factura ya fueron todos devuelto!")

        if context.get("type", False) == "refund_form_ui":
            return clone_list

        abs = {
            'name': _('Return Products'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'res_id': clone_list[0],
            'view_id': False,
            'context': context,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }
        return abs

    def create_picking(self, cr, uid, ids, context=None):
        res = super(pos_order, self).create_picking(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            order.picking_id.invoice_id = order.invoice_id.id
            if order.amount_total < 0:
                order.picking_id.afecta = order.invoice_id
        return res

    def test_paid(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.lines and not order.amount_total:
                return True

            if order.credit_paid > 0:
                return True

            if (not order.lines) or (abs(order.amount_total-(order.amount_paid+order.credit_paid)) > 0.00001):
                return False
        return True

    def update_refund_qty_on_origin(self, cr, uid, ids, context=None):
        order = self.pool.get("pos.order").browse(cr, uid, ids, context=context)
        for line in order.lines:
            if line.qty >= 0:
                raise exceptions.Warning("Las cantidades para una devolucion deben de ser negativas!")

            qty_available_to_refund = line.origin.qty + line.origin.return_qty
            if (line.qty*-1) > qty_available_to_refund:
                exceptions.Warning("Del producto {} solo puede la cantidad de {}!".format(line.product_id, qty_available_to_refund))

            qty_refund_update = (line.qty*-1) + line.origin.return_qty
            self.pool.get("pos.order.line").write(cr, uid, line.origin.id, {"return_qty": qty_refund_update})

    def action_refund(self, cr, uid, ids, context=None):

        self.update_refund_qty_on_origin(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'refund'}, context=None)
        self.action_invoice(cr, uid, ids, context=context)
        self.create_picking(cr, uid, ids, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if context.get("active_id", False):
            order_to_copy = self.pool.get("pos.order").browse(cr, uid, context["active_id"], context=context)
            if order_to_copy.type == "refund":
                raise exceptions.Warning("No esta permitido duplicar notas de credito!")

        return super(pos_order, self).copy(cr, uid, id, default=default, context=context)

    def get_ncf_info(self, cr, uid, pos_reference, context={}):
        res = {}
        order_id = self.pool.get("pos.order").search(cr, uid, [("pos_reference", "like", pos_reference)])
        order = self.browse(cr, uid, order_id)
        if order:
            res = {"ncf_type": order.invoice_id.journal_id.name, "ncf": order.invoice_id.number}
        return res


class pos_order_line(osv.Model):
    _inherit = "pos.order.line"

    # def onchange_qty(self, cr, uid, ids, product, discount, qty, price_unit, context=None):
    #     result = {}
    #     if not product:
    #         return result
    #     account_tax_obj = self.pool.get('account.tax')
    #     cur_obj = self.pool.get('res.currency')
    #
    #     prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
    #
    #     price = price_unit * (1 - (discount or 0.0) / 100.0)
    #     partner_id = self.browse(cr, uid, ids).order_id.partner_id
    #     taxes = account_tax_obj.compute_all(cr, uid, prod.taxes_id, price, qty, product=prod, partner=partner_id)
    #
    #     result['price_subtotal'] = taxes['total']
    #     result['price_subtotal_incl'] = taxes['total_included']
    #     return {'value': result}

    def _check_orderline_stock(self, cr, uid, ids, context=None):
        inventory_obj = self.pool.get('stock.inventory.report')
        for obj in self.browse(cr, uid, ids, context=context):
            inventory_ids = inventory_obj.search(cr, uid, [('product_id', '=', obj.product_id.id), \
                                                           ('location_id', '=',
                                                            obj.order_id.session_id.config_id.stock_location_id.id)])
            if not inventory_ids:
                return False
            else:
                tot_stock = 0
                for inventory in inventory_obj.browse(cr, uid, inventory_ids):
                    tot_stock += inventory.qty
                if obj.qty > tot_stock:
                    return False
        return True

    def _amount_line_all(self, cr, uid, ids, field_names, arg, context=None):
        res = dict([(i, {}) for i in ids])
        account_tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            taxes_ids = [ tax for tax in line.product_id.taxes_id if tax.company_id.id == line.order_id.company_id.id ]
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            taxes = account_tax_obj.compute_all(cr, uid, taxes_ids, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id]['price_subtotal'] = taxes['total']
            if line.order_id.partner_id.property_account_position.fiscal_type == 'special':
                res[line.id]['price_subtotal_incl'] = taxes['total']
            else:
                res[line.id]['price_subtotal_incl'] = taxes['total_included']

        return res

    _columns = {
        'price_subtotal': old_fields.function(_amount_line_all, multi='pos_order_line_amount', digits_compute=dp.get_precision('Product Price'), string='Subtotal w/o Tax', store=True),
        'price_subtotal_incl': old_fields.function(_amount_line_all, multi='pos_order_line_amount', digits_compute=dp.get_precision('Account'), string='Subtotal', store=True),
        'return_qty': old_fields.float('Devultos', digits_compute=dp.get_precision('Product UoS'), default=0.00, copy=False),
        'note': old_fields.char('Nota'),
        'origin': old_fields.many2one("pos.order.line", string="Origen de la devolucion", copy=False)
    }


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def create_from_ui(self, cr, uid, partner, context=None):
        fiscal_position = partner.get("fiscal_position", False)
        if fiscal_position:
            fiscal_position = self.pool.get("account.fiscal.position").search(cr, uid, [('fiscal_type','=', fiscal_position)])
            if fiscal_position:
                partner.update({"property_account_position": fiscal_position[0]})
        return super(res_partner, self).create_from_ui(cr, uid, partner, context=context)

