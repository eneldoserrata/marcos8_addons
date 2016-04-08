import xmlrpclib
from pprint import pprint as pp

# bad len 4, 16
# good len 2,3,14,17
file = "inventorytest.csv"
import requests
import json

location = []
inventory = []

lines = [line.strip() for line in open('inventory-a.txt')]

for line in lines:
    if len(line) in [2, 3]:
        inventory.append(line)
    elif len(line) == 4:
        inventory.append(line + " BAD LINE")
    elif len(line) == 14:
        # B-B-155-80-R13
        # U-PLT-C-285-75-R16
        old = line.split("-")
        coverted = "U-PLT-{}-{}-{}-{}".format(old[0], old[2], old[3], old[4])
        inventory.append(coverted)
    elif len(line) == 16:
        inventory.append(line + " BAD SKU")
    elif len(line) == 17:
        # 0005-C-155-80-R13
        # U-PLT-C-285-75-R16
        old = line.split("-")
        if len(old) == 4:
            oldn = old[1].split(".")
            coverted = "U-PLT-{}-{}-{}-{}".format(oldn[0], oldn[1], old[2], old[3])
        else:
            coverted = "U-PLT-{}-{}-{}-{}".format(old[1], old[2], old[3], old[4])
        inventory.append(coverted)

pp(inventory)