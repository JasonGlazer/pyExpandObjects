# -*- coding: utf-8 -*-

import unittest
from test import epjson_test


def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromModule(epjson_test))
    return suite

runner = unittest.TextTestRunner(verbosity=1)
runner.run(suite())
