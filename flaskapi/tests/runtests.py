import unittest
import sys


if __name__ == '__main__':
    if len(sys.argv) > 1:
        unittest.main(module='flaskapi.tests')
    else:
        argv = ['flaskapi', 'discover', '-s', 'flaskapi/tests']
        unittest.main(argv=argv)
