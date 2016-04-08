# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
#    Write by Eneldo Serrata (eneldo@marcos.do)
#
##############################################################################

from openerp import models, fields, api, exceptions
import openerp.addons.decimal_precision as dp
import base64

class subsidiary(models.Model):
    _name = "mipf.subsidiary"

    name = fields.Char("Sucursal", required=True)


class ipf_printer_config(models.Model):
    _name = 'mipf.printer.config'

    name = fields.Char("Descripcion", required=True)
    host = fields.Char("Host", required=True)
    user_ids = fields.Many2many('res.users', string="Usuarios", required=True)
    print_copy = fields.Boolean("Imprimir con copia", default=False)
    subsidiary = fields.Many2one("mipf.subsidiary", string="Sucursal", required=True)
    daily_book_ids = fields.One2many("mipf.daily.book", "printer_id", string="Libros diarios")
    state = fields.Selection([("deactivate", "Desactivada"), ("active", "Activa")], default="deactivate")
    serial = fields.Char("Serial de la impresora", readonly=True)

    def set_book_totals(self, book):
        book_header_sun = [0, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
        daily_book_row = base64.b64decode(book.book).split("\n")

        for row in daily_book_row:
            field_list = row.split("||")
            if field_list[0] == "1":
                book_header_sun[0] += int(field_list[3]) if field_list[3] else 0
                book_header_sun[1] += float(field_list[4]) if field_list[4] else 0.00
                book_header_sun[2] += float(field_list[5]) if field_list[5] else 0.00
                book_header_sun[3] += float(field_list[11]) if field_list[11] else 0.00
                book_header_sun[4] += float(field_list[12]) if field_list[12] else 0.00
                book_header_sun[5] += float(field_list[14]) if field_list[14] else 0.00
                book_header_sun[6] += float(field_list[15]) if field_list[15] else 0.00
                book_header_sun[7] += float(field_list[17]) if field_list[17] else 0.00
                book_header_sun[8] += float(field_list[18]) if field_list[18] else 0.00
                book_header_sun[9] += float(field_list[20]) if field_list[20] else 0.00
                book_header_sun[10] += float(field_list[21]) if field_list[21] else 0.00

        values = {
            "doc_qty": book_header_sun[0],
            "total": book_header_sun[1],
            "total_tax": book_header_sun[2],
            "final_total": book_header_sun[3],
            "final_total_tax": book_header_sun[4],
            "fiscal_total": book_header_sun[5],
            "fiscal_total_tax": book_header_sun[6],
            "ncfinal_total": book_header_sun[7],
            "ncfinal_total_tax": book_header_sun[8],
            "ncfiscal_total": book_header_sun[9],
            "ncfiscal_total_tax": book_header_sun[10],
        }

        return book.write(values)

    @api.model
    def save_book(self, new_book, serial, bookday):
        printer_id = self.get_ipf_host(get_id=True)
        date = bookday.split("-")
        filename = "LV{}{}{}.000".format(date[0][2:4],date[1],date[2])

        book = self.env["mipf.daily.book"].search([('serial', '=', serial), ('date', '=', bookday)])
        if book:
            book.unlink()

        values = {"printer_id": printer_id, "date": bookday, "book": base64.b64encode(new_book), "serial": serial, "filename": filename}

        new_book = self.env["mipf.daily.book"].create(values);

        self.set_book_totals(new_book)

        return True

    def ncf_fiscal_position_exception(self, partner_name):
        raise exceptions.Warning(u'Tipo de comprobante fiscal inválido!',
                u"El tipo de comprobante no corresponde a la posicion fical del cliente '%s'!" % (partner_name))

    @api.model
    def get_user_printer(self):
        return self.search([("user_ids", "=", self.env.uid)])

    @api.model
    def get_ipf_host(self, get_id=False):
        printer = False
        if self._context.get("from_wizard", False):
            printer = self.browse(self._context["ipf_id"])
        elif self._context.get("active_model", False) == "mipf.printer.config":
            printer = self.browse(self._context["active_id"])
        else:
            printer = self.get_user_printer()

        if printer:
            if get_id:
                return printer.id
            else:
                return {"host": printer.host}
        else:
            raise exceptions.Warning("Las impresoras fiscales no estan configuradas!")


class ipf_daily_book(models.Model):
    _name = "mipf.daily.book"
    _order = "date"

    printer_id = fields.Many2one("mipf.printer.config", readonly=True)
    subsidiary = fields.Many2one(string="Sucursal", related="printer_id.subsidiary")
    date = fields.Date("Fecha", readonly=True)
    serial = fields.Char("Serial de la impresora", readonly=True)
    book = fields.Binary("Libro diario", readonly=True)
    filename = fields.Char("file name", readonly=True)

    doc_qty = fields.Integer("Doc", digits=dp.get_precision('Account'))
    total = fields.Float("Total", digits=dp.get_precision('Account'))
    total_tax = fields.Float("Total Itbis", digits=dp.get_precision('Account'))
    final_total = fields.Float("Final", digits=dp.get_precision('Account'))
    final_total_tax = fields.Float("Final Itbis", digits=dp.get_precision('Account'))
    fiscal_total = fields.Float("Fiscal", digits=dp.get_precision('Account'))
    fiscal_total_tax= fields.Float("Fiscal Itbis", digits=dp.get_precision('Account'))
    ncfinal_total = fields.Float("NC final", digits=dp.get_precision('Account'))
    ncfinal_total_tax = fields.Float("NC final Itbis", digits=dp.get_precision('Account'))
    ncfiscal_total = fields.Float("NC fiscal", digits=dp.get_precision('Account'))
    ncfiscal_total_tax = fields.Float("NC fiscal Itbis", digits=dp.get_precision('Account'  ))


class ipf_monthly_book(models.Model):
    _name = "mipf.monthly.book"

    subsidiary = fields.Many2one("mipf.subsidiary", string="Sucursal", required=True)
    period_id = fields.Many2one("account.period", string="Periodo", readonly=False, required=True)
    book = fields.Binary("Libro Mensual", readonly=True)
    filename = fields.Char("file name")

    doc_qty = fields.Integer("Doc", digits=dp.get_precision('Account'))
    total = fields.Float("Total", digits=dp.get_precision('Account'))
    total_tax = fields.Float("Total Itbis", digits=dp.get_precision('Account'))
    final_total = fields.Float("Final", digits=dp.get_precision('Account'))
    final_total_tax = fields.Float("Final Itbis", digits=dp.get_precision('Account'))
    fiscal_total = fields.Float("Fiscal", digits=dp.get_precision('Account'))
    fiscal_total_tax= fields.Float("Fiscal Itbis", digits=dp.get_precision('Account'))
    ncfinal_total = fields.Float("NC final", digits=dp.get_precision('Account'))
    ncfinal_total_tax = fields.Float("NC final Itbis", digits=dp.get_precision('Account'))
    ncfiscal_total = fields.Float("NC fiscal", digits=dp.get_precision('Account'))
    ncfiscal_total_tax = fields.Float("NC fiscal Itbis", digits=dp.get_precision('Account'  ))
