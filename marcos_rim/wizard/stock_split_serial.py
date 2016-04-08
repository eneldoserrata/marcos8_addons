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
# from openerp import models, api
#
#
# class stock_picking_account_move(models.TransientModel):
#     """
#     This wizard will make all account_move from picking
#     """
#     _name = "marcos_rim.picking.split.serial"
#     _description = "split and serial all the products in picking in"
#
#     def _default_session(self):
#         return self.env['stock.picking'].browse(self._context.get('active_id'))
#
#     @api.multi
#     def split_and_serial(self):
#         moves_lines = [move.id for move in self.env["stock.picking"].browse(self.env.context["active_ids"]).move_lines]
#         moves = [move for move in self.env["stock.move"].browse(moves_lines)]
#         new_ids = self.sql_split_move(moves)
#         # split = self.pool.get("stock.move").split(self.env.cr, self.env.uid, moves[1], 1)
#         return {'type': 'ir.actions.act_window_close'}
#
#     def sql_split_move(self, moves):
#         new_ids =[]
#         for move in moves:
#             if int(move.product_qty) == 1:
#                 continue
#             else:
#                 for index in range(int(move.product_qty)):
#                     print index
#                     duplicate_move_query = """
#                     INSERT INTO stock_move (origin,product_uos_qty,product_uom,price_unit,product_uom_qty,procure_method,
#                         product_uos,location_id,priority,picking_type_id,partner_id,company_id,note,state,product_packaging,
#                         purchase_line_id,weight_uom_id,date_expected,procurement_id,warehouse_id,inventory_id,
#                         partially_available,propagate,restrict_partner_id,date,restrict_lot_id,push_rule_id,
#                         name,invoice_state,rule_id,location_dest_id,group_id,product_id,picking_id,create_uid,write_uid,
#                         create_date,write_date,product_qty)
#                     (SELECT
#                         origin,1,product_uom,price_unit,1,procure_method,product_uos,location_id,priority,picking_type_id,
#                         partner_id,company_id,note,state,product_packaging,purchase_line_id,weight_uom_id,date_expected,
#                         procurement_id,warehouse_id,inventory_id,partially_available,propagate,restrict_partner_id,
#                         date,restrict_lot_id,push_rule_id,name,invoice_state,rule_id,location_dest_id,group_id,
#                         product_id,picking_id,create_uid,write_uid,create_date,write_date,
#                         1 FROM stock_move WHERE id = %s) RETURNING id
#                     """
#                     self.env.cr.execute(duplicate_move_query, (move.id,))
#                     new_id = self.env.cr.fetchone()[0]
#                     new_ids.append(new_id)
#
#
#
#                     query1 = """
#                         delete from stock_location_route_move where move_id=%s AND route_id IN (SELECT stock_location_route_move.route_id
#                         FROM stock_location_route_move, "stock_location_route" WHERE stock_location_route_move.move_id=%s
#                         AND stock_location_route_move.route_id = stock_location_route.id )
#                     """
#
#                     self.env.cr.execute(query1, (new_id,new_id))
#
#                     query2 = """
#                     insert into stock_location_route_move (move_id,route_id) values (%s, %s)
#                     """
#
#                     self.env.cr.execute(query2, (new_id, 2))
#
#                     query3 = """
#                     insert into stock_location_route_move (move_id,route_id) values (%s, %s)
#                     """
#                     self.env.cr.execute(query3, (new_id, 3))
#
#                     query4 = """
#                     delete from stock_quant_move_rel where move_id=%s AND quant_id
#                     IN (SELECT stock_quant_move_rel.quant_id FROM stock_quant_move_rel, "stock_quant"
#                     WHERE stock_quant_move_rel.move_id=%s AND stock_quant_move_rel.quant_id = stock_quant.id )
#                     ORDER BY id
#                     """
#
#                 delete_old_move_query = """
#                 DELETE FROM stock_move where id = %s
#                 """
#                 self.env.cr.execute(delete_old_move_query, (move.id,))
#
#         return new_ids
#
#
#     @api.multi
#     def split_order_line_by_one(self):
#         order_lines = [move.id for move in self.env["purchase.order"].browse(self.env.context["active_ids"]).order_line]
#         lines = [line for line in self.env["purchase.order.line"].browse(order_lines)]
#         new_ids = self.sql_split_order_lines(lines)
#         # split = self.pool.get("stock.move").split(self.env.cr, self.env.uid, moves[1], 1)
#         return {'type': 'ir.actions.act_window_close'}
#
#
#     def sql_split_order_lines(self, lines):
#         new_ids =[]
#         count = 0
#         for line in lines:
#             if int(line.product_qty) == 1:
#                 continue
#             else:
#                 for index in range(int(line.product_qty)):
#                     query = """
#                     INSERT INTO "purchase_order_line"
#                                  (
#                                    "name",
#                                    "product_uom",
#                                    "date_planned",
#                                    "order_id",
#                                    "price_unit",
#                                    "state",
#                                    "product_qty",
#                                    "account_analytic_id",
#                                    "invoiced",
#                                    "product_id",
#                                    "create_uid",
#                                    "write_uid",
#                                    "create_date",
#                                    "write_date")
#                                (SELECT "name",
#                                    "product_uom",
#                                    "date_planned",
#                                    "order_id",
#                                    "price_unit",
#                                    "state",
#                                    1,
#                                    "account_analytic_id",
#                                    "invoiced",
#                                    "product_id",
#                                    "create_uid",
#                                    "write_uid",
#                                    "create_date",
#                                    "write_date" FROM "purchase_order_line" WHERE id = %s) RETURNING id
#                                     """
#
#                     self.env.cr.execute(query, (line.id,))
#                     new_ids.append(self.env.cr.fetchone()[0])
#
#             query = """
#             DELETE FROM "purchase_order_line" WHERE id = %s
#             """
#             self.env.cr.execute(query, (line.id,))
#             count += 1
#             print count
#
#         return new_ids
#
