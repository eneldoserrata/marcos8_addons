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
import logging

import werkzeug
from openerp import http
from openerp.osv import orm
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale, QueryURL, table_compute
from openerp.addons.website.models.website import slug
import json
import urlparse
_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class RimControl(http.Controller):
    @http.route(['/qc/'], type='http', auth='public')
    def qc(self, debug=False, **k):
        if not request.session.uid:
            return http.local_redirect('/web/login?redirect=/qc')
        return request.render('marcos_rim.rimqc')

    @http.route(['/transfer/'], type='http', auth='user')
    def int_transfer(self, debug=False, **k):
        if not request.session.uid:
            return http.local_redirect('/web/login?redirect=/transfer')

        return request.render('marcos_rim.locationmovewidget')

    @http.route(['/salepicking/'], type='http', auth='user')
    def sale_picking(self, debug=False, **k):
        if not request.session.uid:
            return http.local_redirect('/web/login?redirect=/salepicking')

        return request.render('marcos_rim.salepickingwidget')

    # @http.route(['/gpl/'], type='http', auth='public')
    # def sale_picking(self, debug=False, **k):
    #
    #     cr, uid, context, pool = request.cr, 1, request.context, request.registry
    #     template_obj = pool['product.template']
    #     product_ids = template_obj.search(cr, uid, [('qty_available','>',0)], context=context)
    #     products = template_obj.browse(cr, uid, product_ids, context=context)
    #
    #     price_list = {}
    #     prod = [prod for prod in products]
    #     for product in prod:
    #         if not price_list.get(product.name[-3:], False):
    #             if len(product.name) == 18:
    #                 price_list[product.name[-3:]] = {}
    #
    #
    #
    #
    #     rins = sorted([r[0] for r in price_list.iteritems()])
    #     rins_menu = [{"caption":r, "href":"#"+r} for r in rins]
    #
    #     for rin in rins:
    #         for product in prod:
    #             if len(product.name) == 18:
    #                 if not price_list[rin].get(product.name[8:-4], False) and rin == product.name[-3:]:
    #                     price_list[rin][product.name[8:-4]] = {}
    #
    #     for product in prod:
    #         if len(product.name) == 18:
    #                 try:
    #                     price_list[product.name[-3:]][product.name[8:-4]][product.name[6:-11]] = {"price": product.list_price, "qty": product.qty_available}
    #                 except:
    #                     print "noooooooo {}".format(product.name)
    #
    #     table_body = ""
    #     for rin in sorted(price_list.iteritems()):
    #         table_body += """
    #             <table class="tg table table-striped table-bordered table-hover" id="{}">
    #                 <tr>
    #                     <th class="tg-031e" colspan="3" rowspan="2">Sizes</th>
    #                     <th class="tg-031e" colspan="8">Price and QTY by Quality</th>
    #                 </tr>
    #                 <tr>
    #                     <td class="tg-031e" style="text-align: center;">A</td>
    #                     <td class="tg-031e" style="text-align: center;">QTY</td>
    #                     <td class="tg-031e" style="text-align: center;">B</td>
    #                     <td class="tg-031e" style="text-align: center;">QTY</td>
    #                     <td class="tg-031e" style="text-align: center;">C</td>
    #                     <td class="tg-031e" style="text-align: center;">QTY</td>
    #                     <td class="tg-031e" style="text-align: center;">T</td>
    #                     <td class="tg-031e" style="text-align: center;">QTY</td>
    #                 </tr>
    #
    #                 """.format(rin[0])
    #
    #
    #         for serie in rin[1].iteritems():
    #             rserie = serie[0]+"-"+rin[0]
    #
    #             if serie[1].get("A", False):
    #                 pricea = serie[1]["A"].get("price", 0)
    #                 qtya = int(serie[1]["A"].get("qty", 0))
    #             else:
    #                 pricea = 0
    #                 qtya = 0
    #
    #             if serie[1].get("B", False):
    #                 priceb = serie[1]["B"].get("price", 0)
    #                 qtyb = int(serie[1]["B"].get("qty", 0))
    #             else:
    #                 priceb = 0
    #                 qtyb = 0
    #
    #
    #             if serie[1].get("C", False):
    #                 pricec = serie[1]["C"].get("price", 0)
    #                 qtyc = int(serie[1]["C"].get("qty", 0))
    #             else:
    #                 pricec = 0
    #                 qtyc = 0
    #
    #             if serie[1].get("T", False):
    #                 pricet = serie[1]["T"].get("price", 0)
    #                 qtyt = int(serie[1]["T"].get("qty", 0))
    #             else:
    #                 pricet = 0
    #                 qtyt = 0
    #
    #             table_body += """
    #                 <tr>
    #                     <td class="tg-031e" colspan="3"  style="text-align: center;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                     <td class="tg-031e" style="text-align: right;">{}</td>
    #                 </tr>
    #
    #             """.format(rserie, pricea, qtya, priceb, qtyb, pricec, qtyc, pricet, qtyt)
    #
    #         table_body += """
    #         </table>
    #         """
    #     res = request.render('marcos_rim.GabrielReport', {"table_body": table_body, "top_menu_link": rins_menu})
    #     return res


class website_sale(website_sale):
    @http.route(['/shop',
                 '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 '/shop/category/<model("product.public.category"):category>/page/<int:page>'
                ], type='http', auth="user", website=True)
    def shop(self, page=0, category=None, search='', **post):

        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        domain = request.website.sale_product_domain()
        if search.startswith("sku"):

            search_list = search.split("-")
            grado = search_list[1] if not search_list[1] == "all" else "-"
            ancho = search_list[2] if not search_list[2] == "all" else "-"
            alto = search_list[3] if not search_list[3] == "all" else "-"
            aro = search_list[4] if not search_list[4] == "all" else ""
            cantidad = search_list[5]
            clasification = search_list[6]

            select_search = "{}%{}%{}%{}".format(grado, ancho, alto, aro)

            if "qty0510" in cantidad:
                domain += ['&', '&', ("qty_available", ">=", 5), ("qty_available", "<=", 10)]
            elif "qty1025" in cantidad:
                domain += ['&', '&', ("qty_available", ">=", 10), ("qty_available", "<=", 25)]
            elif "qty2550" in cantidad:
                domain += ['&', '&', ("qty_available", ">=", 25), ("qty_available", "<=", 50)]
            elif "qty5000" in cantidad:
                domain += ['&', ("qty_available", ">", 50)]

            if "clap" in clasification:
                domain += [('clasification', '=', "p")]
            elif "clag" in clasification:
                domain += [('clasification', '=', "g")]
            elif "clas" in clasification:
                domain += [('clasification', '=', "s")]
            elif "clab" in clasification:
                domain += [('clasification', '=', "b")]

            if select_search:
                domain += ['|', '|', '|', ('name', 'ilike', select_search), ('description', 'ilike', select_search),
                           ('description_sale', 'ilike', select_search), ('product_variant_ids.default_code', 'ilike', select_search)]
            if category:
                domain += [('public_categ_ids', 'child_of', int(category))]

        else:
            if search:
                domain += ['|', '|', '|', ('name', 'ilike', search), ('description', 'ilike', search),
                           ('description_sale', 'ilike', search), ('product_variant_ids.default_code', 'ilike', search)]
            if category:
                domain += [('public_categ_ids', 'child_of', int(category))]

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"
        product_count = product_obj.search_count(cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)
        pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'],
                                         order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [], context=context)
        categories = category_obj.browse(cr, uid, category_ids, context=context)
        categs = filter(lambda x: not x.parent_id, categories)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price,
                                                                       context=context)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute().process(products),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
        }
        return request.website.render("website_sale.products", values)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        if search.startswith("sku"):

            search_list = search.split("-")
            grado = search_list[1] if not search_list[1] == "all" else "-"
            ancho = search_list[2] if not search_list[2] == "all" else "-"
            alto = search_list[3] if not search_list[3] == "all" else "-"
            aro = search_list[4] if not search_list[4] == "all" else ""

            search = "{}%{}%{}%{}".format(grado, ancho, alto, aro)

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(cr, uid, int(category), context=context)

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [], context=context)
        category_list = category_obj.name_get(cr, uid, category_ids, context=context)
        category_list = sorted(category_list, key=lambda category: category[1])

        pricelist = self.get_pricelist()

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price,
                                                                       context=context)

        product_tmpl_id = pool["product.product"].search(cr, uid, [("product_tmpl_id", "=", int(product))])
        product_quant_ids = pool['stock.quant'].search(cr, uid, [("product_id", "=", product_tmpl_id),
                                                                 ("location_id.usage", "=", u"internal")],
                                                       order="location_id", context=context)
        quants = pool['stock.quant'].browse(cr, uid, product_quant_ids, context=context)

        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(cr, uid, int(product), context=context)

        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'category_list': category_list,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            "quants": quants
        }

        return request.website.render("website_sale.product", values)

    @http.route(['/shop/tracking_last_order'], type='json', auth="public")
    def tracking_cart(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        res = super(website_sale, self).tracking_cart(**post)

        sale_order_id = request.session.get('sale_last_order_id')
        order = request.registry['sale.order'].browse(cr, 1, sale_order_id, context=context)

        for line in order.order_line:
            if line.name.startswith("U-PLT") or line.name.startswith("PLT"):
                for locationlist in line.get_inventory_location(line.product_id.id, context=context):
                    line.name += '\n{}'.format(' '.join(locationlist))
        return res