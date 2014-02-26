import unittest
import sys


if __name__ == '__main__':
    if len(sys.argv) > 1:
        unittest.main(module='flask_api.tests')
    else:
        argv = ['flask_api', 'discover', '-s', 'flask_api/tests']
        unittest.main(argv=argv)
