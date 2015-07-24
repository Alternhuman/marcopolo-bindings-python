#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The MarcoPolo bindings
"""

from setuptools import setup, find_packages

from codecs import open
from os import path
from distutils.core import setup
from distutils.command.clean import clean
from distutils.command.install import install
import os

here = path.abspath(path.dirname(__file__))

if __name__ == "__main__":
    

    with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()

    setup(
        name='marcopolo.bindings',
        namespace_packages=['marcopolo'],
        provides=["marcopolo.bindings"],
        version='0.1.3',

        description='A python binding for MarcoPolo',

        long_description=long_description,

        url='',

        author='Diego Martín',

        author_email='martinarroyo@usal.es',

        license='MIT',

        classifiers=[
            'Development Status :: 3 - Alpha',

            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',

            'Topic :: Software Development :: Libraries :: Python Modules',

            'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',

            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Natural Language :: English',
        ],

        keywords="marcopolo discovery binding",

        packages=find_packages(),
        install_requires=[
            'marcopolo>=0.0.1',
            'six>=1.6.0'
        ],
    ) 
