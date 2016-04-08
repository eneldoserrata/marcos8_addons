import xmlrpclib
import csv
from pprint import pprint as pp
from collections import defaultdict

# bad len 4, 16
# good len 2,3,14,17
file = "inventorytest.csv"

# 1 : final inventory
# 2 : list of all scan
# 3 : last PO
# 4 : Sales
report = 1

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

if report == 1:
    inventory_grade_dict = {}
    inventory_part_dict = {}
    grade_order = ("A", "B", "C")

    for key in grade_order:
        for row in inventory:
            if len(row) == 18:
                part = row[6]
                if part == key:
                    if not inventory_grade_dict.has_key(key):
                        inventory_grade_dict.update({key: 0})

        for row in inventory:
            if len(row) == 18:
                part = row[6]
                if part == key:
                    inventory_grade_dict[key] = inventory_grade_dict[key] + 1
    pp(inventory_grade_dict)

    for row in inventory:
        if len(row) == 18:
            part = "U-PLT-{}".format(row[6:])
            ring = "PLT-{}-{}".format(row[15:], row[6])
            if not inventory_part_dict.has_key(part):
                inventory_part_dict.update({part: {"ring": ring, "qty": 0}})

    for row in inventory:
        if len(row) == 18:
            part = "U-PLT-{}".format(row[6:])
            inventory_part_dict[part]["qty"] = inventory_part_dict[part]["qty"]+1

    pp(inventory_part_dict)


# #####==================================report 2================
if report == 3:
    po = {}
    for row in inventory:
        if len(row) == 18:
            if not po.has_key(row):
                po.update({row: 0})

    for row in inventory:
        if len(row) == 18:
            po[row] = po[row]+1

    pp(po)

# #####==================================report 4================
if report == 4:
    sale_lines = [line.strip() for line in open('inventory_sales-a.csv')]
    sales_dict = {}

    inventory_grade_dict = {}
    inventory_part_dict = {}
    grade_order = ("A", "B", "C")

    for key in grade_order:
        for row in sale_lines:
            new_row = row.split(",")
            if len(new_row[0]) == 18:
                part = new_row[0][6]
                if part == key:
                    if not inventory_grade_dict.has_key(key):
                        inventory_grade_dict.update({key: 0})

        for row in sale_lines:
            new_row = row.split(",")
            if len(new_row[0]) == 18:
                part = new_row[0][6]
                if part == key:
                    inventory_grade_dict[key] = inventory_grade_dict[key] + 1
    pp(inventory_grade_dict)

    for row in sale_lines:
        new_row = row.split(",")
        if len(new_row[0]) == 18:
            part = "U-PLT-{}".format(new_row[0][6:])
            ring = "PLT-{}-{}".format(new_row[0][15:], new_row[0][6])
            if not inventory_part_dict.has_key(part):
                inventory_part_dict.update({part: {"ring": ring, "qty": 0}})

    for row in sale_lines:
        new_row = row.split(",")
        if len(new_row[0]) == 18:
            part = "U-PLT-{}".format(new_row[0][6:])
            inventory_part_dict[part]["qty"] = inventory_part_dict[part]["qty"]+int(new_row[1])

    pp(inventory_part_dict)


# print pp(inventory)

