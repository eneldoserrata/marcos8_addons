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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    ACCOUNT_MOVE_INSERT = """
        INSERT INTO "account_move" (
        "id",
        "name",
        "journal_id",
        "company_id",
        "state",
        "period_id",
        "date",
        "ref",
        "to_check",
        "create_uid",
        "write_uid",
        "create_date",
        "write_date")
        VALUES(
        nextval('account_move_id_seq'),
        %(name)s,
        %(journal_id)s,
        %(company_id)s,
        %(state)s,
        %(period_id)s,
        %(date)s,
        %(ref)s,
        %(to_check)s,
        %(uid)s,
        %(uid)s,
        (now() at time zone 'UTC'),
        (now() at time zone 'UTC'))
        RETURNING id
    """

    ACCOUNT_MOVE_LINE_INSERT = """
    INSERT INTO "account_move_line" (
        "id",
        "ref",
        "account_id",
        "name",
        "quantity",
        "centralisation",
        "product_uom_id",
        "journal_id",
        "company_id",
        "currency_id",
        "credit",
        "state",
        "product_id",
        "period_id",
        "debit",
        "date",
        "date_created",
        "amount_currency",
        "partner_id",
        "move_id",
        "blocked",
        "create_uid",
        "write_uid",
        "create_date",
        "write_date")
    VALUES(
        nextval('account_move_line_id_seq'),
        %(ref)s,
        %(account_id)s,
        %(name)s,
        %(quantity)s,
        'normal',
        %(product_uom_id)s,
        %(journal_id)s,
        1,
        NULL,
        %(credit)s,
        'draft',
        %(product_id)s,
        %(period_id)s,
        %(debit)s,
        %(date)s,
        '2014-12-28',
        0.0,
        %(partner_id)s,
        %(move_id)s,
        false,
        %(uid)s,
        %(uid)s,
        (now() at time zone 'UTC'),
        (now() at time zone 'UTC')) RETURNING id
    """

    def action_done(self, cr, uid, ids, context=None):
        context = context or {}
        if context.get("from_scan", False):
            picking_obj = self.pool.get("stock.picking")
            quant_obj = self.pool.get("stock.quant")
            picking = picking_obj.browse(cr, uid, ids, context=context)
            moves = picking.move_lines
            stock_quant_move_rel = []
            for move in moves:
                for quant in move.reserved_quant_ids:
                    stock_quant_move_rel.append({"quant_id": quant, "move_id": move, "location_dest_id": move.location_dest_id.id})

            quants_ids = [{"id": d["quant_id"].id, "location_dest_id": d["location_dest_id"]} for d in stock_quant_move_rel]
            for uquant in quants_ids:
                cr.execute("UPDATE stock_quant SET location_id=%(location_dest_id)s WHERE id = %(id)s", uquant)

            quants_move_rel = [{"quant_id": d["quant_id"].id, "move_id": d["move_id"].id} for d in stock_quant_move_rel]
            for quant_move_rel in quants_move_rel:

                cr.execute("insert into stock_quant_move_rel (quant_id,move_id) values (%(quant_id)s, %(move_id)s)", quant_move_rel)

            journal_id, acc_src, acc_dest, acc_valuation = quant_obj._get_accounting_data_for_valuation(cr, uid, moves[0], context=context)
            period_id = self.pool.get('account.period').find(cr, uid, moves[0].date, context=context)[0]
            move_dic = {
                        'name': picking.name,
                        'journal_id': journal_id,
                        'company_id': 1,
                        'state': u'draft',
                        'period_id': period_id,
                        'date': moves[0].date,
                        'ref': moves[0].picking_id.name,
                        'to_check': False,
                        'uid': uid}

            cr.execute(self.ACCOUNT_MOVE_INSERT, move_dic)
            account_move_id = move_id = cr.fetchone()[0]

            account_move_lines = []
            for move in moves:
                quant_cost_qty = {}
                for quant in move.reserved_quant_ids:
                    if quant_cost_qty.get(quant.cost):
                        quant_cost_qty[quant.cost] += quant.qty
                    else:
                        quant_cost_qty[quant.cost] = quant.qty

                for cost, qty in quant_cost_qty.items():
                    move_lines = quant_obj._prepare_account_move_line(cr, uid, move, qty, cost, acc_src, acc_valuation, context=context)
                    move_lines[0][2]["journal_id"] = move_lines[1][2]["journal_id"] = journal_id
                    move_lines[0][2]["period_id"] = move_lines[1][2]["period_id"] = period_id
                    move_lines[0][2]["move_id"] = move_lines[1][2]["move_id"] = account_move_id
                    move_lines[0][2]["uid"] = move_lines[1][2]["uid"] = uid
                    account_move_lines.append(move_lines[0][2])
                    account_move_lines.append(move_lines[1][2])
                quant_obj.quants_unreserve(cr, uid, move, context=context)
            for line in account_move_lines:
                cr.execute(self.ACCOUNT_MOVE_LINE_INSERT, line)

            self.pool.get("stock.move").write(cr, uid, [m.id for m in moves], {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
            picking_obj.write(cr, uid, ids, {'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
            return True

        else:
            return super(stock_picking, self).action_done(cr, uid, ids, context=context)


class procurement_order(osv.osv):
    _inherit = "procurement.order"

    MOVE_INSERT = """
        INSERT INTO "stock_move" (
                            "id",
                            "origin",
                            "product_uos_qty",
                            "product_qty",
                            "product_uom",
                            "product_uom_qty",
                            "date",
                            "product_uos",
                            "partner_id",
                            "picking_type_id",
                            "location_id",
                            "company_id",
                            "priority",
                            "state",
                            "weight_uom_id",
                            "date_expected",
                            "procurement_id",
                            "warehouse_id",
                            "propagate",
                            "move_dest_id",
                            "procure_method",
                            "product_id",
                            "name",
                            "partially_available",
                            "invoice_state",
                            "location_dest_id",
                            "group_id",
                            "rule_id",
                            "create_uid",
                            "write_uid",
                            "create_date",
                            "write_date")
                    VALUES(
                           nextval('stock_move_id_seq'),
                           %(origin)s,
                           %(product_uos_qty)s,
                           %(product_uos_qty)s,
                           %(product_uom)s,
                           %(product_uom_qty)s,
                           %(date)s,
                           %(product_uos)s,
                           %(partner_id)s,
                           %(picking_type_id)s,
                           %(location_id)s,
                           %(company_id)s,
                           %(priority)s,
                           'draft',
                           3,
                           %(date_expected)s,
                           %(procurement_id)s,
                           %(warehouse_id)s,
                           %(propagate)s,
                           NULL,
                           'make_to_stock',
                           %(product_id)s,
                           %(name)s,
                           false,
                           %(invoice_state)s,
                           %(location_dest_id)s,
                           %(group_id)s,
                           %(rule_id)s,
                           %(uid)s,
                           %(uid)s,
                           (now() at time zone 'UTC'),
                           (now() at time zone 'UTC'))
                           RETURNING id
    """

    def _custom_move_create(self, cr, uid, procurement, context=None):
        move_list = []
        move_ids = []

        procurement_ids = [p.id for p in procurement]
        cr.execute("""UPDATE "procurement_order" SET "rule_id"=17,"write_uid"=%s,"write_date"=(now() at time zone 'UTC') WHERE id IN %s""", (uid, tuple(procurement_ids)))
        for proc in procurement:
            proc.refresh()
            move_dict = self._run_move_create(cr, uid, proc, context=None)
            move_dict["uid"] = uid
            move_list.append(move_dict)
        for move in move_list:
            cr.execute(self.MOVE_INSERT, move)
            move_id = cr.fetchone()
            move_ids.append(move_id[0])
        if move_ids:
            # self.pool.get('stock.move').browse(cr, uid, move_ids, context=context).refresh()
            self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)

        sale_order_obj = self.pool.get("sale.order")
        move_obj = self.pool.get("stock.move")
        quant_obj = self.pool.get("stock.quant")
        lot_obj = self.pool.get("stock.production.lot")

        order_id = sale_order_obj.search(cr, uid, [("name", "=", procurement[0].origin)])
        order = sale_order_obj.browse(cr, uid, order_id)
        reserved_tuid = {}
        for lines in order.order_line:
            if lines.tuids:
                reserved_tuid[lines.product_id.id] = eval(lines.tuids)

        for key, value in reserved_tuid.iteritems():
            move_id = move_obj.search(cr, uid, [("product_id", "=", key), ("group_id", "=", procurement[0].group_id.id), ("state", "=", "confirmed")], context=context)
            quant_list = []
            for tuid in value:
                lot = lot_obj.search(cr, uid, [("name", "=", tuid)])
                quant = quant_obj.search(cr, uid, [("lot_id", "in", lot)])
                quant_list.append((4, max(quant)))

            move_obj.write(cr, uid, move_id, {"reserved_quant_ids": quant_list})

        picking_obj = self.pool.get("stock.picking")
        picking_id = picking_obj.search(cr, uid, [("group_id", "=", procurement[0].group_id.id), ("state", "=", "confirmed")])[0]
        move_ids = move_obj.search(cr, uid, [("group_id", "=", procurement[0].group_id.id), ("state", "=", "confirmed")], context=context)

        cr.execute("UPDATE stock_move SET state='assigned' WHERE id IN %s", (tuple(move_ids),))
        cr.execute("UPDATE stock_picking SET state='assigned' WHERE id = %s", (picking_id,))

        picking_obj.do_prepare_partial(cr, uid, [picking_id], context=context)

        pack_obj = self.pool.get('stock.pack.operation')
        pack_ids = pack_obj.search(cr, uid, [("picking_id", "=", picking_id)])
        cr.execute("update stock_pack_operation set qty_done = product_qty where id in %s", (tuple(pack_ids),))
        print "============action_done start========================"
        picking_obj.action_done(cr, uid, picking_id, context=context)

    def run(self, cr, uid, ids, autocommit=False, context=None):

        # Sale order sequence is mandatory to start with SO
        if context.get("from_scan", False):
            procurement = self.browse(cr, uid, ids, context=context)
            self._custom_move_create(cr, uid, procurement, context=context)
            return True
        else:
            return super(procurement_order, self).run(cr, uid, ids, autocommit=False, context=context)


class sale_order(osv.osv):
    _inherit = 'sale.order'

    procurement_insert = """
            INSERT INTO "procurement_order" (
            "id",
            "origin",
            "product_uos_qty",
            "partner_dest_id",
            "name",
            "product_uom",
            "sale_line_id",
            "date_planned",
            "company_id",
            "invoice_state",
            "warehouse_id",
            "priority",
            "state",
            "product_qty",
            "product_uos",
            "group_id",
            "location_id",
            "product_id",
            "create_uid",
            "write_uid",
            "create_date",
            "write_date"
            ) VALUES(
            nextval('procurement_order_id_seq'),
            %(origin)s,
            %(product_uos_qty)s,
            %(partner_dest_id)s,
            %(name)s,
            %(product_uom)s,
            %(sale_line_id)s,
            %(date_planned)s,
            %(company_id)s,
            %(invoice_state)s,
            %(warehouse_id)s,
            '1',
            'confirmed',
            %(product_qty)s,
            %(product_uos)s,
            %(group_id)s,
            %(location_id)s,
            %(product_id)s,
            %(uid)s,
            %(uid)s,
            (now() at time zone 'UTC'),
            (now() at time zone 'UTC')) RETURNING id
            """

    def _calc_product_qty(self, cr, uid, ids, name, attr, context=None):

        res = {}
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            cantidad = 0
            for line in order.order_line:
                cantidad += int(line.product_uom_qty)
            res[order.id] = cantidad
        return res

    _columns = {
        "from_scan": fields.boolean("Escaneado", default=False),
        "product_qty_total": fields.function(_calc_product_qty, string="Total de productos", type='integer'),
    }

    def action_ship_create(self, cr, uid, ids, context=None):
        context = context or {}
        order = self.browse(cr, uid, ids, context=context)
        if order.from_scan:
            procurement_obj = self.pool.get('procurement.order')
            vals = self._prepare_procurement_group(cr, uid, order, context=context)
            if not order.procurement_group_id:
                group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                order.write({'procurement_group_id': group_id})
            vals_list = []
            proc_ids = []
            for line in order.order_line:
                vals_dict = self._prepare_order_line_procurement(cr, uid, order, line, group_id=order.procurement_group_id.id, context=context)
                vals_dict["uid"] = uid
                vals_list.append(vals_dict)
            for vals in vals_list:
                cr.execute(self.procurement_insert, vals)
                proc_id = cr.fetchone()
                proc_ids.append(proc_id[0])

            context["from_scan"] = True
            procurement_obj.run(cr, uid, proc_ids, context=context)

            #if shipping was in exception and the user choose to recreate the delivery order, write the new status of SO
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
                order.write(val)
            return True
        else:
            return super(sale_order, self).action_ship_create(cr, uid, ids, context=context)

    def update_from_ui(self, cr, uid, order_id, values, context=None):
        order_line_obj = self.pool.get("sale.order.line")
        order = self.browse(cr, uid, int(order_id), context=context)
        order_line_id = order_line_obj.search(cr, uid, [("order_id", "=", order.id)])
        order_line_obj.unlink(cr, uid, order_line_id);
        for line in values:
            row_line = {'address_allotment_id': False,
                     'delay': 7,
                     'discount': 0,
                     'name': line["sku"],
                     'order_id': int(order_id),
                     'price_unit': line["values"]["precio"],
                     'product_id': line["values"]["product_id"],
                     'product_packaging': False,
                     'product_tmpl_id': line["values"]["product_tmpl_id"],
                     'product_uom': 1,
                     'product_uom_qty': line["values"]["scaneado"],
                     'product_uos': False,
                     'product_uos_qty': 1,
                     'route_id': False,
                     'tax_id': [[6, False, [19]]],
                     'th_weight': 0,
                     'tuids': line["values"]["tuid"],
                     'state': "confirmed"}
            order_line_obj.create(cr, uid, row_line, context=context)

        self.write(cr, uid, int(order_id), {"from_scan": True})
        return True

    def open_barcode_interface_from_order(self, cr, uid, order_ids, context=None):
        order = self.browse(cr, uid, order_ids)

        final_url = "/salepicking/?#action=marcosrim.SalePickingWidget&from_order=true&order_name={}&cliente={}&order_id={}&state={}".format(
            order[0].name, order[0].partner_id.name, order[0].id, order[0].state)

        return {'type': 'ir.actions.act_url', 'url': final_url, 'target': 'self'}

    def get_serial_to_sale(self, cr, uid, serial_lot_name, order_id, context=None):
        result = self.pool.get("stock.production.lot").get_serial_to_move(cr, uid, serial_lot_name, context=context)
        if not result:
            return result
        order_line = self.pool.get("sale.order.line").search(cr, uid, [('order_id', '=', int(order_id)), ('product_id', '=', result["product_id"])], context=context)
        if order_line:
            order_line = self.pool.get("sale.order.line").browse(cr, uid, order_line, context=context)
            qty = int(order_line.product_uom_qty)
            price = order_line.price_unit
            product_tmpl_id = order_line.product_id.product_tmpl_id.id
            clasification = order_line.product_id.product_tmpl_id.clasification
            result.update({"cotizado": qty, "precio": price, "product_tmpl_id": product_tmpl_id, "clasification": clasification, "tuid": serial_lot_name})
        else:
            order_line = self.pool.get("product.product").browse(cr, uid, result["product_id"], context=context)
            qty = 0
            price = order_line.list_price
            clasification = order_line.product_tmpl_id.clasification
            product_tmpl_id = order_line.product_tmpl_id.id
            result.update({"cotizado": qty, "precio": round(price), "product_tmpl_id": product_tmpl_id, "clasification": clasification, "tuid": serial_lot_name})
        return result

    def pull_scaned(self, cr, uid, order_id, context=None):
        order_tuid = []
        order_lines = self.pool.get('sale.order').browse(cr, uid, int(order_id)).order_line
        for line in order_lines:
            if line.tuids:
                order_tuid += eval(line.tuids)
        return order_tuid


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {'tuids': fields.char("Tuids")}

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Allows to delete sales order lines in draft,cancel states"""
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.tuids:
                self.write(cr, uid, rec.id, {"state": "draft"})
        return super(sale_order_line, self).unlink(cr, uid, ids, context=context)



    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False,
                          flag=False, context=None):


        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
                                                             uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                                                             partner_id=partner_id,
                                                             lang=lang, update_tax=update_tax, date_order=date_order,
                                                             packaging=packaging, fiscal_position=fiscal_position,
                                                             flag=flag, context=context)

        if res["value"].get("name", False):
            if res["value"]["name"].startswith("U-PLT") or res["value"]["name"].startswith("PLT"):
                for locationlist in self.get_inventory_location(cr, uid, product, context=context):
                    res["value"]["name"] += '\n{}'.format(' '.join(locationlist))
        return res

    def get_inventory_location(self, cr, uid, product_id, context=None):
        product_quant_ids = self.pool.get('stock.quant').search(cr, uid, [("product_id", "=", product_id),
                                                                          ("location_id.usage", "=", u"internal")],
                                                                order="location_id", context=context)
        locations_names = [quant.location_id.name for quant in
                           self.pool.get('stock.quant').browse(cr, uid, product_quant_ids, context=context)]
        noDupes = []
        [noDupes.append(i) for i in locations_names if not noDupes.count(i)]
        split_noDupes_func = lambda split_noDupes, sz: [split_noDupes[i:i + sz] for i in
                                                        range(0, len(split_noDupes), sz)]
        return split_noDupes_func(noDupes, 10)


