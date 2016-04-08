# -*- coding: utf-8 -*-

from api import source_data, destination_data, destination_api, source_api
from sql import PRODUCT_CATEGORY_SELECT, PRODUCT_CATEGORY_INSERT, PRODUCT_IR_PROPERTY_INSERT, PRODUCT_PRODUCT_INSERT, \
    PRODUCT_PRODUCT_SELECT, PRODUCT_TEMPLATE_INSERT, PRODUCT_TEMPLATE_SELECT


# source_cur = source_data.cursor()
# destination_cur = destination_data.cursor()
#
# source_cur.execute(PRODUCT_CATEGORY_SELECT)
# categories = source_cur.fetchall()
#
# destination_cur.execute("DELETE FROM product_template where id > 1")
# destination_cur.execute("DELETE FROM product_product where id > 1")
# destination_cur.execute("DELETE FROM product_category where id > 2")
# destination_cur.execute("DELETE FROM ir_property where res_id like 'product.template,%'")
# destination_data.commit()
#
# for category in categories:
#     destination_cur.execute(PRODUCT_CATEGORY_INSERT, category)
#
# destination_data.commit()
#
# count = 0
# for category in categories:
#     parent_id = False
#     if category["parent_id"]:
#         parent_id = category["parent_id"]
#
#     scat = source_api.browse("product.category", category["id"], context={"lang": "es_DO"})
#     destination_api.write("product.category", category["id"], {"property_stock_account_input_categ": 179,
#                                                                "property_stock_valuation_account_id": 87,
#                                                                "property_stock_account_output_categ": 184,
#                                                                "parent_id": parent_id,
#                                                                "name": scat.name})
#     count += 1
#     print count
#
#
# source_cur.execute(PRODUCT_TEMPLATE_SELECT)
# products = source_cur.fetchall()
#
# count = 1
# products_ids = []
# for prod in products:
#     products_ids.append(prod["id"])
#     destination_cur.execute(PRODUCT_TEMPLATE_INSERT, prod)
#     count += 1
#     print count
#
# destination_data.commit()
#
# source_cur.execute(PRODUCT_PRODUCT_SELECT)
# products = source_cur.fetchall()
#
# for prod in products:
#     destination_cur.execute(PRODUCT_PRODUCT_INSERT, prod)
#     count += 1
#     print count
#
# for id in products_ids:
#     sql = """INSERT INTO "ir_property"
#             (
#                         "id",
#                         "value_text",
#                         "name",
#                         "type",
#                         "company_id",
#                         "fields_id",
#                         "res_id",
#                         "create_uid",
#                         "write_uid",
#                         "create_date",
#                         "write_date"
#             )
#             VALUES
#             (
#                         Nextval('ir_property_id_seq'),
#                         'real_time',
#                         'valuation',
#                         'selection',
#                         1,
#                         4160,
#                         %(product_template)s,
#                         1,
#                         1,
#                         (Now() at time zone 'UTC'),
#                         (Now() at time zone 'UTC')
#             )
#             returning id
#             """
#
#     sql2 = """
#     INSERT INTO "ir_property"
#             (
#                         "id",
#                         "value_text",
#                         "name",
#                         "type",
#                         "company_id",
#                         "fields_id",
#                         "res_id",
#                         "create_uid",
#                         "write_uid",
#                         "create_date",
#                         "write_date"
#             )
#             VALUES
#             (
#                         Nextval('ir_property_id_seq'),
#                         'average',
#                         'cost_method',
#                         'selection',
#                         1,
#                         4162,
#                         %(product_template)s,
#                         1,
#                         1,
#                         (Now() at time zone 'UTC'),
#                         (Now() at time zone 'UTC')
#             )
#             returning id
#
#     """
#
#     destination_cur.execute(sql, dict(product_template="product.template,{}".format(id)))
#     destination_cur.execute(sql2, dict(product_template="product.template,{}".format(id)))
#     destination_cur.execute("insert into product_supplier_taxes_rel (prod_id,tax_id) values (%(id)s, 8)", dict(id=id))
#     destination_cur.execute("insert into product_supplier_taxes_rel (prod_id,tax_id) values (%(id)s, 5)", dict(id=id))
#     destination_cur.execute("insert into product_taxes_rel (prod_id,tax_id) values (%(id)s, 19)", dict(id=id))
#
# destination_data.commit()
#
#
#
#
# destination_data.close()
# source_data.close()

products = destination_api.search("product.template", [])
count = 1
for product in products:
    prod = source_api.read("product.template", product, ["standard_price"])

    destination_api.write("product.template", product, {"valuation": "real_time",
                                                        "type": "product",
                                                        "cost_method": "average",
                                                        "standard_price": prod["standard_price"]})
    count += 1
    print "update {}".format(count)

