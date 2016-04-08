from odoo_gateway import Session
from simple_timer import Timer


session = Session(['-c', '/Users/eneldoserrata/PycharmProjects/marcos_odoo/.openerp_serverrc', '-d', 'rim'])


move_sql = """
SELECT   "stock_move"."product_id",
         "stock_move"."price_unit",
         "stock_picking"."name"
FROM     "stock_move"
          INNER JOIN "stock_picking"  ON "stock_move"."picking_id" = "stock_picking"."id"
"""
session.cr.execute(move_sql)
moves = session.cr.fetchall()

print session.models.account_move.search_count([('journal_id', '=', 24)])
print "un-post start"
session.models.account_move.search([('journal_id', '=', 24), ('state', '=', 'posted')]).button_cancel()
session.cr.commit()
print "un-post finish"

count = 0
commit = 500
for move in moves:


    sqld = """
            update account_move_line set debit = %(debit)s
            where ref = %(ref)s and product_id = %(product_id)s and debit > 0"""

    session.cr.execute(sqld, {"debit": move[1], "ref": move[2], "product_id": move[0]})

    sqlc = """
            update account_move_line set credit = %(credit)s
            where ref = %(ref)s and product_id = %(product_id)s and credit > 0"""

    session.cr.execute(sqlc, {"credit": move[1], "ref": move[2], "product_id": move[0]})

    if commit == 0:
        session.cr.commit()
        commit = 500
        print commit
    commit -= 1
    count += 1
    print count