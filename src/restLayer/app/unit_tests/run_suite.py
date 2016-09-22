__author__ = 'aarongary'

import unittest
from app import unit_tests
def run_test():
    suite = unittest.TestLoader().loadTestsFromModule(unit_tests.scratch_tests)
    unittest.TextTestRunner().run(suite)