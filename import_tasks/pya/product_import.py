import csv
import xmlrpclib

db = "eym"
uid = 1
password = "admin"
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

tipos =  open('tipos-articulos.csv', 'r')
sub_tipos =  open('sub-tipos-articulos.csv', 'r')
product =  open('articulostodos2.csv', 'r')

dtipos = csv.reader(tipos, delimiter=',')
dsub_tipos = csv.reader(sub_tipos, delimiter=',')
dproduct = csv.reader(product, delimiter=',')

dtipos_list = [row for row in dtipos]
dsub_tipos_list = [row for row in dsub_tipos]
dproduct_list = [row for row in dproduct]

subtipo_list = []

# for tipo in dtipos_list:
#     vals = {'name': tipo[1],
#             'parent_id': 2,
#             'property_account_expense_categ': 179,
#             'property_account_income_categ': 167,
#             'property_stock_account_input_categ': False,
#             'property_stock_account_output_categ': False,
#             'property_stock_journal': 18,
#             'property_stock_valuation_account_id': False,
#             'removal_strategy_id': False,
#             'route_ids': [[6, False, []]],
#             'type': 'view',
#             "oldref": tipo[2]}
#     cat_id = sock.execute(db, uid, password, "product.category", "create", vals)
#     count = 0
#     for subtipo in dsub_tipos_list:
#         if tipo[2] == subtipo[2]:
#             subtipo_dict = {'name': subtipo[3],
#             'parent_id': cat_id,
#             'property_account_expense_categ': 179,
#             'property_account_income_categ': 167,
#             'property_stock_account_input_categ': False,
#             'property_stock_account_output_categ': False,
#             'property_stock_journal': 18,
#             'property_stock_valuation_account_id': False,
#             'removal_strategy_id': False,
#             'route_ids': [[6, False, []]],
#             'type': 'normal',
#             "oldref": subtipo[0]}
#             subtipo_list.append(subtipo_dict)
#         count += 1
#         print count
#
# count = 0
# for sub_tipos in subtipo_list:
#     cat_id = sock.execute(db, uid, password, "product.category", "create", sub_tipos)
#     count += 1
#     print count


product_list = []
count = 0
for product in dproduct_list:

    category_id = sock.execute(db, uid, password, "product.category", "search", [("oldref", "=", product[6])])
    if category_id:
        category_id = int(category_id[0])
    else:
        category_id = 2

    if product[8] == '':
        default_code = product[4]
    else:
        default_code = product[8]


    prod_dic = {
     'active': True,
     'attribute_line_ids': [],
     'categ_id': category_id,
     'company_id': 1,
     'cost_method': 'standard',
     'default_code': default_code,
     'description': False,
     'description_purchase': False,
     'description_sale': False,
     'ean13': False,
     'image_medium': False,
     'list_price': product[24],
     'loc_case': False,
     'loc_rack': False,
     'loc_row': False,
     'mes_type': 'fixed',
     'message_follower_ids': False,
     'message_ids': False,
     'name': product[2],
     'packaging_ids': [],
     'product_manager': False,
     'property_account_expense': False,
     'property_account_income': False,
     'property_stock_account_input': False,
     'property_stock_account_output': False,
     'property_stock_inventory': 5,
     'property_stock_procurement': 6,
     'property_stock_production': 7,
     'route_ids': [[6, False, []]],
     'sale_delay': 0,
     'sale_ok': True,
     'seller_ids': [],
     'standard_price': product[38],
     'state': False,
     'supplier_taxes_id': [[6, False, [8]]],
     'taxes_id': [[6, False, [19]]],
     'track_all': False,
     'track_incoming': False,
     'track_outgoing': False,
     'type': 'product',
     'uom_id': 1,
     'uom_po_id': 1,
     'uos_coeff': 1,
     'uos_id': False,
     'valuation': 'manual_periodic',
     'volume': 0,
     'warranty': 0,
     'weight': 0,
     'weight_net': 0}
    try:
        sock.execute(db, uid, password, "product.template", "create", prod_dic)
    except:
        pass
    count += 1
    print count