from setuptools import setup, find_packages
import sys
from db import __version__

setup(
    name = 'db',
    version = __version__,
    author = "Thomas Huang",
    author_email='lyanghwy@gmail.com',
    description = "db abstraction layer for pythoner",
    license = "GPL",
    keywords = "db abstraction layer for pythoner",
    url='https://github.com/thomashuang/dbpy',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires = ['setuptools',  'MySQL-python'],
    test_suite='unittests',
    classifiers=(
        "Development Status :: Production/Alpha",
        "License :: GPL",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scheduler"
        )
    )