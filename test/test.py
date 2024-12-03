import os
import sys
import importlib

import unittest


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'] + ['discover', '-s', 'test', '-p', '*_test.py'], verbosity=2)