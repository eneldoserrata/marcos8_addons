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

real_list = []


count = 0
products_ids = sock.execute(db, uid, password, model, 'search', [])
products = sock.execute(db, uid, password, model, 'read', products_ids)

avoid_list = {}

for product in products:
    result = "Este no existe"
    if product["name"].startswith("U-PLT-A"):
        result = sock.execute(db, uid, password, model, 'write', product["id"], {"categ_id": 9})
    elif product["name"].startswith("U-PLT-B"):
        result = sock.execute(db, uid, password, model, 'write', product["id"], {"categ_id": 4})
    elif product["name"].startswith("U-PLT-C"):
        result = sock.execute(db, uid, password, model, 'write', product["id"], {"categ_id": 5})
    elif product["name"].startswith("U-PLT-T"):
        result = sock.execute(db, uid, password, model, 'write', product["id"], {"categ_id": 6})
    elif product["name"].startswith("U-PLT-S"):
        result = sock.execute(db, uid, password, model, 'write', product["id"], {"categ_id": 8})
    print result
    # if product["name"].startswith("U-PLT") and product["qty_available"] > 0:
    #     result = sock.execute(db, uid, password, model, 'write', product["id"], {"website_published": True})
    # else:
    #     result = sock.execute(db, uid, password, model, 'write', product["id"], {"website_published": False})
    # print result


pp(avoid_list)



