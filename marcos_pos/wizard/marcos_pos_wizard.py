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

from openerp.osv import osv
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
import time
import openerp.addons.decimal_precision as dp

class pos_cancel_order(models.TransientModel):
    _name = "pos.cancel.order"

    why = fields.Char("Motivo")
    manager = fields.Char("Clave", required=True)

    @api.multi
    def check(self):
        cr, uid, context = self.env.cr, self.env.uid, self.env.context
        for action in self:

            manager = self.pool.get("res.users").search_read(cr, uid, [('short_pwd', '=', action.manager)])
            if manager:
                if context.get("refund", False):
                    return self.pool.get("pos.order").refund(cr, uid, context.get("active_ids"), context=context)
                else:
                    self.pool.get("pos.order").write(cr, uid, context.get("active_id"), {
                        "note": "Cancelada por: {} / {}".format(manager[0].get("display_name"), action.why)})
                    self.pool.get("pos.order").signal_workflow(cr, uid, context.get("active_ids"), 'cancel')
            else:
                if context.get("refund", False):
                    dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'marcos_pos', 'marcos_wizard_pos_refund_order')
                else:
                    dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'marcos_pos', 'marcos_wizard_pos_cancel_order')
                return {
                    'name': _('Cancelar orden'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'pos.cancel.order',
                    'res_id': action.id,
                    'view_id': view_id,
                    'target': 'new',
                    'views': False,
                    'type': 'ir.actions.act_window',
                    'context': self.env.context,
                }


class pos_session_opening(osv.osv_memory):
    _inherit = 'pos.session.opening'

    def open_ui(self, cr, uid, ids, context=None):
        this_record = self.browse(cr, uid, ids[0], context=context)
        res = super(pos_session_opening, self).open_ui(cr, uid, ids, context=context)
        if not this_record.pos_config_id.payment_pos:
            if not this_record.pos_config_id.pos_cashier:
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "pos.order",
                    "views": [[False, "tree"], [False, "form"]],
                    "domain": [("session_id", "=", this_record.pos_session_id.id), ("state","=","draft")],
                    "target": "target",
                    "context": context or {},
                    "view_mode": "tree",
                    "view_id": 903
                }
            else:
                return res
        else:
            return res


class pos_payment(models.TransientModel):
    _name = "pos.payment"

    @api.model
    def _default_journal(self):
        cr, uid, context = self.env.cr, self.env.uid, self.env.context
        session = False
        order_obj = self.pool.get('pos.order')
        active_id = context and context.get('active_id', False)
        if active_id:
            order = order_obj.browse(cr, uid, active_id, context=context)
            session = order.session_id
        if session:
            for journal in session.config_id.journal_ids:
                return journal.id
        return False

    @api.model
    def _default_amount(self):
        cr, uid, context = self.env.cr, self.env.uid, self.env.context
        order_obj = self.pool.get('pos.order')
        active_id = context and context.get('active_id', False)
        if active_id:
            order = order_obj.browse(cr, uid, active_id, context=context)
            return order.amount_total - (order.amount_paid+order.credit_paid)
        return False

    def _get_payment_options(self):
        if self._context.get('pos_session_id'):
            config_id = self.env["pos.session"].browse(self.env.context.get('pos_session_id')).config_id
            payments_id = [journal.id for journal in config_id.journal_ids]
            domain = [('id','in', payments_id)]
            return domain
        return []

    @api.model
    def _is_credit_note(self):
        cr, uid, context = self.env.cr, self.env.uid, self.env.context
        order_obj = self.pool.get('pos.order')
        active_id = context and context.get('active_id', False)
        if active_id:
            order = order_obj.browse(cr, uid, active_id, context=context)
            return order.amount_total < 0

    def _check_open_credit(self):
        sql = """
        SELECT   "pos_order"."id",
         "account_invoice"."date_invoice",
         "account_invoice"."number",
         "account_invoice"."residual",
         "account_invoice"."type"
        FROM     "account_invoice"
                  INNER JOIN "pos_order"  ON "account_invoice"."partner_id" = "pos_order"."partner_id"
        WHERE    ( "residual" > 0.00 ) AND ( "account_invoice"."type" = 'out_refund' ) AND ("pos_order"."id" = %(active_id)s)
        """
        self.env.cr.execute(sql, dict(active_id=self._context.get("active_id")))
        res = self.env.cr.fetchall()
        if res:
            return res

        return False

    @api.model
    def _default_open_credit(self):

        amount = 0.00

        res = self._check_open_credit()
        if res:
            amount += sum([rec[3] for rec in res])

        if self._context.get('active_id', False):
            order = self.env["pos.order"].browse(self._context["active_id"])
            amount -= order.credit_paid

        return amount

    is_credit_note = fields.Boolean(default=_is_credit_note)
    refund_money = fields.Boolean("Devolver dinero o reversar pago", default=False)
    manager_pwd = fields.Char("Clave del supervisor")
    journal_id = fields.Many2one("account.journal", string="Formas de pago", default=_default_journal, domain=_get_payment_options)
    amount = fields.Float('Monto', digits=(16, 2), default=_default_amount)
    payment_name = fields.Char('Referencias')
    payment_date = fields.Date('Payment Date', required=True, default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
    journal_type = fields.Char("Tipo de diario")
    open_credit = fields.Float(u"Aplicar crédito", readonly=True, default=_default_open_credit, digits_compute=dp.get_precision('Account'))

    @api.onchange("journal_id")
    def onchange_journal_id(self):
        self.journal_type = self.journal_id.type

    @api.multi
    def apply_payment(self):

        cr, uid, context = self.env.cr, self.env.uid, self.env.context or {}

        order_obj = self.pool.get('pos.order')
        active_id = context and context.get('active_id', False)

        order = order_obj.browse(cr, uid, active_id, context=context)
        amount = order.amount_total - (order.amount_paid + order.credit_paid)
        data = self.read()[0]

        data.update({'journal': data['journal_id'][0]})
        if context.get("nc", False):
            credits = self._check_open_credit()
            credit_amount = sum([rec[3] for rec in credits])
            if credit_amount >= order.amount_total:
                order.credit_paid = order.amount_total
            else:
                order.credit_paid = credit_amount
        elif self.refund_money == False and self.is_credit_note == False:
            if amount > 0.0:
                order_obj.add_payment(cr, uid, active_id, data, context=context)
            else:
                raise exceptions.Warning(u"El valor del pago no puede ser menor o igual 0.00!")
        elif self.refund_money == False and self.is_credit_note == True:
            if amount < 0.0:
                order_obj.signal_workflow(cr, uid, [active_id], 'refund')
                return {'type': 'ir.actions.act_window_close'}
            else:
                raise exceptions.Warning(u"El valor del pago no puede ser mayor o igual 0.00 para una nota de crédito!")
        elif self.refund_money == True and self.is_credit_note == True:
            if amount < 0.0:
                manager = self.env["res.users"].search([('short_pwd', '=', self.manager_pwd)])
                permissions = self.env["pos.manager"].search([('users', '=', manager.id)])

                if manager and permissions.cash_refund:
                    order_obj.add_payment(cr, manager.id, active_id, data, context=context)
                else:
                    raise exceptions.Warning(u"No tiene permiso para devolver dinero de una nota de crédito!!")
            else:
                raise exceptions.Warning(u"El valor del pago no puede ser mayor o igual 0.00 para una nota de crédito!")

        if order_obj.test_paid(cr, uid, [active_id]):
            if amount != 0.0:
                order_obj.signal_workflow(cr, uid, [active_id], 'paid')

            if order.session_id.config_id.ipf_printer:
                return self.launch_ipf_print(order.id)
            else:
                return {'type': 'ir.actions.act_window_close'}

        return self.launch_payment(self.is_credit_note)

    def launch_payment(self, is_credit_note):

        if not is_credit_note:
            view_id = self.env['ir.ui.view'].search([('name', '=', 'marcos.pos.payment.option.wizard.form')], limit=1).id
        else:
            view_id = self.env['ir.ui.view'].search([('name', '=', 'marcos.pos.refund.option.wizard.form')], limit=1).id
        return {
            'name': _('Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.payment',
            'view_id': view_id,
            'target': 'new',
            'views': False,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
        }

    @api.model
    def launch_ipf_print(self, order_id):
        cr, uid, context = self.env.cr, self.env.uid, self.env.context
        view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, "marcos_pos", 'marcos_view_confirm_print_fiscal_invoice')[1]
        return {
            'name': "",
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.payment',
            'view_id': view_id,
            'target': 'new',
            'views': False,
            'type': 'ir.actions.act_window',
            'context': {"model": "pos.order", "id": order_id}
        }

