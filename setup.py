from setuptools import setup, find_packages
import sys
from db import __version__

setup(
    name = 'dbpy',
    version = __version__,
    author = "Thomas Huang",
    author_email='lyanghwy@gmail.com',
    description = "database abstraction layer for pythoneer",
    license = "GPL",
    keywords = "datbase abstraction layer for pythoneer(orm, database)",
    url='https://github.com/thomashuang/dbpy',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['samples', 'tests*']),
    zip_safe=False,
    include_package_data=True,
    install_requires = ['setuptools',  'MySQL-python'],
    test_suite='unittests',
    classifiers=(
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Database"
        )
    )