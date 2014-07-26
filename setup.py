from __future__ import print_function
from setuptools import setup, find_packages
import os
import sys

long_description = """This project contains a library and tools for manipulating and generating metadata files that conform to the CableLabs VOD Metada 1.1 specification"""

install_dir = os.path.abspath(os.path.dirname(__file__))

# Install requires configparser for Python 2.x
install_requires = ['configparser'] if (sys.version_info[0] < 3) else []

# The path to MediaInfo should be supplied
MediaInfo_path = None
with open(os.path.join(install_dir, "MediaInfo.pth"), mode='r') as infile:
  for file_path in infile:
    file_path = file_path.strip()
    if os.path.isfile(file_path):
      MediaInfo_path = file_path
      break

if MediaInfo_path is not None:
  with open(os.path.join(install_dir, "vod_metadata", "MediaInfo.pth"), mode='w') as outfile:
    print(MediaInfo_path, file=outfile, end='')

setup(name='vod_metadata',
      
      version='2014.06.01',

      description='CableLabs VOD Metadata 1.1 library and tools',
      long_description="Library and tools for CableLabs VOD Metadata 1.1",
      
      url='https://github.com/bbayles/vod_metadata',
      
      author='Bo Bayles',
      author_email='bbayles@gmail.com',
      
      license='MIT',
      
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Telecommunications Industry',
                   'Topic :: Utilities',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',],
      
      keywords='cablelabs vod metadata',

      packages=find_packages(exclude=[]),
      
      install_requires=install_requires,
      # lxml is not required, but is recommended
      package_data = {'vod_metadata': ["*.ini", "*.mp4", "*.pth", "*.xml"]},
      extras_require = {'Speed':  ["lxml"]}
)
