# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import timedelta, datetime

class product_pricelist_version(models.Model):
    _inherit = "product.pricelist.version"

    rate = fields.Float(string="Tasa", digits=(16,4))

class res_currency(models.Model):
    _inherit = "res.currency"

    def is_in_range(self, d, min=False, max=False):
        if max:
            return min <= d <= max
        return min <= d


    @api.v7
    def _get_current_rate(self, cr, uid, ids, raise_on_no_rate=True, context=None):
        #TODO SET ORIGIN IN CONTEXT TO GET PRICELIST RATE FROM ORIGIN

        res = super(res_currency, self)._get_current_rate(cr, uid, ids, raise_on_no_rate=raise_on_no_rate, context=context)
        context = context or {}
        if context.get("pricelist", False):
            price_list = self.pool.get("product.pricelist").browse(cr, uid, context["pricelist"])
            for version in price_list.version_id:
                if version.rate > 0:
                    if version.date_start:
                        date_start = datetime.strptime(version.date_start, "%Y-%m-%d").date()
                        date_end = datetime.strptime(version.date_start, "%Y-%m-%d").date()
                        current_date = datetime.strptime(context["date"].split(" ")[0], "%Y-%m-%d").date()

                        if self.is_in_range(current_date, date_start, date_end):
                            res[ids[1]] = 1/version.rate
                            break

                    else:
                        res[ids[1]] = 1/version.rate

        return res