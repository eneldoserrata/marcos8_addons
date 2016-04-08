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
from openerp import models, api, fields
from openerp.exceptions import except_orm, Warning, RedirectWarning


class marcos_sale_discount(models.TransientModel):
    _name = "marcos.sale.discount"

    discount = fields.Float("Descuento")

    @api.one
    def apply_discount(self):

        if len(self.env.context.get("active_ids", False)) > 1:
            raise except_orm('Accion invalida!',
                'Solo puede aplicar descuentos globales a un documento a la vez!.')

        active_model = self.env.context.get("active_model", False)
        model = self.env[active_model].browse(self.env.context["active_id"])
        if active_model == "account.invoice":
            if model.state != "draft":
                raise except_orm('Accion invalida!',
                'Solo puede aplicar descuentos globales si el documento no esta en borrador!.')
            for line in model.invoice_line:
                line.write({"discount": self.discount})
            model.button_reset_taxes()
        elif active_model == "sale.order":
            if model.state != "draft":
                raise except_orm('Accion invalida!',
                    'Solo puede aplicar descuentos globales si el documento no esta en borrador!.')

            for line in model.order_line:
                line.write({"discount": self.discount})



