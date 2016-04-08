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
from openerp.osv import osv
from openerp import models, api, fields
from openerp.tools.translate import _
import time
import requests
import json


class PrintLabel(models.TransientModel):
    _name = "marcos.rim.serial.label.print"

    printer = fields.Many2one("marcos_rim.barcode_printer", "Impresora", required=True)
    tuids_list = fields.Text("Lista de TUID")

    @api.one
    def print_label(self):
        print_label_list = {"labels": []}
        active_ids = []
        if self.tuids_list:
            tuid_list = [tuid.strip() for tuid in self.tuids_list.split("\n")]
            for tuid in tuid_list:
                active_ids += self.pool.get("stock.production.lot").search(self.env.cr, self.env.uid, [("name", "=", tuid)])
            serials = self.pool.get("stock.production.lot").browse(self.env.cr, self.env.uid, active_ids)
        else:
            serials = self.pool.get("stock.production.lot").browse(self.env.cr, self.env.uid, self.env.context["active_ids"])

        if self.printer.sku_type == "b":
            for serial in serials:
                print_label_list["labels"].append("{},{},{},{}".format(serial.product_id.name, serial.name, self.env.uid, time.strftime("%d-%m-%Y")))
            self.print_labels_sku(print_label_list, self.printer.host, self.printer.dir_path)
        else:
            for serial in serials:
                fieldsplit = serial.product_id.name.split("-")
                fielda = "{}-{}".format(fieldsplit[0],fieldsplit[2])
                print_label_list["labels"].append("{},{},{}".format(fielda, serial.product_id.name, serial.name))

            self.print_labels_sku(print_label_list, self.printer.host, self.printer.dir_path)

    def print_labels_sku(self, print_label_list, server, dir):
        if server == 'test':
            return True
        url = "http://" + server + ":4567/barcode"
        print_label_list.update({"dir": dir})
        headers = {'content-type': 'application/json'}
        try:
            result = requests.post(url, data=json.dumps(print_label_list), headers=headers)
        except:
            raise osv.except_osv(_('Warning!'), _('The print server is not ready on the host!'))
        if result.status_code == 200:
            return True
        return False


