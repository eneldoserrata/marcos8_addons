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

from openerp import models, fields, exceptions, api
from openerp.tools.translate import _
from openerp.osv import osv, fields as old_fields
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class stock_inventory(osv.Model):
    _inherit = "stock.inventory"

    def _get_available_filters(self, cr, uid, context=None):
        res = super(stock_inventory, self)._get_available_filters(cr, uid, context=context)

        mode_to_add = [("invenory_plus", "Importar desde los codigos y sumar al inventario actual"),
                       ("inventory_update", "Importar desde los codigos y actualizar el inventario actual")
                       ]
        res += mode_to_add

        return res

    _columns = {
        'filter': old_fields.selection(_get_available_filters, 'Inventory of', required=True,
                                   help="If you do an entire inventory, you can choose 'All Products' and it will prefill the inventory with the current stock.  If you only do some products  "\
                                      "(e.g. Cycle Counting) you can choose 'Manual Selection of Products' and the system won't propose anything.  You can also let the "\
                                      "system propose for a single product / lot /... "),
    }

    def prepare_inventory(self, cr, uid, ids, context=None):
        invetory = self.browse(cr, uid, ids, context=context)
        if invetory.filter in ["invenory_plus", "inventory_update"]:
            return self.write(cr, uid, ids, {'state': 'confirm', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        else:
            return super(stock_inventory, self).prepare_inventory(cr, uid, ids, context=context)


class stock_quant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def get_product_qty_by_location(self, product_id):
        self._cr.execute("""SELECT   "stock_location"."location_id",
                             "stock_location"."name",
                             "product_product"."id",
                             "product_product"."name_template",
                             SUM( "stock_quant"."qty" )
                            FROM     "stock_quant"
                                      INNER JOIN "product_product"  ON "stock_quant"."product_id" = "product_product"."id"
                                      INNER JOIN "stock_location"  ON "stock_quant"."location_id" = "stock_location"."id"
                            WHERE "product_product"."id" = %(id)s AND"stock_location"."usage" = 'internal'
                            GROUP BY
                             "stock_location"."location_id",
                             "stock_location"."name",
                             "product_product"."id",
                             "product_product"."name_template"
                           """, {"id": product_id})
        result = self._cr.fetchall()
        if result:
            return result
        else:
            return []

    @api.model
    def get_product_qty_in_location(self, product_id, location_id):

        self._cr.execute("""SELECT   "stock_location"."location_id",
                             "stock_location"."name",
                             "product_product"."id",
                             "product_product"."name_template",
                             SUM( "stock_quant"."qty" )
                            FROM     "stock_quant"
                                      INNER JOIN "product_product"  ON "stock_quant"."product_id" = "product_product"."id"
                                      INNER JOIN "stock_location"  ON "stock_quant"."location_id" = "stock_location"."id"
                            WHERE "product_product"."id" = %(product_id)s
                            AND "stock_location"."id" = %(location_id)s
                            AND "stock_location"."usage" = 'internal'
                            GROUP BY
                             "stock_location"."location_id",
                             "stock_location"."name",
                             "product_product"."id",
                             "product_product"."name_template"
                           """, {"product_id": product_id, "location_id": location_id})
        result = self._cr.fetchall()
        if result:
            return result

        return []


class stock_picking(models.Model):
    _inherit = "stock.picking"

    afecta = fields.Many2one("account.invoice")
    src_usage = fields.Selection(string="Desde", related="picking_type_id.default_location_src_id.usage", readonly=True)
    dest_usage = fields.Selection(string="Hasta", related="picking_type_id.default_location_dest_id.usage", readonly=True)
    refund_type = fields.Selection(string="Tipo de factura", related="afecta.type", readonly=True)

    @api.model
    def do_transfer(self):
        res = super(stock_picking, self).do_transfer()
        for picking in self:
            if picking.group_id:
                group_name = picking.group_id.name

                so_id = self.pool.get("sale.order").search(self._cr, self._uid, [("name", "=", picking.group_id.name)])
                po_id = self.pool.get("purchase.order").search(self._cr, self._uid,
                                                               [("name", "=", picking.group_id.name)])

                if so_id:
                    origin = self.pool.get("sale.order").browse(self._cr, self._uid, so_id, context=self._context)
                elif po_id:
                    origin = self.pool.get("purchase.order").browse(self._cr, self._uid, po_id, context=self._context)

                if origin.invoice_ids and not picking.invoice_id:
                    if not picking.afecta:
                        picking.invoice_id = origin.invoice_ids[0].id
        return res


class stock_location(models.Model):
    _inherit = "stock.location"

    property_stock_valuation_account_id = fields.Many2one('account.account', company_dependent=True,
                                                          string="Stock Valuation Account",
                                                          help="When real-time inventory valuation is enabled on a product, this account will hold the current value of the products.", )


class product_template(osv.osv):
    _inherit = 'product.template'

    def get_product_accounts(self, cr, uid, product_id, context=None):

        if context is None:
            context = {}
        product_obj = self.browse(cr, uid, product_id, context=context)

        stock_input_acc = product_obj.property_stock_account_input and product_obj.property_stock_account_input.id or False
        if not stock_input_acc:
            stock_input_acc = product_obj.categ_id.property_stock_account_input_categ and product_obj.categ_id.property_stock_account_input_categ.id or False

        stock_output_acc = product_obj.property_stock_account_output and product_obj.property_stock_account_output.id or False
        if not stock_output_acc:
            stock_output_acc = product_obj.categ_id.property_stock_account_output_categ and product_obj.categ_id.property_stock_account_output_categ.id or False

        journal_id = product_obj.categ_id.property_stock_journal and product_obj.categ_id.property_stock_journal.id or False

        # marcos check if account is declare in location
        account_valuation = False
        if context.get("active_model", False) == "stock.picking":
            picking_id = self.pool.get("stock.picking").browse(cr, uid, context["active_id"])
            account_valuation = picking_id.location_id.property_stock_valuation_account_id.id or picking_id.location_dest_id.property_stock_valuation_account_id.id

        if not account_valuation:
            account_valuation = product_obj.categ_id.property_stock_valuation_account_id and product_obj.categ_id.property_stock_valuation_account_id.id or False

        if not all([stock_input_acc, stock_output_acc, account_valuation, journal_id]):
            raise osv.except_osv(_('Error!'), _('''One of the following information is missing on the product or product category and prevents the accounting valuation entries to be created:
    Product: %s
    Stock Input Account: %s
    Stock Output Account: %s
    Stock Valuation Account: %s
    Stock Journal: %s
    ''') % (product_obj.name, stock_input_acc, stock_output_acc, account_valuation, journal_id))
        return {
            'stock_account_input': stock_input_acc,
            'stock_account_output': stock_output_acc,
            'stock_journal': journal_id,
            'property_stock_valuation_account_id': account_valuation
        }



