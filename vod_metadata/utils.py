import os.path
import sys


# Find data files when frozen. Adapted from cx_Freeze documentation:
# http://cx-freeze.readthedocs.org/en/latest/faq.html
def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)
