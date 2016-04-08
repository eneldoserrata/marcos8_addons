# -*- coding: utf-8 -*-
import xmlrpclib
import csv

product_list = []
product_clasification_list = []

price_file =  open('price_taxed.csv', 'r')
clasification_file =  open('tires_clasification.csv', 'r')

price_list = csv.reader(price_file, delimiter=',')
clasification_list = csv.reader(clasification_file, delimiter=',')

price_rows = [row for row in price_list]
clasification_rows = [row for row in clasification_list]


for index in range(3):
    for row in price_rows:
        if index == 0:
            grade = "A"
            price = float(row[3])
        elif index == 1:
            grade = "B"
            price = float(row[4])
        elif index == 2:
            grade = "C"
            price = float(row[5])
        product_list.append("U-PLT-{}-{}-{}-{},{}".format(grade, row[0], row[1], row[2], price))

for row in clasification_rows:
    product_clasification_list.append("{}-{}-{},{}".format(row[0],row[1],row[2],row[3],))

clasification_name = [row.split(",")[0] for row in product_clasification_list]

final_list = []
for prod in product_list:
    value = prod.split(",")[0][8:]
    if value in clasification_name:
        index = clasification_name.index(value)
        clasification = product_clasification_list[index].split(",")[1]
        final_prod = prod+",{}".format(clasification)
        # prod_index = product_list.index(prod)
        final_list.append(final_prod)
    else:
        final_list.append(prod+",")


price_file.close()
clasification_file.close()

# localurl = "http://127.0.0.1:8069/xmlrpc/object"
# rimurl = "http://shoprrt.com/xmlrpc/object"
db = "rim"
# db = "rimreadytires"
uid = 1
password = "Antonio230"

# from pprint import pprint as pp
# print pp(final_list)

sock = xmlrpclib.ServerProxy('http://127.0.0.1:8069/xmlrpc/object')
model = "product.template"
no_list = []
for row in final_list:
    product_name = row.split(",")[0]
    price = row.split(",")[1]
    clasification = row.split(",")[2]
    if clasification == "PLATINUM":
        clasification = "g"
    if clasification == "GOLD":
        clasification = "p"
    if clasification == "SILVER":
        clasification = "b"
    if clasification == "BRONZE":
        clasification = "s"
    prod_id = sock.execute(db, uid, password, model, 'search', [["default_code","=",product_name]])
    if len(prod_id):
        print prod_id
        result = sock.execute(db, uid, password, model, 'write', prod_id, {"list_price": float(price)})
    else:
        no_list.append(",".join([product_name, str(price), str(clasification)]))

print no_list
