from odoo_gateway import Session
from simple_timer import Timer


session = Session(['-c', '/Users/eneldoserrata/PycharmProjects/marcos_odoo/.openerp_serverrc', '-d', 'rim'])

cr = session.cr

lot_ids = [l.id for l in session.models.stock_production_lot.search([])]

count = 0
total_time = False
moves = set()
skua_ab = {}

for lot_id in session.models.stock_production_lot.search([]):
    timer = Timer()
    for quant in session.models.stock_quant.search([('lot_id', '=', lot_id.id)]):
        moves |= {move.id for move in quant.history_ids}
    try:
        from_qc_skua_cost = 0.00
        for move_id in session.models.stock_move.search([("id", "in", sorted(list(moves)))]):
            if move_id.location_id.usage == "internal" and move_id.location_id.usage == "supplier":
                move_id.with_context({"from_qc": False}).product_price_update_before_done()

            elif move_id.location_id.usage == "internal" and move_id.location_id.usage == "internal":
                move_id.with_context({"from_qc": False}).product_price_update_before_done()

            elif move_id.location_id.usage == "internal" and move_id.location_id.usage == "production":
                from_qc_skua_cost = move_id.product_id.standard_price
                context = {"from_qc": "skua", "from_qc_skua_cost": from_qc_skua_cost}
                move_id.with_context(context).product_price_update_before_done()

            elif move_id.location_id.usage == "production" and move_id.location_id.usage == "internal":
                if from_qc_skua_cost == 0.00:
                    from_qc_skua_cost = move_id.product_id.standard_price
                context = {"from_qc": "skub", "from_qc_skua_cost": from_qc_skua_cost}
                move_id.with_context(context).product_price_update_before_done()

            elif move_id.location_id.usage == "internal" and move_id.location_id.usage == "customer":
                move_id.with_context({"from_qc": False}).product_price_update_before_done()

            elif move_id.location_id.usage == "customer" and move_id.location_id.usage == "internal":
                move_id.with_context({"from_qc": False}).product_price_update_before_done()

            from_qc_skua_cost = 0.00


                # make_qc(self, cr, uid, 8, 'U-PLT-A-255-65-R18', {'canfix': True, 'location_id': 7, 'uid': 1, 'name': 'Administrator', 'default_printer': 4}, context=None):
    except:
        print "except"

    current_time = timer.duration
    total_time += current_time
    print "id: {}, Serial: {}, take: {}, total time: {}".format(lot_id.id, lot_id.name, timer.duration, total_time)
    cr.commit()
    moves = set()

