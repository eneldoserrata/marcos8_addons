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

from openerp import models, api
import datetime

class account_period(models.Model):
    _inherit = "account.period"

    @api.model
    def find(self, dt=None):
        context = self._context
        if not dt:
            dt = datetime.datetime.today().strftime(D_FMT)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]

        company_id = context.get('company_id', False) or self.env.user.company_id.id
        args.append(('company_id', '=', company_id))
        result = []
        if context.get('account_period_prefer_normal', True):
            # look for non-special periods first, and fallback to all if no result is found
            result = self.search(args + [('special', '=', False)])
        if not result:
            result = self.search(args)
        if not result:
            year = dt.split("-")[0]
            date_start = "{}-01-01".format(year)
            date_stop = "{}-12-31".format(year)

            fiscal_year = self.env["account.fiscalyear"].sudo().create({"name": year,"code": year,"company_id": company_id,"date_start": date_start,"date_stop": date_stop})

            fiscal_year.sudo().create_period()

        if context.get('account_period_prefer_normal', True):
            # look for non-special periods first, and fallback to all if no result is found
            result = self.search(args + [('special', '=', False)])
        if not result:
            result = self.search(args)

        return result
