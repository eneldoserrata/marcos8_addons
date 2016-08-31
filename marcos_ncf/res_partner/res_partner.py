# -*- coding: utf-8 -*-
########################################################################################################################
#  Copyright (c) 2015 - Marcos Organizador de Negocios SRL. (<https://marcos.do/>) #  Write by Eneldo Serrata (eneldo@marcos.do)
#  See LICENSE file for full copyright and licensing details.
#
# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used
# (nobody can redistribute (or sell) your module once they have bought it, unless you gave them your consent)
# if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
########################################################################################################################
from ..tools import is_identification, _internet_on
import requests
from openerp import models, api, exceptions, fields
import re

import logging


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_method = fields.Selection([('manual', 'Basada en las líneas de pedidos de compra'),
                                        ('order', 'Basada en las facturas borrador generadas'),
                                        ('picking', 'Basada en recepciones')],
                                       'Invoicing Control',
                                       help=u"""
                                                    Sobre la base de las líneas de orden de compra: Lugar de líneas\n
                                                    individuales en 'Factura De control> Basado en p.o. líneas "desde\n
                                                    donde se puede selectiva crear y factura. Sobre la base de la factura\n
                                                    generada: crear un proyecto de facturar puede validar más tarde. Bases\n
                                                    de los envíos entrantes: permiten crear una factura cuando se validan\n
                                                    recepciones.
                                                    """
                                       )
    # multiple_company_rnc = fields.Boolean(u"RNC para varias compañias",
    #                                        help=u"Esto permite poder utilizar el RNC en varios registros de compañias"),
    ref_type = fields.Selection([("cedula", u"Cédula"),
                                  ("rnc", u"RNC"),
                                  ("pasport", u"Pasaporte"),
                                  ("none", u"Otros"),
                                  ], string=u"Tipo de identificación", required=True, default="cedula")

    customer_property_account_position = fields.Many2one('account.fiscal.position',
        string=u"Posición fiscal de cliente", company_dependent=False, default=2,
        help="La posición fiscal determinará los impuestos y las cuentas utilizadas para los clientes.",
    )

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(ResPartner, self).name_search(name, args=args, operator=operator, limit=100)
        if not res and name:
            if len(name) in (9,11):
                partners = self.search([('ref','=',name)])
            else:
                partners = self.search([('ref','ilike',name)])

            if partners:
                res = partners.name_get()
        return res

    @api.model
    def ref_is_unique(self, fiscal_id):
        partner = self.search([('ref', '=', fiscal_id)])
        if partner:
            raise exceptions.UserError(u"Ya fue registrada una empresa con este numero de RNC/Cédula")
        return False

    def get_rnc(self, fiscal_id):
        res = requests.get('http://api.marcos.do/rnc/%s' % fiscal_id)
        if res.status_code == 200:
            return res.json()
        else:
            return False

    def validate_fiscal_id(self, fiscal_id):
        vals = {}

        if not len(fiscal_id) in [9, 11]:
            raise exceptions.ValidationError(u"Debe colocar un numero de RNC/Cedula valido!")
        else:
            if _internet_on():
                data = self.get_rnc(fiscal_id)
                if data:
                    vals['ref'] = data['rnc'].strip()
                    vals['name'] = data['name'].strip()
                    vals["comment"] = u"Nombre Comercial: {}, regimen de pago: {},  estatus: {}, categoria: {}".format(
                        data['comercial_name'], data['payment_regimen'], data['status'], data['category'])
                    vals.update({"company_type": "company"})
                    if len(fiscal_id) == 9:
                        vals.update({"company_type": "company"})
                    else:
                        vals.update({"company_type": "person"})
        return vals

    @api.model
    def check_vals(self, vals):
        if self._context.get("install_mode", False):
            return super(ResPartner, self).check_vals(vals)
        if isinstance(vals, unicode):
            vals = {"ref": vals}

        if vals:
            ref_or_name = vals.get("ref", False) or vals.get("name", False)

            ref_type = vals.get("ref_type", False) or self.ref_type
            ref_or_name = re.sub("[^0-9]", "", ref_or_name.strip())

            if ref_type == "cedula" and not len(ref_or_name) == 11:
                raise exceptions.ValidationError(u"Una cédula valida solo debe tener 11 digitos.")
            if ref_type == "rnc" and not len(ref_or_name) == 9:
                raise exceptions.ValidationError(u"Un RNC valido solo debe tener 9 digitos.")

            if ref_type in ("pasport", "none"):
                return vals

            if ref_or_name:
                if ref_or_name.isdigit():
                    fiscal_id = ref_or_name.strip()
                    vals = self.validate_fiscal_id(fiscal_id)
        return vals

    @api.model
    def create(self, vals):
        if self._context.get("install_mode", False) or self._context.get("alias_model_name", False) == "res.users":
            return super(ResPartner, self).create(vals)
        elif vals:
            validation = self.check_vals(vals)
            if validation:
                vals.update(validation)
            else:
                raise exceptions.UserError(u"El número de RNC/Cédula no es vEalido en la DGII.")
            return super(ResPartner, self).create(vals)

    @api.onchange("ref")
    def onchange_ref(self):
        if self.ref and not self._context.get("install_mode", False):
            if self.env["account.invoice"].search_count([('partner_id', '=', self.id)]):
                raise exceptions.UserError("No puede cambiar el RNC/Cédula ya que este cliente o proveedor tiene facturas.")
            self.check_vals(self.ref)

    @api.model
    def name_create(self, name):
        if self._context.get("install_mode", False):
            return super(ResPartner, self).name_create(name)
        if self._rec_name:
            if name.isdigit():
                partner = self.search([('ref', '=', name)])
                if partner or not len(name) in [9, 11] or not self.get_rnc(name):
                    return (0,"")
            record = self.create({self._rec_name: name})
            return record.name_get()[0]
        else:
            _logger.warning("Cannot execute name_create, no _rec_name defined on %s", self._name)
            return False
