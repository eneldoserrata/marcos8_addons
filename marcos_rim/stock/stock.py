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
from openerp.tools.translate import _
import requests
import json
from openerp import models, api
from openerp import fields as new_fields
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import collections
from pprint import pprint as pp


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def action_done_from_ui(self, cr, uid, picking_id, context=None):
        # if context.get("from_order", False) == 'true':
        #     self.action_assign(cr, uid, picking_id, context=context)
        """ called when button 'done' is pushed in the barcode scanner UI """
        #write qty_done into field product_qty for every package_operation before doing the transfer
        pack_op_obj = self.pool.get('stock.pack.operation')

        for operation in self.browse(cr, uid, picking_id, context=context).pack_operation_ids:
            context.update({"no_recompute": True})  #this prevent do_recompute_remaining_quantities on self.create
            pack_op_obj.write(cr, uid, operation.id, {'product_qty': operation.qty_done}, context=context)

        self.pool.get("stock.picking").do_recompute_remaining_quantities(cr, uid, picking_id, context=context)
        self.do_transfer(cr, uid, [picking_id], context=context)
        #return id of next picking to work on
        return self.get_next_picking_for_ui(cr, uid, context=context)


class stock_move(osv.osv):
    _inherit = "stock.move"

    def product_price_update_before_done(self, cr, uid, ids, context=None):
        sku_type = context.get("from_qc", False)
        from_qc_skua_cost = context.get("from_qc_skua_cost", False)
        if sku_type:
            product_obj = self.pool.get('product.product')
            tmpl_dict = {}
            for move in self.browse(cr, uid, ids, context=context):
                #adapt standard price on incomming moves if the product cost_method is 'average'
                if move.product_id.cost_method == 'average':
                    product = move.product_id
                    prod_tmpl_id = move.product_id.product_tmpl_id.id
                    qty_available = move.product_id.product_tmpl_id.qty_available

                    if tmpl_dict.get(prod_tmpl_id):
                        product_avail = qty_available + tmpl_dict[prod_tmpl_id]
                    else:
                        tmpl_dict[prod_tmpl_id] = 0
                        product_avail = qty_available

                    if product_avail <= 0:
                        new_std_price = from_qc_skua_cost
                    else:
                        # Get the standard price
                        amount_unit = product.standard_price
                        if sku_type == "skua":
                            new_std_price = from_qc_skua_cost
                        if sku_type == "skub":
                            # new_std_price = ((amount_unit * product_avail) + (move.price_unit * move.product_qty)) / (product_avail + move.product_qty)
                            new_std_price = ((amount_unit * product_avail) + (from_qc_skua_cost * move.product_qty)) / (
                                product_avail + move.product_qty)

                    tmpl_dict[prod_tmpl_id] += move.product_qty
                    # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products

                    product_obj.write(cr, 1, [product.id], {'standard_price': new_std_price}, context=context)

        else:
            super(stock_move, self).product_price_update_before_done(cr, uid, ids, context=context)


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def search_serial_lot_from_qc(self, cr, uid, serial_lot, context=None):

        serial_lot_id = self.search(cr, uid, [("name", "=", serial_lot)])
        if serial_lot_id:
            serial_lot = self.browse(cr, uid, serial_lot_id)
            try:
                quant_max_id = max([quant.id for quant in serial_lot.quant_ids]) or False
            except:
                return False
            # quant_max = self.pool.get("stock.quant").browse(cr, uid, quant_max_id).id
            quant_max = self.pool.get("stock.quant").read(cr, uid, quant_max_id, ["product_id"])
            return {"sku": quant_max["product_id"][1], "id": serial_lot_id[0]}
        else:
            return False

    def make_qc(self, cr, uid, serial_lot_id, skub, qcuserinfo, context=None):
        stock_move_obj = self.pool.get("stock.move")
        product_obj = self.pool.get("product.product")

        # Validate the seleccion to check is this skb exist
        skub_id = product_obj.search(cr, uid, [("name", "=", skub)])
        if not skub_id:
            return False

        serial_lot = self.browse(cr, uid, serial_lot_id)
        quant_max_id = max([quant.id for quant in serial_lot.quant_ids])
        quant = self.pool.get("stock.quant").browse(cr, uid, quant_max_id)

        if not qcuserinfo.get("location_id", False):
            raise osv.except_osv(_('Warning!'), _('Debe de configurar la ubicacion de QC para la ubicacion de origen!'))

        if quant.product_id.id != skub_id[0]:
            values_a = {'company_id': quant.company_id.id,
                        'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'date_expected': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'group_id': False,
                        'invoice_state': 'none',
                        'location_dest_id': qcuserinfo["location_id"],
                        'location_id': quant.location_id.id,
                        'name': serial_lot.product_id.name,
                        'origin': "QC by {}".format(qcuserinfo["name"]),
                        'partner_id': False,
                        'picking_id': False,
                        'picking_type_id': 3,
                        'priority': '1',
                        'procure_method': 'make_to_stock',
                        'product_id': quant.product_id.id,
                        'product_uom': 1,
                        'product_uom_qty': 1,
                        'product_uos': False,
                        'product_uos_qty': 1,
                        'restrict_lot_id': serial_lot.id
            }

            resa = stock_move_obj.create(cr, uid, values_a, context=context)
            quant.write({"reservation_id": resa})

            values_b = {'company_id': quant.company_id.id,
                        'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'date_expected': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'group_id': False,
                        'invoice_state': 'none',
                        'location_dest_id': quant.location_id.id,
                        'location_id': qcuserinfo["location_id"],
                        'name': skub,
                        'origin': "QC by {}".format(qcuserinfo["name"]),
                        'partner_id': False,
                        'picking_id': False,
                        'picking_type_id': 3,
                        'priority': '1',
                        'procure_method': 'make_to_stock',
                        'product_id': skub_id[0],
                        'product_uom': 1,
                        'product_uom_qty': 1,
                        'product_uos': False,
                        'product_uos_qty': 1,
                        'restrict_lot_id': serial_lot.id
            }

            resb = stock_move_obj.create(cr, uid, values_b, context=context)
            quant.write({"reservation_id": resb})

            context["from_qc_skua_cost"] = quant.product_id.standard_price

            context["from_qc"] = "skua"
            stock_move_obj.action_done(cr, uid, [resa], context=context)
            context["from_qc"] = "skub"

            stock_move_obj.action_done(cr, uid, [resb], context=context)

        print_label_list = {"labels": []}
        default_printer = self.pool.get("marcos_rim.barcode_printer").browse(cr, uid, qcuserinfo["default_printer"])
        print_label_list["labels"].append(
            "{},{},{},{}".format(skub, serial_lot.name, qcuserinfo["uid"], time.strftime("%d-%m-%Y")))
        self.pool.get("stock.pack.operation").print_labels_sku(print_label_list, default_printer["host"],
                                                               default_printer["dir_path"], default_printer["sku_type"],
                                                               context={"from": "qc"})
        return True

    def get_user_daily_process(self, cr, uid, context=None):
        stock_move_obj = self.pool.get("stock.move")
        result = stock_move_obj.search_count(cr, uid, [("create_uid", "=", uid), ("location_id", "=", 7),
                                                       ("create_date", '<=', time.strftime('%Y-%m-%d 23:59:59')),
                                                       ('create_date', '>=', time.strftime('%Y-%m-%d 00:00:00'))])
        return result


    def get_last_serial_source(self, cr, uid, serial_lot_name, context=None):
        serial_lot_ids = self.search(cr, uid, [("name", "=", serial_lot_name)])
        if not serial_lot_ids:
            return False, False

        serial_lot_obj = self.browse(cr, uid, serial_lot_ids[0], context=context)
        if not serial_lot_obj.product_id.track_all:
            raise osv.except_osv(_('Warning!'), _(
                'El serial: {} que pertenece al SKUB: {} No esta configurado para tracking!'.format(serial_lot_name,
                                                                                                    serial_lot_obj.product_id.name)))
        quants = serial_lot_obj.quant_ids
        if not quants:
            return False, False
        max_quant_id = max([quant.id for quant in quants])
        max_quant = self.pool.get("stock.quant").browse(cr, uid, max_quant_id)
        return max_quant, serial_lot_ids[0]

    def get_locations(self, cr, uid, loc_barcode, context=None):
        location_ids = self.pool.get("stock.location").search(cr, uid, [("loc_barcode", "=", loc_barcode)],
                                                              context=context)
        location = self.pool.get("stock.location").browse(cr, uid, location_ids, context=context)
        if location:
            return {"id": location.id, "name": location.name}
        else:
            return False


    def get_serial_to_move(self, cr, uid, serial_lot_name, context=None):
        quant, serial_lot_ids = self.get_last_serial_source(cr, uid, serial_lot_name, context=context)

        if not quant:
            return False

        if quant.location_id.usage == u"internal":
            return {"serial": serial_lot_name, "sku": quant.product_id.name, "source_location": quant.location_id.name,
                    "product_id": quant.product_id.id}
        else:
            return False

    def move_from_to_location(self, cr, uid, vals, location_id_dest, context=None):
        res = False
        for sku in vals:
            quant, serial_lot_ids = self.get_last_serial_source(cr, uid, sku, context=context)
            if location_id_dest == quant.location_id.id:
                raise osv.except_osv(_('Warning!'), _(
                    'El serial: que pertenece al SKUB: {} que ya esta en la ubicacion de destino!'.format(
                        sku)))
            else:
                res = self.action_move(cr, uid, quant, serial_lot_ids, location_id_dest, context=context)
        if res:
            return True
        else:
            return False

    def action_move(self, cr, uid, quant, serial_lot_ids, location_id_dest, context=None):
        move_obj = self.pool.get("stock.move")
        vals = {'company_id': 1,
                'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'date_expected': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'group_id': False,
                'invoice_state': 'none',
                'location_dest_id': location_id_dest,
                'location_id': quant.location_id.id,
                'name': '{} '.format(quant.product_id.name),
                'origin': "Interno",
                'partner_id': 1,
                'picking_id': False,
                'picking_type_id': False,
                'priority': '1',
                'procure_method': 'make_to_stock',
                'product_id': quant.product_id.id,
                'product_uom': 1,
                'product_uom_qty': 1,
                'product_uos': False,
                'product_uos_qty': 1,
                'reserved_quant_ids': [],
                "restrict_lot_id": serial_lot_ids}
        new_move_id = move_obj.create(cr, uid, vals, context=None)
        move_obj.action_done(cr, uid, new_move_id, context=context)
        return True


class barcode_printer(models.Model):
    _name = 'marcos_rim.barcode_printer'

    name = new_fields.Char("Name")
    host = new_fields.Char("Host")
    dir_path = new_fields.Char("Path")
    users = new_fields.Char("Users id")
    sku_type = new_fields.Selection([("a", "SKU A"), ("b", "SKU B")], "SKU TYPE")


class stock_location(osv.osv):
    _inherit = "stock.location"

    _columns = {
        "print_barcode": fields.boolean(_(u"Print the barcode on receipt")),
        "default_printer": fields.many2one(u"marcos_rim.barcode_printer", u"Default Printer"),
        "max_qty": fields.integer("Max Qty"),
        "qc_location": fields.many2one("stock.location", "QC Location")
    }


class stock_pack_operation(osv.osv):
    _inherit = "stock.pack.operation"

    def print_labels_sku(self, print_label_list, server, dir_path, type, context={}):
        if server == 'test':
            return True
        url = "http://" + server + ":4567/barcode"
        print_label_list.update({"dir": dir_path})
        headers = {'content-type': 'application/json'}
        try:
            if context.get("from", False) == "qc":
                label = print_label_list.get("labels", False)[0].split(",")[0].split("-")[2]
                if label in ["-T-", "-S-"]:
                    print "======Not to print"
                    return True
                else:
                    result = requests.post(url, data=json.dumps(print_label_list), headers=headers)
            else:
                result = requests.post(url, data=json.dumps(print_label_list), headers=headers)
        except:
            raise osv.except_osv(_('Warning!'), _('The print server is not ready on the host!'))
        if result.status_code == 200:
            return True
        return False

    def auto_lot_product(self, cr, uid, pack_op, context=None):
        context = context or {}
        context.update({"no_recompute": True})  #this prevent do_recompute_remaining_quantities on self.create
        lot_obj = self.pool.get("stock.production.lot")
        picking_id = pack_op.picking_id.id
        processed_ids = []
        for i in range(int(pack_op.qty_done)):
            lot_id = lot_obj.create(cr, uid, {"product_id": pack_op.product_id.id})
            if pack_op.qty_done > 1:
                op = self.copy(cr, uid, pack_op.id, {'product_qty': 1, 'qty_done': 1, "lot_id": lot_id},
                               context=context)
                processed_ids.append(op)
            else:
                self.write(cr, uid, pack_op.id, {"lot_id": lot_id})
                processed_ids.append(pack_op.id)
        # pack_op.product_qty
        if len(processed_ids) > 1 and len(processed_ids) == int(pack_op.product_qty):
            pack_op.unlink()
        elif len(processed_ids) > 1 and len(processed_ids) != int(pack_op.product_qty):
            qty_remaining = float(int(pack_op.product_qty) - len(processed_ids))
            self.pool.get("stock.pack.operation").write(cr, uid, [pack_op.id],
                                                        {'product_qty': qty_remaining, "qty_done": 0}, context=context)
        if picking_id:
            self.pool.get("stock.picking").do_recompute_remaining_quantities(cr, uid, picking_id, context=context)
        return processed_ids

    def action_drop_down(self, cr, uid, ids, context=None):
        processed_ids = []
        for pack_op in self.browse(cr, uid, ids, context=None):
            if pack_op.product_id.track_all and pack_op.location_id.print_barcode and not pack_op.lot_id:
                result = self.auto_lot_product(cr, uid, pack_op, context=context)
                processed_ids = processed_ids + result

        if processed_ids:
            location_dest_id = self.read(cr, uid, processed_ids, ["location_id"])[0]["location_id"][0]
            location_print_barcode_preference = self.pool.get("stock.location").read(cr, uid, location_dest_id,
                                                                                     ["print_barcode",
                                                                                      "default_printer"])
            if location_print_barcode_preference["print_barcode"]:
                if context.get("barcode_printer_id", False):
                    printer_server = int(context["barcode_printer_id"])
                else:
                    printer_server = location_print_barcode_preference["default_printer"][0]

                if location_print_barcode_preference["default_printer"]:
                    printer_server = self.pool.get("marcos_rim.barcode_printer").read(cr, uid, printer_server,
                                                                                      ["host", "dir_path", "sku_type"])
                    host = printer_server["host"]
                    dir = printer_server["dir_path"]
                    type = printer_server["sku_type"]

                    if type == "a":
                        print_label_list = dict(labels=[",".join(
                            [op["product_id"][1][:4] + op["product_id"][1][6:], op["product_id"][1], op["lot_id"][1]])
                                                        for
                                                        op in
                                                        self.read(cr, uid, processed_ids,
                                                                  ["product_id", "lot_id", "picking_id",
                                                                   "location_id"])])
                    else:
                        print_label_list = dict(
                            labels=[
                                ",".join([op["product_id"][1], op["lot_id"][1], str(uid), time.strftime("%d-%m-%Y")])
                                for op in
                                self.read(cr, uid, processed_ids, ["product_id", "lot_id"])])
                    if self.print_labels_sku(print_label_list, host, dir, type):
                        # self.write(cr, uid, processed_ids, {'processed': 'true'}, context=context)
                        super(stock_pack_operation, self).action_drop_down(cr, uid, processed_ids, context=context)
                    else:
                        raise osv.except_osv(_('Warning!'), _('Printer error fix the problem try again!'))
                else:
                    raise osv.except_osv(_('Warning!'),
                                         _('You must assign a print server host for warehouse location!'))

        else:
            super(stock_pack_operation, self).action_drop_down(cr, uid, ids, context=context)


class QcUsers(models.Model):
    _name = 'marcos_rim.qc_users'

    # @api.model
    # def _barcode_generator(self):
    #     return 'QCUSER{}'.format(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15)))

    name = new_fields.Char("Nombre", required=True)
    usuario = new_fields.Char("usuario", required=True)
    password = new_fields.Char("Clave", required=True)
    # barcode = new_fields.Char("Codigo", required=True, default=_barcode_generator, readonly=True)
    canfix = new_fields.Boolean("Puede rectificar")
    location_id = new_fields.Many2one("stock.location", "QC Location", default=7, required=True, readonly=True)
    default_printer = new_fields.Many2one(u"marcos_rim.barcode_printer", u"Default Printer", required=True)
    qc_user = new_fields.Many2one("res.users", "System User", required=True)
    metadiaria = new_fields.Char("Meta diaria")
    active = new_fields.Boolean("Activo", default=True)

    _sql_constraints = [('qc_name_unique', 'UNIQUE(usuario)', "Este usuario ya esta creado")]

    @api.model
    def create(self, values):
        #TODO Set QC group to new exiting user
        user_obj = self.pool.get('res.users')
        user_id = user_obj.search(self.env.cr, self.env.uid, [("login", "=", values["usuario"])])
        if not user_id and not values.get("qc_user", False):
            vals = {
                "name": values["name"],
                "login": values["usuario"],
                "password": values["password"],
                "active": values.get("active", True)
            }
            new_user = user_obj.copy(self.env.cr, self.env.uid, 17, vals, context=self.env.context)
            values.update({"qc_user": new_user})
        elif user_id:
            values.update({"qc_user": user_id[0]})
        return super(QcUsers, self).create(values)

    @api.one
    def write(self, values):
        user_obj = self.pool.get('res.users')
        vals = {
            # "name": values.get("name", self.name),
            # "login": values.get("usuario", self.usuario),
            "password": values.get("password", self.password),
            "active": values.get("active", self.active)
        }
        user_obj.write(self.env.cr, self.env.uid, self.qc_user.id, vals, context=self.env.context)
        return super(QcUsers, self).write(values)

    @api.model
    def get_qc_user(self):
        qc_user_rec = self.search([("qc_user", "=", self.env.uid)])
        res = {
            "uid": self.env.uid,
            'name': qc_user_rec.qc_user.name,
            'canfix': qc_user_rec.canfix,
            'location_id': qc_user_rec.location_id.id,
            'default_printer': qc_user_rec.default_printer.id
        }
        return res


class SkuReport(models.Model):
    _name = "marcos.rim.sku.report"

    query_string = """
      SELECT
        "stock_production_lot"."name",
        "stock_move"."origin",
        "product_template"."name",
        "stock_move"."price_unit",
        "stock_move"."price_unit",
        "product_category"."name",
        "product_template"."clasification",
        "stock_location"."name"
      FROM  "stock_quant"
        INNER JOIN "stock_production_lot"  ON "stock_quant"."lot_id" = "stock_production_lot"."id"
        INNER JOIN "stock_quant_move_rel"  ON "stock_quant_move_rel"."quant_id" = "stock_quant"."id"
        INNER JOIN "stock_move"  ON "stock_quant_move_rel"."move_id" = "stock_move"."id"
        INNER JOIN "product_product"  ON "stock_move"."product_id" = "product_product"."id"
        INNER JOIN "product_template"  ON "product_product"."product_tmpl_id" = "product_template"."id"
        INNER JOIN "product_category"  ON "product_template"."categ_id" = "product_category"."id"
        INNER JOIN "stock_location"  ON "stock_move"."location_dest_id" = "stock_location"."id"
      ORDER BY "stock_move"."id" DESC
    """

    @api.model
    def get_po(self):
        self.env.cr.execute(self.query_string)
        history_list = self.env.cr.fetchall()
        history_dict = {}
        while history_list:
            move = history_list.pop()
            if not history_dict.get(move[0], False):
                history_dict[move[0]] = []
                                          #origin  sku      q.cost   m.cost   clasi    location
            history_dict[move[0]].append((move[1], move[2], move[3], move[4], move[5], move[6], move[7]))

        od = collections.OrderedDict(sorted(history_dict.items()))
        render_list = []
        for item in od.items():
            first, last = item[1][0], item[1][-1]

            render_list.append({"po": first[0],
                                "tuid": item[0],
                                "skua": first[1],
                                "costa": first[2],
                                "qualitya": first[4],

                                "skub": last[1],
                                "costb": last[3],
                                "qualityb": last[4],
                                "clasification": last[5],
                                "last_location": last[6]
                                })


        if self.env.context.get("json", False):
            return json.dumps(render_list)
        else:
            return render_list

    @api.model
    def get_report_summary(self, selected):

        data = self.with_context(local=True).get_po()

        sku_summary = {"skua": {}, "qualitya": {}, "skub": {}, "qualityb": {}, "clasification": {}}

        if selected[0] == "all":
            pass
        elif selected[0].startswith("PO") or selected[0].startswith("SO"):
            data = [po for po in data if po.get("po", False) == selected[0]]

        for po in data:
            if not sku_summary["skua"].get(po["skua"], False):
                sku_summary["skua"][po["skua"]] = 1
            else:
                sku_summary["skua"][po["skua"]] += 1

            if not sku_summary["qualitya"].get(po["qualitya"], False):
                sku_summary["qualitya"][po["qualitya"]] = 1
            else:
                sku_summary["qualitya"][po["qualitya"]] += 1

            if not sku_summary["skub"].get(po["skub"], False):
                sku_summary["skub"][po["skub"]] = 1
            else:
                sku_summary["skub"][po["skub"]] += 1

            if not sku_summary["qualityb"].get(po["qualityb"], False):
                sku_summary["qualityb"][po["qualityb"]] = 1
            else:
                sku_summary["qualityb"][po["qualityb"]] += 1

            if not sku_summary["clasification"].get(po["clasification"], False):
                sku_summary["clasification"][po["clasification"]] = 1
            else:
                sku_summary["clasification"][po["clasification"]] += 1

        return sku_summary


