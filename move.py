# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction


__all__ = ['Move']


class Move:
    __metaclass__ = PoolMeta
    __name__ = 'stock.move'

    purchase_request = fields.Many2One('purchase.request', 'Purchase Request',
        ondelete='SET NULL', readonly=True)
    purchase_request_state = fields.Function(fields.Selection([
                ('', ''),
                ('requested', 'Requested'),
                ('purchased', 'Purchased'),
                ('cancel', 'Cancel'),
                ], 'Purchase Request State',
            states={
                'invisible': ~Eval('purchase_request_state'),
                }), 'get_purchase_request_state')

    def get_purchase_request_state(self, name=None):
        if self.purchase_request is not None:
            purchase_line = self.purchase_request.purchase_line
            if purchase_line is not None:
                purchase = purchase_line.purchase
                if purchase.state == 'cancel':
                    return 'cancel'
                elif purchase.state in ('processing', 'done'):
                    return 'purchased'
            return 'requested'
        return ''

    @classmethod
    def copy(cls, lines, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default['purchase_request'] = None
        return super(Move, cls).copy(lines, default=default)

    @property
    def direct_stock_supply(self):
        'Returns True if stock move has to be supplied by purchase requests.'
        return self.product.direct_stock_supply

    def get_purchase_request(self):
        'Returns purchase request for the stock move'
        pool = Pool()
        Uom = pool.get('product.uom')
        Request = pool.get('purchase.request')

        if (not self.direct_stock_supply or (self.purchase_request and
                self.purchase_request.state in ['purchased', 'done'])):
            return

        product = self.product
        supplier, purchase_date = Request.find_best_supplier(product,
            self.planned_date or self.effective_date)
        uom = product.purchase_uom or product.default_uom
        quantity = Uom.compute_qty(self.uom, self.quantity, uom)
        requests = Request.search([
                ('product', '=', product.id),
                ('party', '=', supplier and supplier.id),
                ('quantity', '=', quantity),
                ('uom', '=', uom.id),
                ])
        if requests:
            request, = requests
            request.origin = self
        else:
            with Transaction().set_context(_check_access=False):
                if (self.purchase_request and
                        self.purchase_request.state == 'draft'):
                    request = self.purchase_request
                else:
                    request = Request()
                request.product = product
                request.party = supplier
                request.quantity = quantity
                request.uom = uom
                request.computed_quantity = quantity
                request.computed_uom = uom
                request.purchase_date = purchase_date
                request.supply_date = self.planned_date
                request.company = self.company
                request.origin = self
                request.warehouse = (self.from_location.warehouse or
                    self.to_location.warehouse)

        return request

    def create_purchase_requests(self):
        'Create the purchase requests for products with direct_stock_supply '
        'option checked'
        try:
            super(Move, self).create_purchase_requests()
        except AttributeError:
            pass
        request = self.get_purchase_request()
        if request:
            request.save()

    @classmethod
    def assign(cls, moves):
        'Create the purchase requests for moves with direct stock supply '
        'products when out/internal shipments are assigned'
        super(Move, cls).assign(moves)
        for move in moves:
            if (move.from_location.type == 'storage'
                    and move.to_location.type in ('storage', 'production')):
                move.create_purchase_requests()
