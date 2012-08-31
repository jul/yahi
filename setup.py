#!/usr/bin/env python
# -*- coding: "utf-8" -*-

#from distutils.command.build_py import build_py as _build_py
#from distutils.core import setup
from setuptools import setup, find_packages
import unittest
import sys

def test():
    """Specialized Python source builder."""
    loader= unittest.TestLoader()
    suite=loader.discover(".", "test_yahi.py")
    runner=unittest.TextTestRunner()
    result=runner.run(suite)
    if  not result.wasSuccessful():
        raise Exception( "Test Failed: Aborting install")

if "sdist" in sys.argv or "bdist_egg" in sys.argv:
 
    test()

setup(
        name='yahi',
        version='0.1.0',
        author='Julien Tayon',
        author_email='julien@tayon.net',
        packages=['yahi'],
        install_requires=[ 'archery>=0.1', 'pygeoip', 'httpagentparser', 'repoze.lru>=0.6' ],
        keywords=['log', 'parsing' ],
        url='http://yahi.readthedocs.org/',
        scripts=["speed_shoot"],
        license=open('LICENSE.txt').read(),
        description='Versatile parallel log parser',
        classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
)
