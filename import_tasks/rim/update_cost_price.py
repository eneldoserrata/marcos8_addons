import xmlrpclib
import csv


url = "http://127.0.0.1:8069"
db = "rim"
uid = 1
password = "Antonio230"

sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

#
model = "product.template"
no_list = []
with open('para_exportar.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        product_name = "U-PLT-{}-{}-{}-{}".format(row[0], row[1], row[2], row[3])
        prod_id = sock.execute(db, uid, password, model, 'search', [["default_code", "=" ,product_name]])
        price = float(row[4])
        cost = float(row[5])
        if len(prod_id):
            result = sock.execute(db, uid, password, model, 'write', prod_id, {"list_price": price, "standard_price": cost})
        else:
            no_list.append(",".join([product_name, str(price), str(cost)]))


from pprint import pprint as pp
pp(no_list)
pp(len(no_list))


