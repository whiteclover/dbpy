#!/usr/bin/env python

from setuptools import setup, find_packages
import sys
from db import __version__
from codecs import open

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='dbpy',
    version=__version__,
    author="Thomas Huang",
    author_email='lyanghwy@gmail.com',
    description="database abstraction layer for pythoneer",
    long_description=readme,
    license="GPL",
    keywords="database abstraction layer for pythoneer(orm, database)",
    url='https://github.com/whiteclover/dbpy',
    packages=find_packages(exclude=['samples', 'tests*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=['setuptools'],
    test_suite='unittest',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'Topic :: Database'
    ]
)
