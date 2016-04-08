# -*- coding: utf-8 -*-
import xmlrpclib
import base64


url = "http://127.0.0.1:8069"
db = "rim"
uid = 1
password = "Antonio230"

sock = xmlrpclib.ServerProxy('http://127.0.0.1:8069/xmlrpc/object')

model = "product.template"

products_ids = sock.execute(db, uid, password, model, 'search', [])
products = sock.execute(db, uid, password, model, 'read', products_ids, ["name"])
i = open('neumaticos.jpg', 'rb').read()
base_img = base64.b64encode(i)
count = 0
for product in products:
    count += 1
    if product["name"].startswith("U-PLT"):
        try:
            result = sock.execute(db, uid, password, model, 'write', product["id"], {"image_medium": base_img})
            print count, result
        except:
            print "error"
