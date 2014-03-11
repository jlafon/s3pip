import sys

try:
    from s3pip import main
except NameError as err:
    sys.stderr.write('Error: boto and pip<=1.5 are required ({})'.format(err))

__author__ = 'Jharrod LaFon'
__license__ = 'MIT'
__version__ = '0.1.1'