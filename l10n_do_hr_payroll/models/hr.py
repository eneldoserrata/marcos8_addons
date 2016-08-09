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

from openerp import models, fields, api


class NewModule(models.Model):
    _inherit = 'hr.employee'

    def _get_nomina(self):
        selecction = []
        for i in range(1,20):
            selecction.append((1, "Nomina {}".format(i)))

        return selecction

    NUMERO_NOMINA = fields.Selection(_get_nomina, string=u"ID Nómina", default=1, required=True)
    TIPO_DE_DOCUMENTO = fields.Selection([('C',u'Cédula'),('N','NSS'),('P','Pasaporte')], required=True, string=u"Tipo de Documento", default="C")
    NUMERO_DE_DOCUMENTO = fields.Char(string=u"Número de documento", help="Indique el numero del tipo de documento.")


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    rule_const = fields.Boolean(help="This si tru only for contant values rules")




