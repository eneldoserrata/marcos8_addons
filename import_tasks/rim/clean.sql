
=========do_transfer start=============
DELETE FROM stock_move_operation_link WHERE operation_id in (7820, 7821)
INSERT INTO "stock_move_operation_link" ("id", "reserved_quant_id", "qty", "move_id", "operation_id", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('stock_move_operation_link_id_seq'), NULL, 1.0, 7929, 7820, 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id
INSERT INTO "stock_move_operation_link" ("id", "reserved_quant_id", "qty", "move_id", "operation_id", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('stock_move_operation_link_id_seq'), NULL, 1.0, 7929, 7820, 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id
UPDATE "product_product" SET "write_uid"=1,"write_date"=(now() at time zone 'UTC') WHERE id IN (2490)

INSERT INTO "product_price_history" ("id", "datetime", "cost", "company_id", "product_template_id", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('product_price_history_id_seq'), '2014-11-22 15:22:38', 2000.0, 1, 2491, 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id

UPDATE "product_template" SET "write_uid"=1,"write_date"=(now() at time zone 'UTC') WHERE id IN (2491)


UPDATE "product_product" SET "name_template"='PLT-A-R16' WHERE id = 2490


INSERT INTO "stock_quant" ("id", "product_id", "company_id", "qty", "package_id", "cost", "lot_id", "in_date", "location_id", "owner_id", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('stock_quant_id_seq'), 2490, 1, 1.0, NULL, 2000.0, 7316, '2014-11-22 15:22:39', 12, NULL, 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id

insert into stock_quant_move_rel (quant_id,move_id) values (5807,7929)

UPDATE "stock_quant" SET "packaging_type_id"=NULL WHERE id = 5807


INSERT INTO "account_move" ("id", "name", "journal_id", "company_id", "state", "period_id", "date", "ref", "to_check", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('account_move_id_seq'), '/', 24, 1, 'draft', 12, '2014-11-22 03:16:04', 'WH/IN/00023', false, 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id


INSERT INTO "account_move_line" ("id", "ref", "account_id", "name", "quantity", "centralisation", "product_uom_id", "journal_id", "company_id", "currency_id", "credit", "state", "product_id", "period_id", "debit", "date", "date_created", "amount_currency", "partner_id", "move_id", "blocked", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('account_move_line_id_seq'), 'WH/IN/00023', 87, 'PLT-A-R16', 1.0, 'normal', 1, 24, 1, NULL, 0.0, 'draft', 2490, 12, 2000.0, '2014-11-22 03:16:04', '2014-11-22', 0.0, 97, 8362, false, 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id


INSERT INTO "account_move_line" ("id", "ref", "account_id", "name", "quantity", "centralisation", "product_uom_id", "journal_id", "company_id", "currency_id", "credit", "state", "product_id", "period_id", "debit", "date", "date_created", "amount_currency", "partner_id", "move_id", "blocked", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('account_move_line_id_seq'), 'WH/IN/00023', 179, 'PLT-A-R16', 1.0, 'normal', 1, 24, 1, NULL, 2000.0, 'draft', 2490, 12, 0.0, '2014-11-22 03:16:04', '2014-11-22', 0.0, 97, 8362, false, 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id
                    ORDER BY code

UPDATE "account_move" SET "company_id"=1 WHERE id = 8362
UPDATE "account_move_line" SET "company_id"=1 WHERE id = 17599
UPDATE "account_move_line" SET "ref"='WH/IN/00023' WHERE id = 17600
UPDATE "account_move_line" SET "company_id"=1 WHERE id = 17600
UPDATE "account_move" SET "partner_id"=97 WHERE id = 8362

UPDATE "account_move_line" SET "period_id"=12 WHERE id = 17600
UPDATE "account_move_line" SET "period_id"=12 WHERE id = 17599

UPDATE "account_move_line" SET "journal_id"=24 WHERE id = 17600
UPDATE "account_move_line" SET "journal_id"=24 WHERE id = 17599
UPDATE "account_move_line" SET "date"='2014-11-22' WHERE id = 17600
UPDATE "account_move_line" SET "date"='2014-11-22' WHERE id = 17599

UPDATE "account_move_line" SET "state"='valid',"write_uid"=1,"write_date"=(now() at time zone 'UTC') WHERE id IN (17600, 17599)

UPDATE "account_move_line" SET "ref"='WH/IN/00023' WHERE id = 17600
UPDATE "account_move_line" SET "ref"='WH/IN/00023' WHERE id = 17599


UPDATE "account_move_line" SET "company_id"=1 WHERE id = 17600
UPDATE "account_move_line" SET "company_id"=1 WHERE id = 17599

UPDATE "stock_move" SET "date"='2014-11-22 15:22:39',"state"='done',"write_uid"=1,"write_date"=(now() at time zone 'UTC') WHERE id IN (7929)

UPDATE "stock_picking" SET "state"='assigned' WHERE id = 60


INSERT INTO "stock_picking" ("id", "origin", "carrier_tracking_ref", "number_of_packages", "carrier_id", "partner_id", "priority", "picking_type_id", "move_type", "message_last_post", "company_id", "note", "state", "weight_uom_id", "owner_id", "backorder_id", "volume", "date", "reception_to_invoice", "recompute_pack_op", "name", "invoice_state", "create_uid", "write_uid", "create_date", "write_date") VALUES(nextval('stock_picking_id_seq'), 'PO00028', NULL, 0, NULL, 97, '1', 1, 'direct', NULL, 1, NULL, 'draft', 3, NULL, 60, 0.0, '2014-11-22 00:00:00', false, true, 'WH/IN/00027', 'none', 1, 1, (now() at time zone 'UTC'), (now() at time zone 'UTC')) RETURNING id


UPDATE "stock_picking" SET "invoice_state"='none' WHERE id = 64
UPDATE "stock_picking" SET "group_id"=NULL WHERE id = 64

UPDATE "stock_picking" SET "state"='draft' WHERE id = 64

UPDATE "stock_picking" SET "weight_net"='0.00',"weight"='0.00' WHERE id = 64



UPDATE "stock_move" SET "picking_id"=64,"write_uid"=1,"write_date"=(now() at time zone 'UTC') WHERE id IN (7928)

UPDATE "stock_picking" SET "invoice_state"='none' WHERE id = 60

UPDATE "stock_picking" SET "group_id"=39 WHERE id = 60

UPDATE "stock_picking" SET "reception_to_invoice"=false WHERE id = 60

UPDATE "stock_picking" SET "invoice_state"='none' WHERE id = 64
UPDATE "stock_picking" SET "group_id"=39 WHERE id = 64
UPDATE "stock_picking" SET "reception_to_invoice"=false WHERE id = 64

UPDATE "stock_picking" SET "priority"='1',"max_date"='2014-11-22 16:00:00',"min_date"='2014-11-22 16:00:00' WHERE id = 60
UPDATE "stock_picking" SET "state"='done' WHERE id = 60

UPDATE "stock_picking" SET "priority"='1',"max_date"='2014-11-22 16:00:00',"min_date"='2014-11-22 16:00:00' WHERE id = 64

UPDATE "stock_picking" SET "state"='assigned' WHERE id = 64

UPDATE "stock_picking" SET "weight_net"='0.00',"weight"='0.00' WHERE id = 60

UPDATE "stock_picking" SET "weight_net"='0.00',"weight"='0.00' WHERE id = 64
UPDATE "stock_picking" SET "date_done"='2014-11-22 15:22:39',"write_uid"=1,"write_date"=(now() at time zone 'UTC') WHERE id IN (60)

UPDATE "stock_picking" SET "recompute_pack_op"=true,"write_uid"=1,"write_date"=(now() at time zone 'UTC') WHERE id IN (64)

=========do_transfer end=============

