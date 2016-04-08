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
from openerp.addons.survey.controllers.main import WebsiteSurvey
from openerp.addons.web import http
import json
from openerp.addons.web.http import request
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


tipo_ncf = {
    u"220": u"Para Consumidor Final",
    u"221": u"Para Crédito Fiscal ",
    u"222": u"Gubernamental",
    u"223": u"Regímenes especiales"
}

venden = {
    u"224": u"0 – 250",
    u"225": u"250 – 750",
    u"226": u"750 – 1500",
    u"227": u"1500 +"
}

tipos_ventas ={
    u"228": u"Por Mayor",
    u"229": u"Detalle"
}

tipos_distribuyen = {
    u"230": u"Pasajeros",
    u"231": u"Camión",
    u"232": u"OTR",
    u"233": u"Neumaticos para Agricultura"
}


class WebsiteSurvey(WebsiteSurvey):

    @http.route(['/survey/submit/<model("survey.survey"):survey>'],
                type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        result = super(WebsiteSurvey, self).submit(survey, **post)
        if "error" in result.get_data():
            return result
        elif survey.id == 6 and "redirect" in result.get_data():
            cr, uid, context = request.cr, request.uid, request.context
            res_partner_obj = request.registry['res.partner']

            if post.get("6_13_81", False) != "220":
                dgii_result = res_partner_obj.get_rnc(post.get("6_13_80", False))
                if dgii_result:
                    name = dgii_result["name"]
                    ref = dgii_result["rnc"]
                    iscompany = True
                    if post.get("6_13_81", False) == "221":
                        property_account_position = 1
                    elif post.get("6_13_81", False) == "222":
                        property_account_position = 3
                    elif post.get("6_13_81", False) == "223":
                        property_account_position = 4
                else:
                    return result.set_data({"errors": {"6_13_80": u"Para facturar con valor fiscal debe ingresar una identificación válida."}})
            else:
                name = post.get("6_13_78", "")+" / "+ post.get("6_13_79", "")
                ref = False
                iscompany = False
                property_account_position = 2

            partner_values = {'property_account_position': property_account_position,
                              'notify_email': 'always',
                              # 'message_follower_ids': [101,104,3],
                              'active': True,
                              'street': post.get("6_13_85", False),
                              'property_stock_customer': 9,
                              'property_product_pricelist': 1,
                              'property_account_receivable': 82,
                              'country_id': 62,
                              'company_id': 1,
                              'property_account_payable': 141,
                              'type': 'contact',
                              'email': post.get("6_13_84", False),
                              'is_company': iscompany,
                              'ref': ref,
                              'lang': 'es_DO',
                              'street2': 'Calle2',
                              'phone': post.get("6_13_83", False),
                              'credit_limit': 0,
                              'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                              'customer': True,
                              'property_stock_supplier': 8,
                              'name': name,
                              'property_product_pricelist_purchase': 3,
                              'mobile': post.get("6_13_82", False),
                              "user_id": 1}

            tipo_de_factura =           post.get("6_13_81", "")
            Tipos_de_ventas =           post.get("6_13_87", "")
            venden_cada_mes =           post.get("6_13_86", "")
            venden_cada_mes_coment =    post.get("6_13_86_comment", "")
            distribuyen =               post.get("6_13_88", "")
            comment = u"Tipo de factura \n"
            comment += tipo_ncf[tipo_de_factura]+" \n"
            comment += u"Tipos de ventas?/n"
            comment += tipos_ventas[Tipos_de_ventas]+" \n"
            comment += u"Cuantos neumáticos venden cada mes? \n"
            comment += venden[venden_cada_mes]+u"\n"
            comment += venden_cada_mes_coment+"\n"
            comment += u"Tipos de neumaticos que distribuyen? \n"
            comment += tipos_distribuyen[distribuyen]+" \n"
            partner_values.update({"comment": comment})
            new_partner = res_partner_obj.create(cr, 1, partner_values, context=context)
            return result
        else:
            return result


