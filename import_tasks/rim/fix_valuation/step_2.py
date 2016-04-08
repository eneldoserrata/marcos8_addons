from odoo_gateway import Session
from simple_timer import Timer


session = Session(['-c', '/Users/eneldoserrata/PycharmProjects/marcos_odoo/.openerp_serverrc', '-d', 'rim'])

for product in session.models.product_product.search([]):
    session.models.stock_move.search([('product_id', '=', product.id)]).write({"price_unit": product.standard_price})
    print product.id

session.cr.commit()