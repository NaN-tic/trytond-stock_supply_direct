# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


__all__ = ['PurchaseRequest']
__metaclass__ = PoolMeta


class PurchaseRequest:
    __name__ = 'purchase.request'

    @classmethod
    def _get_origin(cls):
        return super(PurchaseRequest, cls)._get_origin() | {'stock.move'}

    @classmethod
    def delete(cls, requests):
        Move = Pool().get('stock.move')

        moves = list(set(r.origin for r in requests
                if isinstance(r.origin, Move)))

        with Transaction().set_context(_check_access=False):
            if moves:
                Move.write(moves, {'purchase_request': None})

        super(PurchaseRequest, cls).delete(requests)
