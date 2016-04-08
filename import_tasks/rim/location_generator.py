import string
from pprint import pprint as pp
import xmlrpclib
import csv

url = "http://127.0.0.1:8069"
db = "rim"
uid = 1
password = "Antonio230"

sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

location = []

rows = list(string.ascii_uppercase)[:14]

for row in rows:
    for col in range(43):
        if col > 0:
            index = rows.index(row) + 1
            # location.append("{}{},{},{},{}{}".format(col, row, index, col, col, row))
            values = {'loc_barcode': '{}{}'.format(col, row),
                      'scrap_location': False,
                      'valuation_in_account_id': False,
                      'name': '{}{}'.format(col, row),
                      'default_printer': False,
                      'location_id': 11,
                      'company_id': 1,
                      'putaway_strategy_id': False,
                      'active': True,
                      'posz': 0,
                      'posx': index,
                      'posy': col,
                      'usage': 'internal',
                      'print_barcode': False,
                      'valuation_out_account_id': False,
                      'partner_id': False,
                      'comment': False,
                      'removal_strategy_id': False}
            location.append(values)


for loc in location:
    print loc
    result = sock.execute(db, uid, password, 'stock.location', 'create', loc)
    print result

