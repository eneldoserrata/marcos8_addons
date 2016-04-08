# -*- coding: utf-8 -*-
import xmlrpclib
import base64
from pprint import pprint as pp

url = "http://shoprrt.com/xmlrpc/object"

db = "rimreadytires"
uid = 1
password = "Antonio230"

sock = xmlrpclib.ServerProxy(url)

model = "product.template"

real_list =[]
# 155/70R10
with open("real_size.txt", "rb") as s:
    for row in s:
        real_part = "{}-{}-{}".format(row[:3], row[4:-4], row[6:])
        real_list.append(real_part)

count = 0
products_ids = sock.execute(db, uid, password, model, 'search', [])
products = sock.execute(db, uid, password, model, 'read', products_ids, ["name", "qty_available"])

avoid_list = {}

for product in products:
    # for part in real_list:
    #     if product["name"][-10:] == part[:-1]:
    #         count += 1
    #         print count, product["qty_available"], product["name"][-10:]
    #     elif product["qty_available"] > 0 and product["name"][-10:] != part[:-1]:
    #         if not avoid_list.get(product["name"], False):
    #             avoid_list[product["name"]] = product["qty_available"]
    #             count += 1
    #             print count

    if product["name"].startswith("U-PLT") and product["qty_available"] > 0:
        result = sock.execute(db, uid, password, model, 'write', product["id"], {"website_published": True})
    else:
        result = sock.execute(db, uid, password, model, 'write', product["id"], {"website_published": False})
    print result


pp(avoid_list)



