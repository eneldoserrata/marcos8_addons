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

    id_nss = fields.Char("NSS")


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    sequence   = fields.Integer('Sequence', select=True, help="Gives the sequence order when displaying a list of expense lines.")
    rule_const = fields.Boolean()
    tss_type = fields.Selection([
        ('none',u'No aplica para novedades TSS'),
        ('SALARIO_SS',u'Salario cotizable para la Seg. Social'),
        ('APORTE_ORDINARIO',u'Aporte Voluntario Ordinario'),
        ('SALARIO_ISR',u'Salario  cotizable para el ISR'),
        ('OTRAS_REMUNERACIONES',u'Otras remuneraciones'),
        ('REMUNERACIONES_OTROS_EMPLEADORES',u'Remuneración en otros empleadores'),
        ('INGRESOS_EXENTOS_ISR ',u'Ingresos Exentos ISR'),
        ('INFOTEP ',u'Salario  cotizable para el INFOTEP'),
        ('SALDO_A_FAVOR ',u'Saldo a Favor'),
        ('HORAS_EXTRAS ',u'Horas extras'),
    ], string="Campo novedad TSS", default="none")




