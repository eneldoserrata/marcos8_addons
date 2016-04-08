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
import base64

class DgiiSaleReport(models.Model):
    _name = "dgii.sale.report"

    company_id = fields.Many2one("res.company", required=True, default=lambda s: s.env.user.company_id.id, readonly=True, string=u"Comercio", help="Nombre del comerio afiliado a VisaNet")
    PERIODO = fields.Many2one("account.period", required=True)
    CANTIDAD_REGISTROS = fields.Integer("Cantidad de registros", readonly=True)
    TOTAL_MONTO_FACTURADO = fields.Float("Total monto facturado", readonly=True)
    TOTAL_MONTO_ITBIS = fields.Float("Total monto ITBIS", readonly=True)
    report = fields.Binary("Descargar archivo", readonly=True)
    report_name = fields.Char(u"Nombre de Reporte", size=40, readonly=True)
    line_ids = fields.One2many("dgii.sale.report.line", "sale_report_id", readonly=True)


    @api.one
    @api.constrains('company_id', 'PERIODO')
    def company_period_constraing(self):
        envio = self.search([("company_id","=",self.company_id.id),("PERIODO","=",self.PERIODO.id)])
        if len(envio) > 1:
            raise exceptions.Warning("Ya ha generado un reporte 606 para este período, debe buscarlo en la lista!")

    @api.multi
    def generate_file(self):
        invoice_ids = self.env["account.invoice"].search([("company_id","=",self.company_id.id), ("period_id","=",self.PERIODO.id)])
        self.TOTAL_MONTO_FACTURADO = sum([rec.amount_total for rec in invoice_ids])
        self.CANTIDAD_REGISTROS = len([rec.amount_total for rec in invoice_ids])
        self.TOTAL_MONTO_ITBIS = sum([rec.amount_tax for rec in invoice_ids])
        lines = []
        for inv in invoice_ids:
            line = []
            rnc = inv.partner_id.ref
            line.append(inv.partner_id.ref)

            if not rnc:
                line.append("3")
            elif len(rnc) == 9:
                line.append("1")
            elif len(rnc) == 11:
                line.append("2")

            line.append(inv.number)

            if inv.parent_id:
                line.append(inv.parent_id.number)
            else:
                line.append("X")
            line.append(inv.date_invoice)

            if inv.amount_tax:
                line.append(inv.amount_tax)
            else:
                line.append(0)

            if inv.amount_total:
                line.append(inv.amount_total)
            else:
                line.append(0)
            lines.append(line)

        self.line_ids.unlink()
        lines_dict_list = []
        for line in lines:
            lines_dict_list.append([0, False, {"sale_report_id": self.id,
                                               "RNC_CEDULA": line[0],
                                               "TIPO_IDENTIFICACION": line[1],
                                               "NUMERO_COMPROBANTE_FISCAL": line[2],
                                               "NUMERO_COMPROBANTE_MODIFICADO": line[3],
                                               "FECHA_COMPROBANTE": line[4],
                                               "ITBIS_FACTURADO": line[5],
                                               "MONTO_FACTURADO": line[6],
                                               }])

        self.write({"line_ids": lines_dict_list})
        path = '/tmp/606{}.txt'.format(self.company_id.vat)
        f = open(path,'w')
        header_str = ""
        header_str += "607"
        header_str += self.company_id.vat.rjust(11)
        periodo = self.PERIODO.name.split("/")
        header_str += periodo[1]+periodo[0]
        header_str += str(self.CANTIDAD_REGISTROS).zfill(12)
        header_str += ('%.2f' % self.TOTAL_MONTO_FACTURADO).zfill(16)
        f.write(header_str + '\n')

        for line in self.line_ids:
            line_str = ""
            if line.RNC_CEDULA:
                line_str += line.RNC_CEDULA.rjust(11)
            else:
                line_str += "".rjust(11)
            line_str += line.TIPO_IDENTIFICACION
            line_str += line.NUMERO_COMPROBANTE_FISCAL
            line_str += "".rjust(19) if line.NUMERO_COMPROBANTE_MODIFICADO == "X" else line.NUMERO_COMPROBANTE_MODIFICADO
            fecha = line.FECHA_COMPROBANTE.split("-")
            line_str += fecha[0]+fecha[1]+fecha[2]
            line_str += ('%.2f' % line.ITBIS_FACTURADO).zfill(12)
            line_str += ('%.2f' % line.MONTO_FACTURADO).zfill(12)
            f.write(line_str+ '\n')

        f.close()
        f = open(path,'rb')
        report = base64.b64encode(f.read())
        f.close()
        report_name = 'DGII_F_607_' + self.company_id.vat + '_' + periodo[1]+periodo[0] + '.TXT'
        self.write({'report': report, 'report_name': report_name})
        return True






class DgiiSaleReportLine(models.Model):
    _name = "dgii.sale.report.line"

    sale_report_id = fields.Many2one("dgii.sale.report")
    RNC_CEDULA = fields.Char(u"RNC/Cédula", size=11)
    TIPO_IDENTIFICACION = fields.Char(u"Tipo Identificación", size=1)
    NUMERO_COMPROBANTE_FISCAL = fields.Char(u"Nümero comprobante fiscal", size=19)
    NUMERO_COMPROBANTE_MODIFICADO = fields.Char(u"Nümero comprobante modificado", size=19)
    FECHA_COMPROBANTE = fields.Char("Fecha comprobante")
    ITBIS_FACTURADO = fields.Float("ITBIS facturado")
    MONTO_FACTURADO = fields.Float("Monto facturado")
