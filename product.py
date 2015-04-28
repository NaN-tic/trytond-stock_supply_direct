# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Equal, Not


__all__ = ['Template']
__metaclass__ = PoolMeta


class Template:
    __name__ = 'product.template'

    direct_stock_supply = fields.Boolean('Direct Stock Supply',
        help='Generates a purchase request for each stock line of this '
            'product regardless of the stock levels, when out/internal '
            'shipments are assigned.',
        states={
            'invisible': ~Eval('purchasable') |
                Not(Equal(Eval('type', 'goods'), 'goods')),
            },
        depends=['purchasable', 'type'])
