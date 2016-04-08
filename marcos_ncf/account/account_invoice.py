# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
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
from ..tools import is_ncf, is_identification, _internet_on
from openerp.exceptions import ValidationError
import requests
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from psycopg2 import IntegrityError

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class account_invoice(models.Model):
    _inherit = "account.invoice"

    # def _auto_init(self, cr, context=None):
    #     self._sql_constraints = [
    #         ('number_uniq', 'unique(number, company_id, journal_id, type, partner_id)',
    #          'Invoice Number must be unique per Company!'),
    #     ]
    #     super(account_invoice, self)._auto_init(cr, context)

    def _check_ncf(self, rnc, ncf):
        if ncf and rnc:
            res = requests.get('http://api.marcos.do/ncf/{}/{}'.format(rnc, ncf))
            if res.status_code == 200:
                return res.json()
        return {}

    def _invoice_ncf_validate(self):

        if self.type in ['in_invoice', "in_refund"] and not self.reference_type in ['none', 'ext'] \
                and not self.journal_id.ncf_special in ['gasto', 'informal'] and self.ncf_required == True:

            # if not self.internal_number and self.ncf_required:
            #     raise ValidationError("Debe colocar el NCF de la factura proveedor")

            if self.internal_number:
                if self.internal_number[9:11] == '02':
                    raise ValidationError("El numero de comprobante fiscal no es valido "
                                          "verifique de que no esta digitando un comprobante "
                                          "de consumidor final codigo 02")
                elif self.type == "in_refund" and not self.internal_number[9:11] == '04':
                    raise ValidationError(u"Codigo de NCF para notas de crédito invalido debe de ser codigo 04")

                if _internet_on():
                    result = self._check_ncf(self.partner_id.ref, self.internal_number)
                    if not result.get("valid", False):
                        raise ValidationError("El numero de comprobante fiscal no es valido "
                                              "no paso la validacion en DGII")

                elif not is_ncf(self.internal_number, self.env.context.get("type", False)) and self.ncf_required:
                    raise ValidationError("El numero de comprobante fiscal no es valido"
                                          "verifique de que no esta digitando un comprobante"
                                          "de consumidor final codigo 02 o revise si lo ha"
                                          "digitado incorrectamente")

    @api.model
    def _get_reference_type(self):
        return [
            ('none', u'Pendiente de digitar'),
            ('ext', u'Servicios en el exterior'),
            ('01', '01 - Gastos de personal'),
            ('02', '02 - Gastos por trabajo, suministros y servicios'),
            ('03', '03 - Arrendamientos'),
            ('04', '04 - Gastos de Activos Fijos'),
            ('05', u'05 - Gastos de Representación'),
            ('06', '06 - Otras Deducciones Admitidas'),
            ('07', '07 - Gastos Financieros'),
            ('08', '08 - Gastos Extraordinarios'),
            ('09', '09 - Compras y Gastos que forman parte del Costo de Venta'),
            ('10', '10 - Adquisiciones de Activos'),
            ('11', '11 - Gastos de Seguro')
        ]


    """
    If the shop is defined on the user will be the default shop ncf configuration an read only
    else if the shop not defined on the user the user can select the shop
    """

    @api.multi
    def _get_deafult_user_shop_config(self):
        return self.env["shop.ncf.config"].get_default()



    """
    When fiscal position change have to search the coresponding journal type
    and from werehouse jornal invoice configuration

    TODO: create correct demo data because when isntall with demo data get exception because
    the new field shop_ncf_config_id not include an get exception this is the reason i place
    try inthis exception
    """

    # TODO cotrol ncf_required on credit note
    @api.onchange('fiscal_position')
    def onchange_fiscal_position(self):
        if self.fiscal_position:
            if not self.shop_ncf_config_id and self.env.context.get("default_type", False) == "out_invoice":
                self.fiscal_position = False
                return {'warning': {
                    'title': "Seleccione la sucursal",
                    'message': "Para poder realizar una factura debe selecionar la sucursal que realizara la factura"}}
            else:
                if self.env.context.get('type', False) == "out_invoice":
                    if self.fiscal_position.fiscal_type == "final":
                        self.journal_id = self.shop_ncf_config_id.final
                    elif self.fiscal_position.fiscal_type == "fiscal":
                        self.journal_id = self.shop_ncf_config_id.fiscal
                    elif self.fiscal_position.fiscal_type == "special":
                        self.journal_id = self.shop_ncf_config_id.special
                    elif self.fiscal_position.fiscal_type == "gov":
                        self.journal_id = self.shop_ncf_config_id.gov

                elif self.env.context.get('type', False) in ["in_invoice", "in_refund"]:
                    if self.fiscal_position.fiscal_type in [u'informal', u'minor']:
                        self.ncf_required = False
                    elif self.journal_id.type in ["purchase", "purchase_refund"]:
                        self.ncf_required = True
                    if self.fiscal_position.fiscal_type in [d[0] for d in self._get_reference_type()]:
                        self.reference_type = self.fiscal_position.fiscal_type
                    else:
                        self.reference_type = 'none'
        if self.partner_id.property_account_position.id != self.fiscal_position.id:
            self.partner_id.write({"property_account_position": self.fiscal_position.id})

    @api.onchange("reference_type")
    def onchange_reference_type(self):
        if self.reference_type in ['none', 'ext']:
            self.ncf_required = False
        else:
            self.ncf_required = True

    @api.constrains("reference_type")
    def constrains_reference_type(self):
        self._invoice_ncf_validate()

    def _get_partner_journal(self, fiscal_type, shop):
        if fiscal_type == "final" or fiscal_type == False:
            return shop.final.id
        elif fiscal_type == "fiscal":
            return shop.fiscal.id
        elif fiscal_type == "special":
            return shop.special.id
        elif fiscal_type == "gov":
            return shop.gov.id
        elif fiscal_type == "out_refund":
            return shop.nc.id

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False, company_id=False):
        if partner_id:
            res = super(account_invoice, self).onchange_partner_id(type=type, partner_id=partner_id,
                                                                   date_invoice=date_invoice, payment_term=payment_term,
                                                                   partner_bank_id=partner_bank_id,
                                                                   company_id=company_id)

            partner_obj = self.env["res.partner"].browse(partner_id)
            property_account_position = partner_obj.property_account_position
            if not property_account_position:
                partner_obj.write({"property_account_position": 2})
                res["value"].update({"fiscal_position": 2})

            shop_id = self._get_deafult_user_shop_config()
            shop_obj = self.env["shop.ncf.config"].browse(shop_id)
            if partner_obj.customer:
                journal_id = self._get_partner_journal(property_account_position.fiscal_type, shop_obj)
                res["value"].update({"journal_id": journal_id})

            return res
        else:
            return False

    reference_type = fields.Selection('_get_reference_type', string='Tipo de comprobante',
                                      required=True, readonly=True, states={'draft': [('readonly', False)]},
                                      default='none')
    internal_number = fields.Char(string='Invoice Number', readonly=False, copy=False, size=19,
                                  help="Unique number of the invoice, computed automatically when the invoice is created.")
    ncf_required = fields.Boolean("Requiere NCF", related="journal_id.ncf_required")
    nif = fields.Char("NIF", default="false", readonly=True, copy=False)
    pay_to = fields.Many2one("res.partner", "Pagar a")
    shop_ncf_config_id = fields.Many2one("shop.ncf.config", "Sucursal", default=_get_deafult_user_shop_config,
                                         required=False, readonly=True)

    _sql_constraints = [
        ('number_uniq', 'unique(number, company_id, journal_id, type, partner_id)',
             'Invoice Number must be unique per Company!')
    ]

    @api.onchange("shop_ncf_config_id")
    def onchange_shop_ncf_config_id(self):

        if self.type == "out_refund":
            self.journal_id = self.shop_ncf_config_id.nc.id
        elif self.type == "out_invoice":
            if self.fiscal_position.fiscal_type == "final" or False:
                self.journal_id = self.shop_ncf_config_id.final.id
            elif self.fiscal_position.fiscal_type == "fiscal":
                self.journal_id = self.shop_ncf_config_id.fiscal.id
            elif self.fiscal_position.fiscal_type == "gov":
                self.journal_id = self.shop_ncf_config_id.gov.id
            elif self.fiscal_position.fiscal_type == "special":
                self.journal_id = self.shop_ncf_config_id.spacial.id

    def get_partner_journal(self, type, fiscal_type):
        if type == "out_refund":
            return self.shop_ncf_config_id.nc.id
        elif type == "out_invoice":
            if fiscal_type == "final" or False:
                return self.shop_ncf_config_id.final.id
            elif fiscal_type == "fiscal":
                return self.shop_ncf_config_id.fiscal.id
            elif fiscal_type == "gov":
                return self.shop_ncf_config_id.gov.id
            elif fiscal_type == "special":
                return self.shop_ncf_config_id.spacial.id

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            if self.journal_id.type in ["purchase", "purchase_refund"]:
                self.ncf_required = self.journal_id.ncf_required
                self.currency_id = self.journal_id.currency.id or self.journal_id.company_id.currency_id.id,
                self.company_id = self.journal_id.company_id.id,
                if self.journal_id.ncf_special == "gasto":
                    self.partner_id = self.journal_id.special_partner.id


    @api.one
    @api.constrains('type')
    def type_check(self):
        # TODO fix this validation
        if self.type == "in_invoice" and self.fiscal_position.vat_required:
            if not is_identification(self.partner_id.ref):
                raise ValidationError(
                    u"No puede crear una factura de compra a proveedor sin un rnc o cedula valido!")
        if self.type == "out_invoice" and self.fiscal_position.vat_required:
            if not is_identification(self.partner_id.ref):
                raise ValidationError(
                    u"No puede crear una factura de venta a un cliente sin un rnc o cedula valido que no sea consumidor final!")
        return True

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):

        if self.pay_to:
            supplier_account_id = self.partner_id.property_account_payable.id
            for line in [lines[2] for lines in move_lines]:
                if line.get("account_id", False) == supplier_account_id:
                    line.update({'partner_id': self.pay_to.id,
                                 'account_id': self.pay_to.property_account_payable.id})
        return move_lines

    @api.multi
    def unlink(self):
        for invoice in self:
            if invoice.state not in ('draft', 'cancel') and not self.env.uid == 1:
                raise Warning(
                    _('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            elif invoice.internal_number and not self.env.uid == 1:
                raise Warning(_(
                    'You cannot delete an invoice after it has been validated (and received a number).  You can set it back to "Draft" state and modify its content, then re-confirm it.'))
        return super(account_invoice, self).unlink()


    @api.multi
    def onchange_payment_term_date_invoice(self, payment_term_id, date_invoice):
        vals = {"value": {}}
        if date_invoice:
            period_id = \
                self.pool.get("account.period").find(self.env.cr, self.env.uid, dt=date_invoice,
                                                     context=self.env.context)[
                    0]
            vals["value"].update({"period_id": period_id})
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if not payment_term_id:
            # To make sure the invoice due date should contain due date which is
            # entered by user when there is no payment term defined
            vals["value"].update({'date_due': self.date_due or date_invoice})
            return vals

        pterm = self.env['account.payment.term'].browse(payment_term_id)
        pterm_list = pterm.compute(value=1, date_ref=date_invoice)[0]
        if pterm_list:
            vals["value"].update({'date_due': max(line[0] for line in pterm_list)})
            return vals
        else:
            raise except_orm(_('Insufficient Data!'),
                             _('The payment term of supplier does not have a payment term line.'))

    @api.model
    def create(self, vals):

        if self.env.context.get("type", False) == 'out_invoice':
            if not vals.get("shop_ncf_config_id", False):
                vals.update({"shop_ncf_config_id": self.env["shop.ncf.config"].get_default()})
            if not vals.get("fiscal_position", False):
                vals.update(
                    {
                        "fiscal_position": self.env['res.partner'].browse(
                            vals["partner_id"]).property_account_position.id})

        invoice = super(account_invoice, self).create(vals)

        if invoice.type == 'out_invoice':
            invoice.journal_id = self._get_partner_journal(invoice.partner_id.property_account_position.fiscal_type,
                                                           invoice.shop_ncf_config_id)
        elif invoice.type == 'out_refund':
            invoice.journal_id = self._get_partner_journal("out_refund", invoice.shop_ncf_config_id)

        return invoice


    @api.multi
    def action_move_create(self):
        if not self.number and self.internal_number:

            number = self.internal_number
            partner_id = self.partner_id.id

            self.env.cr.execute("select id from account_invoice where number = %(number)s and partner_id = %(partner_id)s",{"number": number, "partner_id": partner_id})
            exist = self.env.cr.fetchone()
            if exist:
                raise except_orm("Advertencia!", u'Este nümero de comprobante fiscal ya fue registrado para esta empresa')
        return super(account_invoice, self).action_move_create()


    @api.multi
    def invoice_validate(self):

        self._invoice_ncf_validate()
        if self.parent_id:
            self.reference_type = self.parent_id.reference_type
        elif self.type in ["in_invoice", "in_refund"] and self.reference_type == "none":
            raise except_orm("Advertencia!",
                             u'No puede validar una factura de compra con el tipo pendiente de digitar!')
        res = super(account_invoice, self).invoice_validate()
        return res

    @api.model
    def check_open_credit(self, partner_id):
        amount = 0.00
        sql = """
        SELECT
         "account_invoice"."date_invoice",
         "account_invoice"."number",
         "account_invoice"."residual",
         "account_invoice"."type"
        FROM "account_invoice"
        WHERE ( "residual" > 0.00 ) AND ( "account_invoice"."type" = 'out_refund' ) AND ("account_invoice"."partner_id" = %(partner_id)s)
        """
        self.env.cr.execute(sql, dict(partner_id=partner_id.id))
        res = self.env.cr.fetchall()
        if res:
            amount += sum([rec[2] for rec in res])

        return amount

    def invoice_pay_supplier(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'marcos_ncf', 'view_vendor_payment_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }

    @api.multi
    def invoice_pay_customer(self):

        if not self.ids: return []
        if self.check_open_credit(self.partner_id) > 0:
            view_id = self.pool.get('ir.model.data').get_object_reference(self.env.cr, self.env.uid,'marcos_ncf','invoice_credit_apply_form')[1]
            return {
                'name': _("Pay Invoice"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'invoice.credit.apply',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': {
                    'payment_expected_currency': self.currency_id.id,
                    'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(self.partner_id).id,
                    'default_amount': self.type in ('out_refund', 'in_refund') and -self.residual or self.residual,
                    'default_reference': self.name,
                    'close_after_process': True,
                    'invoice_type': self.type,
                    'invoice_id': self.id,
                    'default_type': self.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                    'type': self.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment'
                }
            }
        else:
            return super(account_invoice, self).invoice_pay_customer()


# class account_invoice_line(models.Model):
#     _inherit = "account.invoice.line"
#     #
#     @api.multi
#     def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
#                           partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
#                           company_id=None):
#         res = super(account_invoice_line, self).product_id_change(product, uom_id, qty=qty, name=name,
#                                                                   type='out_invoice',
#                                                                   partner_id=partner_id, fposition_id=fposition_id,
#                                                                   price_unit=price_unit, currency_id=currency_id,
#                                                                   company_id=company_id)
#
#         if product:
#             name = self.pool.get("product.product").name_get(self.env.cr, self.env.uid, [product],
#                                                              context=self.env.context)[0][1]
#             res["value"]["name"] = name
#         import pdb;pdb.set_trace()
#         return res