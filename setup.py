from setuptools import setup, find_packages
import sys

long_description = (
    "This project contains a library and tools for manipulating and "
    "generating metadata files that conform to the CableLabs VOD Metada 1.1 "
    "specification"
)

# Install requires configparser for Python 2.x
install_requires = ['configparser'] if (sys.version_info[0] < 3) else []

setup(
    name='vod_metadata',
    version='2014.07.28',
    license='MIT',
    url='https://github.com/bbayles/vod_metadata',

    description='CableLabs VOD Metadata 1.1 library and tools',
    long_description="Library and tools for CableLabs VOD Metadata 1.1",

    author='Bo Bayles',
    author_email='bbayles@gmail.com',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Telecommunications Industry',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='cablelabs vod metadata',

    packages=find_packages(exclude=[]),
    test_suite='tests',

    # lxml is not required, but is recommended
    install_requires=install_requires,
    extras_require={'Speed':  ["lxml"]},

    package_data={'vod_metadata': ["*.ini", "*.mp4", "*.pth", "*.xml"]},
)
