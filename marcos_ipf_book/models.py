# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2015 Marcos Organizador de Negocios SRL http://marcos.do
#    Write by Eneldo Serrata (eneldo@marcos.do)
#
##############################################################################

from openerp import models, fields, api
import base64
import openerp.addons.decimal_precision as dp


class ipf_monthly_book(models.Model):
    _name = "ipf.monthly.book"

    subsidiary = fields.Many2one("shop.ncf.config", string="Sucursal", required=True)
    period_id = fields.Many2one("account.period", string="Periodo", readonly=False, required=True)
    book = fields.Binary("Libro Mensual", readonly=True)
    filename = fields.Char("file name")

    doc_qty = fields.Integer("Transacciones", digits=dp.get_precision('Account'))
    total = fields.Float("Total", digits=dp.get_precision('Account'))
    total_tax = fields.Float("Total Itbis", digits=dp.get_precision('Account'))
    final_total = fields.Float("Final total", digits=dp.get_precision('Account'))
    final_total_tax = fields.Float("Final Itbis total", digits=dp.get_precision('Account'))
    fiscal_total = fields.Float("Fiscal total", digits=dp.get_precision('Account'))
    fiscal_total_tax= fields.Float("Fiscal Itbis total", digits=dp.get_precision('Account'))
    ncfinal_total = fields.Float("NC final total", digits=dp.get_precision('Account'))
    ncfinal_total_tax = fields.Float("NC final Itbis total", digits=dp.get_precision('Account'))
    ncfiscal_total = fields.Float("NC fiscal total", digits=dp.get_precision('Account'))
    ncfiscal_total_tax = fields.Float("NC fiscal Itbis total", digits=dp.get_precision('Account'  ))