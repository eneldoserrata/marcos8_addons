# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Open Business Solutions (<http://www.obsdr.com>)
#    Author: Naresh Soni
#    Copyright 2015 Cozy Business Solutions Pvt.Ltd(<http://www.cozybizs.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp import models, api


class PrintCheck(models.AbstractModel):
    _name = 'report.l10n_do_check_printing.check_one'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_do_check_printing.check_one')

        payment_ids = self.env[report.model].browse(self._ids)
        payments = []
        for payment in payment_ids:
            year, month, day = payment.date.split("-")
            payment.report_date = "{} {} {} {} {} {} {} {}".format(day[0],day[1],month[0],month[1],year[0],year[1],
                                                                   year[2], year[3])
            payments.append(payment)

        docargs = {
            "doc_ids": self._ids,
            "doc_model": report.model,
            "docs": payments
        }
        return report_obj.render('l10n_do_check_printing.check_one', docargs)


