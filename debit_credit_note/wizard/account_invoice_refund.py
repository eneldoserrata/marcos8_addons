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
from openerp.exceptions import except_orm

from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import netsvc
from openerp.osv.orm import browse_null
import time
import openerp.addons.decimal_precision as dp
import datetime


class account_invoice_refund(osv.osv_memory):
    """Refunds invoice"""
    _inherit = 'account.invoice.refund'

    def _check_ncf(self, cr, uid, ids):
        # for refund in self.browse(cr, uid, ids):
        #     if refund.journal_id.type == "purchase_refund":
        #         if is_ncf(refund.ncf, "in_refund"):
        #             return True
        #         else:
        #             return False
        return True

    def _get_reason(self, cr, uid, context=None):
        active_id = context and context.get('active_id', False)
        if active_id:
            inv = self.pool.get('account.invoice').browse(cr, uid, active_id, context=context)
            return inv.name
        else:
            return ''

    def _get_journal(self, cr, uid, context=None):
        if context.get("type", False) == "out_invoice":
            invoice = self.pool.get("account.invoice").browse(cr, uid, context["active_id"])
            return invoice.shop_ncf_config_id.nc
        obj_journal = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        if context is None:
            context = {}
        inv_type = context.get('type', 'out_invoice')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        type = (inv_type == 'out_invoice') and 'sale_refund' or \
               (inv_type == 'out_refund') and 'sale' or \
               (inv_type == 'in_invoice') and 'purchase_refund' or \
               (inv_type == 'in_refund') and 'purchase'
        journal = obj_journal.search(cr, uid, [('type', '=', type), ('company_id', '=', company_id)], limit=1,
                                     context=context)
        return journal and journal[0] or False

    def _is_discount(self, cr, uid, ids, filter_refund, *a):

        if filter_refund == "desc":
            return {"value": {"is_discount": True}}
        else:
            return {"value": {"is_discount": False}}

    _columns = {
        'is_discount': fields.boolean(default=False),
        'filter_refund': fields.selection([
                                          ('desc', 'Aplicar un descuento'),
                                          ('refund', 'Create a draft refund'),
                                          ('cancel', 'Cancel: create refund and reconcile'),
                                          ('modify', 'Modify: create refund, reconcile and create a new draft invoice')
                                          ],
                                          "Refund Method", required=True,
                                          help='Refund base on this type. You can not Modify and Cancel if the invoice'
                                               ' is already reconciled'),
        "ncf": fields.char("NCF Proveedor", size=19),
        "discount_value": fields.char('Monto del descuento', digits_compute=dp.get_precision('Account')),
        'date': fields.date('Date', required=True,  help='This date will be used as the invoice date for credit note and period will be chosen accordingly!'),

    }

    _constraints = [(_check_ncf, u'El número de comprobante fiscal para la nota de crédito no es válido!', ['ncf'])]

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'journal_id': _get_journal,
        'filter_refund': 'desc',
        'description': _get_reason,
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False,
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        user_obj = self.pool.get('res.users')
        # remove the entry with key 'form_view_ref', otherwise fields_view_get
        # crashes
        # context.pop('form_view_ref', None)
        res = super(account_invoice_refund, self). \
            fields_view_get(cr, uid,
                            view_id=view_id,
                            view_type=view_type,
                            context=context,
                            toolbar=toolbar, submenu=submenu)
        type = context.get('type', 'out_invoice')
        company_id = user_obj.browse(
            cr, uid, uid, context=context).company_id.id
        journal_type = (type == 'out_invoice') and 'sale_refund' or \
                       (type == 'out_refund') and 'sale' or \
                       (type == 'in_invoice') and 'purchase_refund' or \
                       (type == 'in_refund') and 'purchase'
        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(cr, uid, '',
                                                          [('type', '=',
                                                            journal_type),
                                                           ('company_id',
                                                            'child_of',
                                                            [company_id])],
                                                          context=context)
                res['fields'][field]['selection'] = journal_select
        return res

    def _get_period(self, cr, uid, context={}):
        """
        Return  default account period value
        """
        account_period_obj = self.pool.get('account.period')
        ids = account_period_obj.find(cr, uid, context=context)
        period_id = False
        if ids:
            period_id = ids[0]
        return period_id

    def _get_orig(self, cr, uid, inv, context={}):
        """
        Return  default origin value
        """
        nro_ref = ''
        if inv.type == 'out_invoice':
            nro_ref = inv.number
        orig = _('INV REFUND:') + (nro_ref or '') + _('- DATE:') + (
            inv.date_invoice or '') + (' TOTAL:' + str(inv.amount_total) or '')
        return orig

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs

        """
        inv_obj = self.pool.get('account.invoice')
        refund_obj = self.pool.get('account.invoice')
        reconcile_obj = self.pool.get('account.move.reconcile')
        account_m_line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        wf_service = netsvc.LocalService('workflow')
        inv_tax_obj = self.pool.get('account.invoice.tax')
        inv_line_obj = self.pool.get('account.invoice.line')
        res_users_obj = self.pool.get('res.users')
        if context is None:
            context = {}

        for form in self.browse(cr, uid, ids, context=context):
            created_inv = []
            company = res_users_obj.browse(cr, uid, uid, context=context).company_id
            journal_id = form.journal_id.id
            for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise osv.except_osv(_('Error!'), _('Cannot %s draft/proforma/cancel invoice.') % (mode))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise osv.except_osv(_('Error!'), _('Cannot %s invoice which is already reconciled, '
                                                        'invoice should be unreconciled first. You can only '
                                                        'refund this invoice.') % (mode))

                if form.date:
                    period = self.pool.get("account.period").find(cr, uid, dt=form.date, context=context)[0]
                elif form.period.id:
                    period = form.period.id
                else:
                    period = inv.period_id and inv.period_id.id or False
                if not journal_id:
                    journal_id = inv.journal_id.id

                date = form.date

                if form.description:
                    description = form.description
                else:
                    description = inv.name

                if not period:
                    raise osv.except_osv(_('Insufficient Data!'),
                                         _('No period found on the invoice.'))

                refund_id = inv_obj.refund(cr, uid, [inv.id], date, period, description, journal_id, context=context)

                refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                refund_obj.button_reset_taxes(cr, uid, refund.id, context=context)
                # Add parent invoice

                update_data = {'date_due': date,
                               'check_total': inv.check_total,
                               'parent_id': inv.id}
                if form.ncf:
                    update_data.update({"internal_number": form.ncf})

                if mode == "desc":
                    try:
                        discount_value = "%" in form.discount_value and float(form.discount_value.replace("%", "")) or float(form.discount_value)
                        in_percent = "%" in form.discount_value and True or False
                    except:
                        raise osv.except_osv(_(u'Valor inválido'),
                                         _(u'Debe de colocar un valor válido para el descuento, el único carácter permintido es el de % si desea aplicar un porciento de el valor de la factura'))

                    inv_date = datetime.datetime.strptime(inv.date_invoice, "%Y-%m-%d").date()
                    form_date = datetime.datetime.strptime(form.date, "%Y-%m-%d").date()
                    days = form_date-inv_date
                    days = days.days

                    if in_percent:
                        if discount_value > 100 or discount_value <= 0:
                            raise osv.except_osv(_(u'Valor inválido'),
                                         _(u'El descuento que desea aplicar no es valido!'))
                        else:
                            discount_total = refund.amount_total*discount_value/100
                            if discount_total > inv.residual:
                                raise osv.except_osv(_(u'Valor inválido'),
                                         _(u'No puede aplicar un descuento mayor al saldo de la factura!'))
                            else:
                                discount_value = 100-discount_value

                        for line in refund.invoice_line:
                            line.name = _("Discount")
                            if days < 30:
                                line.discount = discount_value
                            else:
                                line.discount = discount_value
                                line.invoice_line_tax_id = False
                    else:
                        for line in refund.invoice_line:
                            line.unlink();
                        refund.write({"invoice_line": [(0, 0, {"name": _("Discount"), "quantity": 1, "price_unit": discount_value})]})

                refund_obj.write(cr, uid, [refund.id], update_data)
                refund_obj.button_compute(cr, uid, refund_id)

                created_inv.append(refund_id[0])

                if mode in ('cancel', 'modify', 'desc'):
                    movelines = inv.move_id.line_id
                    to_reconcile_ids = {}
                    debit = credit = 0
                    for line in movelines:

                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_ids[line.account_id.id] = [line.id]
                        if type(line.reconcile_id) != browse_null:
                            reconcile_obj.unlink(cr, uid, line.reconcile_id.id)
                    wf_service.trg_validate(uid, 'account.invoice',
                                            refund.id, 'invoice_open', cr)
                    refund = inv_obj.browse(
                        cr, uid, refund_id[0], context=context)
                    for tmpline in refund.move_id.line_id:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_ids[
                                tmpline.account_id.id].append(tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile_partial(
                            cr, uid, to_reconcile_ids[account],
                            writeoff_period_id=period,
                            writeoff_journal_id=inv.journal_id.id,
                            writeoff_acc_id=inv.account_id.id
                        )
                    if mode == 'modify':
                        invoice = inv_obj.read(cr, uid, [inv.id],
                                               ['name', 'type', 'number',
                                                'reference', 'comment',
                                                'date_due', 'partner_id',
                                                'partner_insite',
                                                'partner_contact',
                                                'partner_ref', 'payment_term',
                                                'account_id', 'currency_id',
                                                'invoice_line', 'tax_line',
                                                'journal_id', 'period_id'],
                                               context=context)
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(
                            cr, uid, invoice['invoice_line'], context=context)
                        invoice_lines = inv_obj._refund_cleanup_lines(
                            cr, uid, invoice_lines, context=context)
                        tax_lines = inv_tax_obj.browse(
                            cr, uid, invoice['tax_line'], context=context)
                        tax_lines = inv_obj._refund_cleanup_lines(
                            cr, uid, tax_lines, context=context)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line': tax_lines,
                            'period_id': period,
                            'name': description,
                            'origin': self._get_orig(cr, uid, inv, context={}),
                        })
                        for field in (
                                'partner_id', 'account_id', 'currency_id',
                                'payment_term', 'journal_id'):
                            invoice[field] = invoice[
                                                 field] and invoice[field][0]
                        inv_id = inv_obj.create(cr, uid, invoice, {})
                        if inv.payment_term.id:
                            data = inv_obj.onchange_payment_term_date_invoice(
                                cr, uid, [inv_id], inv.payment_term.id, date)
                            if 'value' in data and data['value']:
                                inv_obj.write(cr, uid, [inv_id], data['value'])
                        created_inv.append(inv_id)
            xml_id = (inv.type == 'out_refund') and 'action_invoice_tree1' or \
                     (inv.type == 'in_refund') and 'action_invoice_tree2' or \
                     (inv.type == 'out_invoice') and 'action_invoice_tree3' or \
                     (inv.type == 'in_invoice') and 'action_invoice_tree4'
            result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
            id = result and result[1] or False
            result = act_obj.read(cr, uid, id, context=context)
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result

    def invoice_refund(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)

        invoice = self.pool.get("account.invoice").browse(cr, uid, context.get("active_ids", False))

        if data.filter_refund in ["refund", "cancel", "modify"] and invoice.reference != "PTV":
            invoice.check_from_stock()

        if invoice.no_more_cn:
            raise osv.except_osv(_('Alerta!'), _(
                'No puede crear mas notas de credito para esta factura'))
        return self.compute_refund(cr, uid, ids, data.filter_refund, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
