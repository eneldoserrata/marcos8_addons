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

from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from lxml import etree


class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def print_voucher(self, cr, uid, ids, context=None):
        if not ids:
            raise osv.except_osv(_('Printing error'), _('No a seleccionado nigun recibo para imprimir '))

        data = {
            'id': ids and ids[0],
            'ids': ids,
        }

        return self.pool['report'].get_action(
            cr, uid, [], 'marcos_report.report_voucher', data=data, context=context
        )
