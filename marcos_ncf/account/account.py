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


class account_move(models.Model):
    _inherit = "account.move"

    def account_assert_balanced(self):
        return True
        cr.execute("""\
            SELECT      move_id
            FROM        account_move_line
            WHERE       state = 'valid'
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > 0.00001
            """)
        assert len(cr.fetchall()) == 0, \
            "For all Journal Items, the state is valid implies that the sum " \
            "of credits equals the sum of debits"
        return True


class account_fiscal_position(models.Model):
    _inherit = 'account.fiscal.position'

    def _get_fiscal_type(self):
        return (
            ("fiscal", u"Facturas para crédito fiscal"),
            ("final", u"Facturas para Consumidore Final"),
            ("final_note", u"Nota de crédito a consumidor final"),
            ("fiscal_note", u"Nota de crédito para crédito fiscal"),
            ("special", u"Factura Regímenes Especiales"),
            ("gov", u"Factura Gubernamental"),
            ("informal", u"Proveedores Informales"),
            ("minor", u"Gastos Menores"),
            ('01', u'01 - Gastos de personal'),
            ('02', u'02 - Gastos por trabajo, suministros y servicios'),
            ('03', u'03 - Arrendamientos'),
            ('04', u'04 - Gastos de Activos Fijos'),
            ('05', u'05 - Gastos de Representación'),
            ('06', u'06 - Otras Deducciones Admitidas'),
            ('07', u'07 - Gastos Financieros'),
            ('08', u'08 - Gastos Extraordinarios'),
            ('09', u'09 - Compras y Gastos que forman parte del Costo de Venta'),
            ('10', u'10 - Adquisiciones de Activos'),
            ('11', u'11 - Gastos de Seguro')
        )

    fiscal_type = fields.Selection(_get_fiscal_type, "Tipo de NCF")
    for_supplier = fields.Boolean("Para proveedores")


class account_journal(models.Model):
    _order = "name"
    _inherit = 'account.journal'

    ipf_payment_type = fields.Selection([(u'cash', u'Efectivo'),
                                         (u'Check', u'Cheque'),
                                         (u'credit_card', u'Tarjeta de crédito'),
                                         (u'debit_card', u'Tarjeta de debito'),
                                         (u'card', u'Tarjeta'),
                                         (u'coupon', u'Cupón'),
                                         (u'other', u'Otro'),
                                         (u'credit_note', u'Nota de crédito')],
                                        u'Formas de pago impresora fiscal', required=False,
                                        help=u"Esta configuracion se encuantra internamente en la impresora fiscal y debe de especificar esta opecion. " \
                                             u"Esta es la forma en que la impresora fiscal registra el pago en los libros.")
    ncf_special = fields.Selection([("gasto", "Gastos Menores"),
                                    ("informal", "Proveedores Informales"),
                                    ("pruchase", "Diario de compra por caja chica")], "Compras Especiales",
                                   help="Debe marcar esta casilla si el diario esta destinado pa generar comprobantes especiales de compra como Gastos Menores o Proveedores informales.")
    special_partner = fields.Many2one("res.partner", "Empresa para gastos menores")
    special_product = fields.Many2one("product.product", "Producto para gastos menores")
    is_cjc = fields.Boolean("Caja Chica", help="Marcar si usara este diario para control de efectivo de caja chica")
    informal_journal_id = fields.Many2one("account.journal", "Diario de Proveedores informales")
    gastos_journal_id = fields.Many2one("account.journal", "Diario de Gastos Menores")
    purchase_journal_id = fields.Many2one("account.journal", "Diario Compras")
    pay_to = fields.Many2one("res.partner", "Pagar a")
    ncf_required = fields.Boolean("Requiere NCF del proveedor", default=False)
    active = fields.Boolean("Activo", default=True)
    nc_payment = fields.Boolean("Control de notas de credito", default=False)
    cash_bank_type = fields.Boolean()


class account_tax(models.Model):
    _inherit = 'account.tax'

    exempt = fields.Boolean("Exempt")
    itbis = fields.Boolean("ITBIS")
    retention = fields.Boolean(u"Retención ITBIS")
    retention_isr = fields.Boolean(u"Retención ISR")

    # Validate if each tax is marked as 'exempt' and zero the 'amount'
    @api.v7
    def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False):
        result = super(account_tax, self).compute_all(cr, uid, taxes, price_unit, quantity, product=product,
                                                      partner=partner, force_excluded=force_excluded)
        for tax in result['taxes']:
            tax_obj = self.pool.get('account.tax').browse(cr, uid, tax['id'])
            if tax_obj.exempt:
                tax['amount'] = 0.0
        return result

    @api.v8
    def compute_all(self, price_unit, quantity, product=None, partner=None, force_excluded=False):
        return self._model.compute_all(
            self._cr, self._uid, self, price_unit, quantity,
            product=product, partner=partner, force_excluded=force_excluded)
