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


import re
import time
import requests
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import exceptions

CURRENCY_DISPLAY_PATTERN = re.compile(r'(\w+)\s*(?:\((.*)\))?')


class res_currency(osv.osv):
    _inherit = "res.currency"

    def _get_central_bank_rate(self):
        res = requests.get("http://api.marcos.do/central_bank_rates")
        if res.status_code == 200:
            return res.json()
        else:
            return False

    def get_rate_usd(self, cr, uid, ids, context=None):
        rate_of_the_day = self._get_central_bank_rate()
        if not rate_of_the_day["dollar"].get("selling_rate", False):
            raise exceptions.Warning("No se pudo obtener la taza del banco central debe actualizarla de forma manual");

        if rate_of_the_day:
            rate_Factor = 1.0/float(rate_of_the_day["dollar"]["selling_rate"])
            vals = {"name": time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    "rate": rate_Factor,
                    "currency_id": ids[0]}
            new_rate = self.pool.get("res.currency.rate").create(cr, uid, vals, context=context)
            return new_rate
        else:
            pass


class res_currency_rate(osv.osv):
    _inherit = "res.currency.rate"

    _columns = {
        'rate': fields.float('Rate', digits=(12, 14), help='The rate of the currency to the currency of rate 1')
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
