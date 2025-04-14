#!/usr/bin/env python
# -*- coding: "utf-8" -*-

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

long_description = open("README.rst").read()

setup(
        name='yahi',
        version='0.1.7',
        author='Julien Tayon, Stephane Bard',
        author_email='julien@tayon.net, stephanebard@gmail.com',
        packages=['yahi'],
        install_requires=[ 'archery>=0.1', 'pygeoip', 'httpagentparser', 'repoze.lru>=0.6' ],
        keywords=['log', 'parsing' ],
        url='http://yahi.readthedocs.org/',
        scripts=["scripts/speed_shoot", "scripts/yahi_all_in_one_maker"],
        license=open('LICENSE.txt').read(),
        description='Versatile log parser',
        long_description=long_description, 
        classifiers=[
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
)
