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

from openerp.osv import osv, fields


class account_move(osv.osv):
    _inherit = "account.move"

    def account_assert_balanced(self, cr, uid, context=None):
        return True
        cr.execute("""\
            SELECT      move_id
            FROM        account_move_line
            WHERE       state = 'valid'
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) > 0.00001
            """)
        assert len(cr.fetchall()) == 0, \
            "For all Journal Items, the state is valid implies that the sum " \
            "of credits equals the sum of debits"
        return True
