# -*- coding: utf-8 -*-

from api import source_data, destination_data
from sql import PARTNER_SELECT, PARTNER_INSERT, ir_property_select, ir_property_insert, PARTNER_SELECT_PARENT


source_cur = source_data.cursor()
destination_cur = destination_data.cursor()

source_cur.execute(PARTNER_SELECT)
partner = source_cur.fetchall()

destination_cur.execute("DELETE FROM res_partner where id > 5")
destination_cur.execute("DELETE FROM ir_property where res_id like 'res.partner%'")
destination_data.commit()

count = 0
with_parent_list = []
for par in partner:


    destination_cur.execute(PARTNER_INSERT, par)
    new_partner = destination_cur.fetchone()

    source_cur.execute(ir_property_select, dict(like="res.partner%,{}".format(par[0])))
    properties = source_cur.fetchall()
    for prop in properties:
        prop = dict(prop)
        destination_cur.execute("SELECT id from ir_model_fields where name = %s", (prop["name"],))
        fields_id = destination_cur.fetchall()
        if fields_id:

            res_id = prop["res_id"].split(",")
            prop.update({"res_id": "{},{}".format(res_id[0], par[0])})
            prop.update({"fields_id": "{}".format(fields_id[0][0])})
            destination_cur.execute(ir_property_insert, prop)

    if count == 500:
        destination_data.commit()
        count = 0
    count += 1
    print count

source_cur.execute(PARTNER_SELECT_PARENT)
partner = source_cur.fetchall()

count = 0
with_parent_list = []
for par in partner:


    destination_cur.execute(PARTNER_INSERT, par)
    new_partner = destination_cur.fetchone()

    source_cur.execute(ir_property_select, dict(like="res.partner%,{}".format(par[0])))
    properties = source_cur.fetchall()
    for prop in properties:
        prop = dict(prop)
        destination_cur.execute("SELECT id from ir_model_fields where name = %s", (prop["name"],))
        fields_id = destination_cur.fetchall()
        if fields_id:

            res_id = prop["res_id"].split(",")
            prop.update({"res_id": "{},{}".format(res_id[0], par[0])})
            prop.update({"fields_id": "{}".format(fields_id[0][0])})
            destination_cur.execute(ir_property_insert, prop)

    count += 1
    if count == 500:
        destination_data.commit()
        count = 0
    print count

destination_data.commit()
destination_data.close()
source_data.close()