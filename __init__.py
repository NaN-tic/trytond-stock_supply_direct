# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .product import *
from .move import *
from .purchase import *


def register():
    Pool.register(
        Template,
        Move,
        PurchaseRequest,
        module='stock_supply_direct', type_='model')
