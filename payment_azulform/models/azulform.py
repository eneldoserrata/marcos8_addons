# -*- coding: utf-8 -*-
# #############################################################################
#
# Copyright (c) 2014 Marcos Organizador de Negocios- Eneldo Serrata - http://marcos.do
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company like Marcos Organizador de Negocios.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# #############################################################################

try:
    import simplejson as json
except ImportError:
    import json
from openerp.addons.payment.models.payment_acquirer import ValidationError
import logging
import hashlib
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)

from openerp.osv import osv, fields
from openerp.http import request

_logger = logging.getLogger(__name__)

class PaymentAcquirerAzulForm(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_providers(self, cr, uid, context=None):
        providers = super(PaymentAcquirerAzulForm, self)._get_providers(cr, uid, context=context)
        providers.append(['azulform', 'Azul pago via formulario'])
        return providers

    def _get_azulform_urls(self, cr, uid, acquirer, context=None):
        if acquirer.environment == 'prod':
            return {
                'azulform_form_url': acquirer.azulfomr_url_prod
            }
        else:
            return {
                'azulform_form_url': acquirer.azulform_url_test
            }

    def azulform_get_form_action_url(self, cr, uid, id, context=None):
        return '/payment/transfer/azulform'

    _columns = {
        "azulform_azulform_url_test":           fields.char("Azul form Url servicio", required=True, degault="/"),
        "azulform_MerchantId_test":             fields.char("No. de comercio", required=True, degault="/"),
        "azulform_MerchantName_test":           fields.char("Nombre del comercio", required=True, degault="/"),
        "azulform_MerchantType_test":           fields.char("Tipo de comercio", required=True, degault="/"),
        "azulform_CurrencyCode_test":           fields.char("Codigo de moneda", required=True, degault="/"),
        "azulform_ApprovedUrl_test":            fields.char("redirigir al aprobar", required=True, degault="/payment/azulform/accept"),
        "azulform_DeclinedUrl_test":            fields.char("redirigir al declinar", required=True, degault="/shop/payment"),
        "azulform_CancelUrl_test":              fields.char("redirigir al cancelar", required=True, degault="/shop/payment"),
        "azulform_ResponsePostUrl_test":        fields.char("redirigir al completar", required=False),
        "azulform_UseCustomField1_test":        fields.char("Fiand 1 ID", required=True, degault="/"),
        "azulform_CustomField1Label_test":      fields.char("Field 1 label", degault="/"),
        "azulform_CustomField1Value_test":      fields.char("Field 1 value", degault="/"),
        "azulform_UseCustomField2_test":        fields.char("Fiand 2 ID", required=True, degault="/"),
        "azulform_CustomField2Label_test":      fields.char("Field 2 label", degault="/"),
        "azulform_CustomField2Value_test":      fields.char("Field 2 value", degault="/"),
        "azulform_ShowTransactionResult_test":  fields.char("Mostrar resultado de azul", degault="/"),
        "azulform_AuthKey_test":                     fields.char("AuthKey", default="/"),

        "azulform_azulform_url_prod":           fields.char("Azul form Url servicio", required=True, default="/"),
        "azulform_MerchantId_prod":             fields.char("No. de comercio", required=True, default="/"),
        "azulform_MerchantName_prod":           fields.char("Nombre del comercio", required=True, default="/"),
        "azulform_MerchantType_prod":           fields.char("Tipo de comercio", required=True, default="/"),
        "azulform_CurrencyCode_prod":           fields.char("Codigo de moneda", required=True, default="/"),
        "azulform_ApprovedUrl_prod":            fields.char("redirigir al aprobar", required=True, default="/payment/azulform/accept"),
        "azulform_DeclinedUrl_prod":            fields.char("redirigir al declinar", required=True, default="/shop/payment"),
        "azulform_CancelUrl_prod":              fields.char("redirigir al cancelar", required=True, default="/shop/payment"),
        "azulform_ResponsePostUrl_prod":        fields.char("redirigir al completar", required=False),
        "azulform_UseCustomField1_prod":        fields.char("Fiand 1 ID", required=True, default="0"),
        "azulform_CustomField1Label_prod":      fields.char("Field 1 label"),
        "azulform_CustomField1Value_prod":      fields.char("Field 1 value"),
        "azulform_UseCustomField2_prod":        fields.char("Fiand 2 ID", required=True, default="0"),
        "azulform_CustomField2Label_prod":      fields.char("Field 2 label", default="/"),
        "azulform_CustomField2Value_prod":      fields.char("Field 2 value", default="/"),
        "azulform_ShowTransactionResult_prod":  fields.char("Mostrar resultado de azul", default="0"),
        "azulform_AuthKey_prod":                     fields.char("AuthKey", required=True, default="0"),

    }

    def _azulform_generate_shasign(self, values, key):
        concat = ""
        concat += values["MerchantId"]
        concat += values["MerchantName"]
        concat += values["MerchantType"]
        concat += values["CurrencyCode"]
        concat += values["OrderNumber"]
        concat += values["Amount"]
        concat += values["ITBIS"]
        concat += values["ApprovedUrl"]
        concat += values["DeclinedUrl"]
        concat += values["CancelUrl"]
        concat += values["ResponsePostUrl"] or ""
        concat += values["UseCustomField1"]
        concat += values["CustomField1Label"] or ""
        concat += values["CustomField1Value"] or ""
        concat += values["UseCustomField2"]
        concat += values["CustomField2Label"] or ""
        concat += values["CustomField2Value"] or ""
        concat += key  or ""

        return hashlib.sha512(concat).hexdigest()

    def azulform_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        azul_tx_values = dict(tx_values)
        order_id = self.pool.get("sale.order").search(cr, uid, [("name", "=", tx_values["reference"])], context=context)
        order = self.pool.get("sale.order").browse(cr, uid, order_id, context=context)

        amount = '%.2f' % azul_tx_values["amount"]
        itbis = '%.2f' % order.amount_tax
        amount = amount.replace(".","")
        itbis = itbis.replace(".","")

        temp_azul_tx_values = {
            "azulform_url": acquirer.azulform_azulform_url_test if acquirer.environment == "test" else acquirer.azulform_azulform_url_prod,
            "MerchantId": acquirer.azulform_MerchantId_test if acquirer.environment == "test" else acquirer.azulform_MerchantId_prod,
            "MerchantName": acquirer.azulform_MerchantName_test if acquirer.environment == "test" else acquirer.azulform_MerchantName_prod,
            "MerchantType": acquirer.azulform_MerchantType_test if acquirer.environment == "test" else acquirer.azulform_MerchantType_prod,
            "CurrencyCode": acquirer.azulform_CurrencyCode_test if acquirer.environment == "test" else acquirer.azulform_CurrencyCode_prod,
            "OrderNumber": azul_tx_values["reference"],
            "Amount": amount,
            "ITBIS": itbis,
            "ApprovedUrl": acquirer.azulform_ApprovedUrl_test if acquirer.environment == "test" else acquirer.azulform_ApprovedUrl_prod,
            "DeclinedUrl": acquirer.azulform_DeclinedUrl_test if acquirer.environment == "test" else acquirer.azulform_DeclinedUrl_prod,
            "CancelUrl": acquirer.azulform_CancelUrl_test if acquirer.environment == "test" else acquirer.azulform_CancelUrl_prod,
            "ResponsePostUrl": acquirer.azulform_ResponsePostUrl_test if acquirer.environment == "test" else acquirer.azulform_ResponsePostUrl_prod,
            "UseCustomField1": acquirer.azulform_UseCustomField1_test if acquirer.environment == "test" else acquirer.azulform_UseCustomField1_prod,
            "CustomField1Label": acquirer.azulform_CustomField1Label_test if acquirer.environment == "test" else acquirer.azulform_CustomField1Label_prod,
            "CustomField1Value": acquirer.azulform_CustomField1Value_test if acquirer.environment == "test" else acquirer.azulform_CustomField1Value_prod,
            "UseCustomField2": acquirer.azulform_UseCustomField2_test if acquirer.environment == "test" else acquirer.azulform_UseCustomField2_prod,
            "CustomField2Label": acquirer.azulform_CustomField2Label_test if acquirer.environment == "test" else acquirer.azulform_CustomField2Label_prod,
            "CustomField2Value": acquirer.azulform_CustomField2Value_test if acquirer.environment == "test" else acquirer.azulform_CustomField2Value_prod,
            "ShowTransactionResult": acquirer.azulform_ShowTransactionResult_test if acquirer.environment == "test" else acquirer.azulform_ShowTransactionResult_prod
        }
        azul_tx_values.update(temp_azul_tx_values)

        AuthKey = acquirer.azulform_AuthKey_test if acquirer.environment == "test" else acquirer.azulform_AuthKey_prod
        shasign = self._azulform_generate_shasign(azul_tx_values, AuthKey)

        azul_tx_values.update({"AuthHash": shasign,
                               "reference": azul_tx_values["reference"],
                               "currency": azul_tx_values["currency"],
                               "return_url": "/shop/confirmation"
                               })
        return partner_values, azul_tx_values


class TransferPaymentTransaction(osv.Model):
    _inherit = 'payment.transaction'

    def _azulform_form_get_tx_from_data(self, cr, uid, data, context=None):
        reference, pay_id, shasign = data.get('OrderNumber', False), data.get('AuthorizationCode', False), data.get('AuthHash', False)

        tx_ids = self.search(cr, uid, [('reference', '=', reference)], context=context)

        vals = {
            "azulform_authorizationcode": data.get("AuthorizationCode", False),
            "azulform_datetime": data.get("DateTime", False),
            "azulform_responsecode": data.get("ResponseCode", False),
            "azulform_isocode": data.get("IsoCode", False),
            "azulform_rrn": data.get("RRN", False),
            "state": "done"
        }
        self.write(cr, uid, tx_ids[0], vals, context=context)

        return self.browse(cr, uid, tx_ids[0], context=context)


    _columns = {
        'azulform_authorizationcode': fields.char(u'Código de autorización', size=10),
        'azulform_datetime': fields.char(u'Fecha y hora', size=10),
        'azulform_responsecode': fields.char(u'Código de respuesta', size=10),
        'azulform_isocode': fields.char(u'isoCode de Respuesta', size=10),
        'azulform_rrn': fields.char(u'Número de referencia', size=10)
    }



