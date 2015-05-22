import unittest
import sys
import subprocess


if __name__ == '__main__':
    if len(sys.argv) > 1:
        unittest.main(module='flask_api.tests')
    else:
        subprocess.call([sys.executable, '-m', 'unittest', 'discover'])
