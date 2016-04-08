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

from openerp.osv import orm, fields, osv
from openerp.tools.translate import _
from openerp import api



class account_fiscal_position_template(osv.osv):
    _inherit = 'account.fiscal.position.template'

    _columns = {
        'name': fields.char('Fiscal Position Template', required=True),
        'chart_template_id': fields.many2one('account.chart.template', 'Chart Template', required=True),
        'account_ids': fields.one2many('account.fiscal.position.account.template', 'position_id', 'Account Mapping'),
        'tax_ids': fields.one2many('account.fiscal.position.tax.template', 'position_id', 'Tax Mapping'),
        'note': fields.text('Notes'),
        "fiscal_type": fields.char("Tipo de NCF"),
        "for_supplier": fields.boolean("Para proveedores")
    }

    def generate_fiscal_position(self, cr, uid, chart_temp_id, tax_template_ref, acc_template_ref, company_id, context=None):
        """
        This method generate Fiscal Position, Fiscal Position Accounts and Fiscal Position Taxes from templates.

        :param chart_temp_id: Chart Template Id.
        :param taxes_ids: Taxes templates reference for generating account.fiscal.position.tax.
        :param acc_template_ref: Account templates reference for generating account.fiscal.position.account.
        :param company_id: company_id selected from wizard.multi.charts.accounts.
        :returns: True
        """
        if context is None:
            context = {}
        obj_tax_fp = self.pool.get('account.fiscal.position.tax')
        obj_ac_fp = self.pool.get('account.fiscal.position.account')
        obj_fiscal_position = self.pool.get('account.fiscal.position')
        fp_ids = self.search(cr, uid, [('chart_template_id', '=', chart_temp_id)])
        for position in self.browse(cr, uid, fp_ids, context=context):
            new_fp = obj_fiscal_position.create(cr, uid,
                                                {'company_id': company_id,
                                                 'name': position.name,
                                                 'note': position.note,
                                                 'fiscal_type': position.fiscal_type,
                                                 'for_supplier': position.for_supplier
                                                 })
            for tax in position.tax_ids:
                obj_tax_fp.create(cr, uid, {
                    'tax_src_id': tax_template_ref[tax.tax_src_id.id],
                    'tax_dest_id': tax.tax_dest_id and tax_template_ref[tax.tax_dest_id.id] or False,
                    'position_id': new_fp
                })
            for acc in position.account_ids:
                obj_ac_fp.create(cr, uid, {
                    'account_src_id': acc_template_ref[acc.account_src_id.id],
                    'account_dest_id': acc_template_ref[acc.account_dest_id.id],
                    'position_id': new_fp
                })
        return True


class account_tax_template(osv.osv):

    _inherit = 'account.tax.template'
    _description = 'Templates for Taxes'

    _columns = {
        "exempt": fields.boolean("Exempt"),
        "itbis": fields.boolean("ITBIS"),
        "retention": fields.boolean(u"Retención")
    }

    def _generate_tax(self, cr, uid, tax_templates, tax_code_template_ref, company_id, context=None):
        """
        This method generate taxes from templates.

        :param tax_templates: list of browse record of the tax templates to process
        :param tax_code_template_ref: Taxcode templates reference.
        :param company_id: id of the company the wizard is running for
        :returns:
            {
            'tax_template_to_tax': mapping between tax template and the newly generated taxes corresponding,
            'account_dict': dictionary containing a to-do list with all the accounts to assign on new taxes
            }
        """
        if context is None:
            context = {}
        res = {}
        todo_dict = {}
        tax_template_to_tax = {}
        for tax in tax_templates:
            vals_tax = {
                'name':tax.name,
                'sequence': tax.sequence,
                'amount': tax.amount,
                'type': tax.type,
                'applicable_type': tax.applicable_type,
                'domain': tax.domain,
                'parent_id': tax.parent_id and ((tax.parent_id.id in tax_template_to_tax) and tax_template_to_tax[tax.parent_id.id]) or False,
                'child_depend': tax.child_depend,
                'python_compute': tax.python_compute,
                'python_compute_inv': tax.python_compute_inv,
                'python_applicable': tax.python_applicable,
                'base_code_id': tax.base_code_id and ((tax.base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.base_code_id.id]) or False,
                'tax_code_id': tax.tax_code_id and ((tax.tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.tax_code_id.id]) or False,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_code_id': tax.ref_base_code_id and ((tax.ref_base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_base_code_id.id]) or False,
                'ref_tax_code_id': tax.ref_tax_code_id and ((tax.ref_tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_tax_code_id.id]) or False,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'include_base_amount': tax.include_base_amount,
                'description': tax.description,
                'company_id': company_id,
                'type_tax_use': tax.type_tax_use,
                'price_include': tax.price_include,
                "exempt": tax.exempt,
                "itbis": tax.itbis,
                "retention": tax.retention
            }
            new_tax = self.pool.get('account.tax').create(cr, uid, vals_tax)
            tax_template_to_tax[tax.id] = new_tax
            #as the accounts have not been created yet, we have to wait before filling these fields
            todo_dict[new_tax] = {
                'account_collected_id': tax.account_collected_id and tax.account_collected_id.id or False,
                'account_paid_id': tax.account_paid_id and tax.account_paid_id.id or False,
            }
        res.update({'tax_template_to_tax': tax_template_to_tax, 'account_dict': todo_dict})
        return res


class account_fiscal_position(orm.Model):
    _inherit = 'account.fiscal.position'

    def _get_fiscal_type(self, cursor, user_id, context=None):
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

    _columns = {
        "fiscal_type": fields.selection(_get_fiscal_type, "Tipo de NCF"),
        "for_supplier": fields.boolean("Para proveedores")
    }

class account_journal(osv.osv):
    _order = "name"
    _inherit = 'account.journal'
    _columns = {
        'ipf_payment_type': fields.selection([(u'cash', u'Efectivo'),
                                              (u'Check', u'Cheque'),
                                              (u'credit_card', u'Tarjeta de crédito'),
                                              (u'debit_card', u'Tarjeta de debito'),
                                              (u'card', u'Tarjeta'),
                                              (u'coupon', u'Cupón'),
                                              (u'other', u'Otro'),
                                              (u'credit_note', u'Nota de crédito')],
                                             u'Formas de pago impresora fiscal', required=False,
                                             help=u"Esta configuracion se encuantra internamente en la impresora fiscal y debe de especificar esta opecion. " \
                                                  u"Esta es la forma en que la impresora fiscal registra el pago en los libros."),
        "ncf_special": fields.selection([("gasto", "Gastos Menores"),
                                         ("informal", "Proveedores Informales"),
                                         ("pruchase", "Diario de compra por caja chica")], "Compras Especiales", help="Debe marcar esta casilla si el diario esta destinado pa generar comprobantes especiales de compra como Gastos Menores o Proveedores informales."),
        "special_partner": fields.many2one("res.partner", "Empresa para gastos menores"),
        "special_product": fields.many2one("product.product", "Producto para gastos menores"),
        "is_cjc": fields.boolean("Caja Chica", help="Marcar si usara este diario para control de efectivo de caja chica"),
        "informal_journal_id": fields.many2one("account.journal", "Diario de Proveedores informales"),
        "gastos_journal_id": fields.many2one("account.journal", "Diario de Gastos Menores"),
        "purchase_journal_id": fields.many2one("account.journal", "Diario Compras"),
        "pay_to": fields.many2one("res.partner", "Pagar a"),
        "ncf_required": fields.boolean("Requiere NCF del proveedor", default=False),
        "active": fields.boolean("Activo", default=True),
        "nc_payment": fields.boolean("Control de notas de credito", default=False)

    }


class account_tax(osv.osv):
    _inherit = 'account.tax'

    _columns = {
        "exempt": fields.boolean("Exempt"),
        "itbis": fields.boolean("ITBIS"),
        "retention": fields.boolean(u"Retención")
    }

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



