# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
#    Write by Eneldo Serrata (eneldo@marcos.do)
#
##############################################################################

from openerp import models, fields, api
import base64
import hashlib
from datetime import date

class monthly_daily_wizard(models.TransientModel):
    _name = "daily.book.mwizard"

    def _get_printer_domain(self):
        printer_ids = [printer.id for printer in self.env["mipf.printer.config"].search([('user_ids','=', self.env.uid)])]
        if printer_ids:
            return [('id','in',printer_ids)]

        return False

    def _get_default(self):
        printer_ids = [printer.id for printer in self.env["mipf.printer.config"].search([('user_ids','=', self.env.uid)])]
        if printer_ids:
            return printer_ids[0]
        return False

    ipf_id = fields.Many2one("mipf.printer.config", string="Seleccione la impresora", domain=_get_printer_domain,
                             default=_get_default, required=True)
    day = fields.Date("Dia", required=True, default=date.today().strftime('%Y-%m-%d'))

class monthly_book_wizard(models.TransientModel):
    _name = "monthly.book.mwizard"

    period_id = fields.Many2one("account.period", string="Periodo", readonly=False, required=True)

    @api.multi
    def generate_monthly_book(self):
        subsidiary = {}

        domain = [('date','>=',self.period_id.date_start), ('date','<=',self.period_id.date_stop)]
        for book in self.env["mipf.daily.book"].search(domain):
            if not subsidiary.get(book.subsidiary.id, False):
                subsidiary.update({book.subsidiary.id: [book]})
            else:
                subsidiary[book.subsidiary.id].append(book)

        for key, val in subsidiary.iteritems():
            book_header_sun = ["3", "{}", 0, 0.00, 0.00, "", 0.00, "", "", "", 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
            book_detail = []
            final_book = ""
            for record in val:
                daily_book_row = base64.b64decode(record.book).split("\n")

                for row in daily_book_row:
                    field_list = row.split("||")
                    if field_list[0] == "1":
                        book_header_sun[2] += int(field_list[3]) if field_list[3] else 0
                        book_header_sun[3] += float(field_list[4]) if field_list[4] else 0.00
                        book_header_sun[4] += float(field_list[5]) if field_list[5] else 0.00
                        book_header_sun[6] += float(field_list[7]) if field_list[7] else 0.00
                        book_header_sun[10] += float(field_list[11]) if field_list[11] else 0.00
                        book_header_sun[11] += float(field_list[12]) if field_list[12] else 0.00
                        book_header_sun[12] += float(field_list[14]) if field_list[14] else 0.00
                        book_header_sun[13] += float(field_list[15]) if field_list[15] else 0.00
                        book_header_sun[14] += float(field_list[17]) if field_list[17] else 0.00
                        book_header_sun[15] += float(field_list[18]) if field_list[18] else 0.00
                        book_header_sun[16] += float(field_list[20]) if field_list[20] else 0.00
                        book_header_sun[17] += float(field_list[21]) if field_list[21] else 0.00
                    book_detail.append(row)

            for idx, val in enumerate(book_header_sun):
                if isinstance(val, float):
                    book_header_sun[idx] = '%.2f' % book_header_sun[idx]
            header_line = str(book_header_sun).strip('[]').replace("'", "")+"||\n"
            header_line = header_line.replace(", ", "||")
            header_line = header_line.replace(" ", "")
            detail = ""
            for row in book_detail:
                if row:
                    detail += row+"\n"

            m = hashlib.sha1()
            m.update(detail)
            header_hash = m.hexdigest().upper()
            final_header_line = header_line.format(header_hash)
            final_book = final_header_line + detail
            old_book = self.env["mipf.monthly.book"].search([("subsidiary", "=", key), ("period_id", '=', self.period_id.id)])
            if old_book:
                old_book.unlink()
            date = self.period_id.date_start.split("-")
            filename = "LM{}{}.{}".format(date[0][2:4],date[1],key)
            values = {
                "subsidiary": key,
                "period_id": self.period_id.id,
                "book": base64.b64encode(final_book),
                "filename": filename,
                "doc_qty": book_header_sun[2],
                "total": book_header_sun[3],
                "total_tax": book_header_sun[4],
                "final_total": book_header_sun[10],
                "final_total_tax": book_header_sun[11],
                "fiscal_total": book_header_sun[12],
                "fiscal_total_tax": book_header_sun[13],
                "ncfinal_total": book_header_sun[14],
                "ncfinal_total_tax": book_header_sun[15],
                "ncfiscal_total": book_header_sun[16],
                "ncfiscal_total_tax": book_header_sun[17],
            }
            self.env["mipf.monthly.book"].create(values)
            book_header_sun = ["3", "{}", 0, 0.00, 0.00, "", 0.00, "", "", "", 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
            book_detail = []
            final_book = ""






