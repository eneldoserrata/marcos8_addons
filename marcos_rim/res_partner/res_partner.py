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

from openerp.osv import osv
from openerp.tools import email_split
from openerp import SUPERUSER_ID

# class res_partner(osv.Model):
#     _inherit = "res.partner"
#
#     @api.model
#     def create(self, vals):

# def extract_email(email):
#     """ extract the email address from a user-friendly email address """
#     addresses = email_split(email)
#     return addresses[0] if addresses else ''
#
#
# class wizard_user(osv.osv_memory):
#     _inherit = 'portal.wizard.user'
#
#     def get_error_messages(self, cr, uid, ids, context=None):
#         res_users = self.pool.get('res.users')
#         emails = []
#         error_empty = []
#         error_emails = []
#         error_user = []
#         ctx = dict(context or {}, active_test=False)
#         for wizard_user in self.browse(cr, SUPERUSER_ID, ids, context):
#             if wizard_user.in_portal and not self._retrieve_user(cr, SUPERUSER_ID, wizard_user, context):
#                 email = extract_email(wizard_user.email)
#                 if not email:
#                     error_empty.append(wizard_user.partner_id)
#                 if email in emails and email not in error_emails:
#                     error_emails.append(wizard_user.partner_id)
#                 user = res_users.search(cr, SUPERUSER_ID, [('login', '=', email)], context=ctx)
#                 if user:
#                     error_user.append(wizard_user.partner_id)
#                 emails.append(email)
#
#         error_msg = []
#         if error_empty:
#             error_msg.append("%s\n- %s" % (_("Some contacts don't have a valid email: "),
#                                 '\n- '.join(['%s' % (p.display_name,) for p in error_empty])))
#         if error_emails:
#             error_msg.append("%s\n- %s" % (_("Several contacts have the same email: "),
#                                 '\n- '.join([p.email for p in error_emails])))
#         if error_user:
#             error_msg.append("%s\n- %s" % (_("Some contacts have the same email as an existing portal user:"),
#                                 '\n- '.join(['%s <%s>' % (p.display_name, p.email) for p in error_user])))
#         if error_msg:
#             error_msg.append(_("To resolve this error, you can: \n"
#                 "- Correct the emails of the relevant contacts\n"
#                 "- Grant access only to contacts with unique emails"))
#         return error_msg