from odoo_gateway import Session
from simple_timer import Timer


session = Session(['-c', '/Users/eneldoserrata/PycharmProjects/marcos_odoo/.openerp_serverrc', '-d', 'rim'])

cr = session.cr

lot_ids = [l.id for l in session.models.stock_production_lot.search([])]

count = 0
total_time = False
moves = set()
skua_cost = {}

for lot_id in session.models.stock_production_lot.search([]):
    timer = Timer()
    for quant in session.models.stock_quant.search([('lot_id', '=', lot_id.id)]):
        moves |= {move.id for move in quant.history_ids}
    try:
        for move_id in session.models.stock_move.search([("id", "in", sorted(list(moves)))]):
            if move_id.location_id.id == 8:
                order = session.models.purchase_order.search([('name', '=', move_id.origin)])
                order_lines = session.models.purchase_order_line.search([('order_id', '=', order.id)])
                for order_line in order_lines:
                    if order_line.product_id.id == move_id.product_id.id:
                        if order_line.price_unit_pesos:
                            cost = order_line.price_unit_pesos*order.custom_rate or 43.80
                        elif order_line.product_id.id == move_id.product_id.id:
                            cost = order_line.price_unit*43.80

                        if move_id.price_unit != cost:
                            session.models.stock_move.browse(move_id.id).write({"price_unit": cost})

                        if not skua_cost.get(move_id.product_id.id, False):
                            skua_cost[move_id.product_id.id] = {"qty": 1, "cost": cost or 0.00, "average": cost or 0.00}
                        else:
                            skua_cost[move_id.product_id.id]["qty"] += 1
                            skua_cost[move_id.product_id.id]["cost"] += cost
                            skua_cost[move_id.product_id.id]["average"] = skua_cost[move_id.product_id.id]["cost"]/skua_cost[move_id.product_id.id]["qty"]
    except:
        print "except"

    # current_time = timer.duration
    # total_time += current_time
    # print "id: {}, take: {}, total time: {}".format(lot_id.id, timer.duration, total_time)
    print lot_id.id
    cr.commit()
    moves = set()

count = 0
for key, val in skua_cost.iteritems():
    session.models.product_product.browse(key).write({"standard_price": val["average"]})
    count += 1
    print count

cr.commit()