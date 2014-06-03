from setuptools import setup, find_packages
from os import path
import sys

long_description = """This project contains a library and tools for manipulating and generating metadata files that conform to the CableLabs VOD Metada 1.1 specification"""

# Install requires configparser for Python 2.x
if sys.version_info[0] < 3:
  install_requires=['configparser'],
else:
  install_requires=[]

setup(name='vod_metadata',
      
      version='2014.06.01',

      description='A sample Python project',
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
      package_data = {'vod_metadata': ["*.ini", "*.mp4", "*.xml"]},
      extras_require = {'Speed':  ["lxml"]}
)