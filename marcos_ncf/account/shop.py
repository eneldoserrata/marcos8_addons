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
from openerp.exceptions import ValidationError


class InvoiceJournalConfig(models.Model):
    _name = "shop.ncf.config"

    name = fields.Char("Sucursal", size=40, required=False)
    final = fields.Many2one("account.journal", "Consumidor final", required=False)
    fiscal = fields.Many2one("account.journal", u"Para crédito fiscal", required=False)
    special = fields.Many2one("account.journal", u"Regímes especiales", required=False)
    gov = fields.Many2one("account.journal", "Gubernalmentales", required=False)
    nc = fields.Many2one("account.journal", u"Notas de crédito", required=False)
    nd = fields.Many2one("account.journal", u"Notas de débito", required=False)
    default_warehouse = fields.Many2one("stock.warehouse", u"Almacén predeterminado")

    """
    This method return de default shop ncf config for the user

    TODO: create correct demo data because when isntall with demo data get exception because
    the new field shop_ncf_config_id not include an get exception this is the reason i place
    try inthis exception
    """

    @api.v8
    @api.multi
    def get_default(self):
        try:
            resp = False
            if self.env.user.shop_ncf_config_id.id:
                resp = self.env.user.shop_ncf_config_id.id
            elif self.search_count([]) > 0:
                resp = self.search([])[0].id

            if not resp:
                raise ValidationError(
                    u"Se debe realizar la configuración de los comprobantes fiscales antes de realizar una factura!")
            else:
                return resp
        except:
            return False
