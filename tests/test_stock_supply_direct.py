# This file is part of the stock_supply_direct module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class StockSupplyDirectTestCase(ModuleTestCase):
    'Test Stock Supply Direct module'
    module = 'stock_supply_direct'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        StockSupplyDirectTestCase))
    return suite
