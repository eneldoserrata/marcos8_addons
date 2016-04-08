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
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp

from decimal import *


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):

        product_uom = self.pool.get('product.uom')
        if not order.importation:
            price_unit = order_line.price_unit
        else:
            price_unit = order_line.price_unit_pesos * order.custom_rate

        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor

        if order.currency_id.id != order.company_id.currency_id.id and not order.importation:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        res = []
        move_template = {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': order.date_order,
            'date_expected': fields.date.date_to_datetime(self, cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': False,
            'state': 'draft',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': order.picking_type_id.id,
            'group_id': group_id,
            'procurement_id': False,
            'origin': order.name,
            'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id':order.picking_type_id.warehouse_id.id,
            'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
        }

        diff_quantity = order_line.product_qty
        for procurement in order_line.procurement_ids:
            procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
            tmp = move_template.copy()
            tmp.update({
                'product_uom_qty': min(procurement_qty, diff_quantity),
                'product_uos_qty': min(procurement_qty, diff_quantity),
                'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                'procurement_id': procurement.id,
                'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='picking' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                'propagate': procurement.rule_id.propagate,
            })
            diff_quantity -= min(procurement_qty, diff_quantity)
            res.append(tmp)
        #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
        #split the future stock move in two because the route followed may be different.
        if diff_quantity > 0:
            move_template['product_uom_qty'] = diff_quantity
            move_template['product_uos_qty'] = diff_quantity
            res.append(move_template)
        return res

    _columns = {
        "custom_rate": fields.float("Taza de la planilla de aduanas",
                                    help=u"El valor de la tasa de cambio en la planilla de liquidación de aduanas"),
        "dop_total_cost": fields.float(u"Total de costos en pesos (DOP)",
                                       help="La suma de todas las facturas y gastos en pesos antes de impuestos"),
        "usd_total_cost": fields.float(u"Total de costos en dólares (USD)",
                                       help=u"La suma de todas las facturas y gastos en dólares"),
        "importation": fields.boolean(u"Es una Importación")
    }



    def action_invoice_create(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids, context=context)
        if order.importation:
            pass
        else:
            return super(purchase_order, self).action_invoice_create(cr, uid, ids, context=context)


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    def compute_list(self, total_paid, quantities, prices, ids):
        new_prices     = [Decimal(str(p))   for p      in prices]
        new_quantities = [Decimal(str(qty)) for qty    in quantities]
        totals_ary     = [p*qty             for p, qty in zip(new_quantities, new_prices)]
        total          = sum(totals_ary)

        total_paid     = Decimal(str(total_paid))

        # totals + importation expenses
        total_importation = [ n + total_paid*(n/total) for n in totals_ary]

        # prices + importantion expenses
        expenses = [imp/qty for qty, imp in zip(new_quantities, total_importation)]

        ret = [round(float(expend), 2) for expend in expenses]

        return [{'id': t[0], 'price': t[1]} for t in zip(ids, ret)]

    def extract_lists(self, products):
        ids        = []
        prices     = []
        quantities = []

        for product_info in products:
            ids.append(product_info['id'])
            prices.append(product_info['price'])
            quantities.append(product_info['qty'])

        return {'ids': ids, 'prices': prices, 'quantities': quantities}

    def _amount_line_liquidation(self, cr, uid, ids, prop, arg, context=None):
        order = self.browse(cr, uid, ids, context=context)[0]
        response = {}
        if order.order_id.importation:

            res_list = []
            rate = order.order_id.custom_rate
            lines = self.browse(cr, uid, ids, context=context)
            for line in lines:
                if line.price_subtotal <= 0:
                    raise osv.except_osv('Alerta!', "No puede agragar productos con valor cero")
                elif rate < 0:
                    raise osv.except_osv('Alerta!', "Debe de expecificar la taza de la planilla de importacion")
                elif order.order_id.dop_total_cost <= 0:
                    raise osv.except_osv('Alerta!', "Debe de expecificar el total de los gastos en pesos para esta importacion")
                elif order.order_id.usd_total_cost <= 0:
                    raise osv.except_osv('Alerta!', "Debe de expecificar el total de los gastos en dolares para esta importacion")

                res = {}
                res["id"] = line.id
                res["qty"] = line.product_qty
                res["price"] = line.price_subtotal / line.product_qty
                res_list.append(res)

            lista = self.extract_lists(res_list)
            total_importacion = (order.order_id.dop_total_cost/rate) + order.order_id.usd_total_cost
            rets = self.compute_list(total_importacion, lista['quantities'], lista['prices'], lista['ids'])
            for ret in rets:
                response[ret["id"]] = ret["price"]
            return response
        return {}


    _columns = {
        'price_unit_pesos': fields.function(_amount_line_liquidation, string='Cost unit (USD)',
                                            digits_compute=dp.get_precision('Account'))
    }


class product_product(osv.osv):
    _inherit = "product.product"

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = context.get('display_default_code', False) and d.get('default_code', False) or False
            if code:
                name = '[%s] %s' % (code, name)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id,
                                                                       context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)

        result = []
        products = self.browse(cr, SUPERUSER_ID, ids, context=context)
        for product in products:
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and "%s (%s)" % (s.product_name, variant) or False
                    mydict = {
                        'id': product.id,
                        'name': seller_variant or name,
                        'default_code': s.product_code or product.default_code,
                    }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                    'id': product.id,
                    'name': name,
                    'default_code': product.default_code,
                }
                result.append(_name_get(mydict))
        return result