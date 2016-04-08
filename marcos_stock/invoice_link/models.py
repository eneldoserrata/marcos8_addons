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

from openerp import models, fields, api, exceptions


class stock_move(models.Model):
    _inherit = "stock.move"

    invoice_line_id = fields.Many2one('account.invoice.line', 'Invoice Line', readonly=True)

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):

        res = super(stock_move, self)._create_invoice_line_from_vals(move, invoice_line_vals)
        move.write({'invoice_line_id': res})
        return res

    def product_price_update_after_done(self, cr, uid, ids, context=None):
        '''
        This method adapts the price on the product when necessary
        '''
        for move in self.browse(cr, uid, ids, context=context):
            #adapt standard price on outgoing moves if the product cost_method is 'real', so that a return
            #or an inventory loss is made using the last value used for an outgoing valuation.
            if move.product_id.cost_method == 'real' and move.location_dest_id.usage != 'internal':
                #store the average price of the move on the move and product form
                self._store_average_cost_price(cr, uid, move, context=context)
            elif move.product_id.cost_method == 'real':
                group_name = move.picking_id.group_id.name
                purchase_order_id = self.pool.get("purchase.order").search(cr, uid, [('name','=',group_name)])
                purchase_order = self.pool.get("purchase.order").browse(cr, uid, purchase_order_id)
                if purchase_order:
                    self._store_average_cost_price(cr, uid, move, context=context)




class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _get_invoice_view_xmlid(self):
        res = {}
        for pick in self:
            if pick.invoice_id:
                if pick.invoice_id.type in ('in_invoice', 'in_refund'):
                    res[pick.id] = 'account.invoice_supplier_form'
                else:
                    res[pick.id] = 'account.invoice_form'
            else:
                res[pick.id] = False
        return res

    invoice_id = fields.Many2one('account.invoice', 'Invoice', readonly=True)
    invoice_view_xmlid = fields.Char(compute='_get_invoice_view_xmlid', type='char',
                                             string="Invoice View XMLID", readonly=True)

    @api.multi
    def _create_invoice_from_picking(self, vals):
        res = super(stock_picking, self)._create_invoice_from_picking(self.id, vals)
        self.id.write({'invoice_id': res})
        return res


class account_invoice(models.Model):
    _inherit = "account.invoice"


    picking_ids = fields.One2many('stock.picking', 'invoice_id', 'Related Pickings', readonly=True,
                                  help="Related pickings (only when the invoice has been generated from the picking).")
    sale_ids = fields.Many2many('sale.order', 'sale_order_invoice_rel', 'invoice_id','order_id', 'Sale Orders',
                                readonly=True, help="This is the list of sale orders related to this invoice.")


    @api.model
    def check_from_stock(self):
        except_product_list = []

        if not self.reference == "PTV":
            for line in self.invoice_line:
                if line.product_id:
                    if line.product_id.type in ["product", "consu"] \
                            and not (line.invoice_id.sale_ids or line.invoice_id.picking_ids):
                        except_product_list.append(line.product_id.name)
                    else:
                        continue

            # if except_product_list:
            #     raise exceptions.except_orm(u"Advertencia!", u'Para facturar o crear una nota de crédito a los productos {} que son de tipo almacenable o consumibles debe hacerlo'
            #                                         u' desde un pedido de compra o conduce'.format(except_product_list))

    @api.multi
    def action_move_create(self):

        res = super(account_invoice, self).action_move_create()
        self.check_from_stock()
        try:
            if self.sale_ids and not self.picking_ids:
                picking_id = self.sale_ids[0].picking_ids[0]
                if picking_id:
                    self.pool.get("stock.picking").write(self.env.cr, self.env.uid, [picking_id.id], {"invoice_id": self.id})
        except:
            pass

        return res


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    move_line_ids = fields.One2many('stock.move', 'invoice_line_id', 'Related Stock Moves', readonly=True,
                                    help="Related stock moves (only when the invoice has been generated from the picking).")


