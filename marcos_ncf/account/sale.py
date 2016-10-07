# -*- coding: utf-8 -*-

from openerp import models,api


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.v7
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res = super(SaleOrder, self)._prepare_invoice(cr, uid, order, lines, context=context)
        partner_id = res.get("partner_id", False)
        if partner_id:
            partner_id = self.pool.get("res.partner").browse(cr, uid, partner_id)
            customer_property_account_position = partner_id.customer_property_account_position
            if customer_property_account_position:
                customer_property_account_position = customer_property_account_position.id
            else:
                customer_property_account_position = 2
            res.update({"fiscal_position": customer_property_account_position})
        return res
