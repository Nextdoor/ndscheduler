#!/usr/bin/env python
# -*- coding: utf-8 -*-

import multiprocessing  # To make python setup.py test happy
import os
import shutil
import subprocess

from distutils.command.clean import clean
from setuptools import find_packages
from setuptools import setup

multiprocessing

PACKAGE = 'ndscheduler'
__version__ = None
execfile(os.path.join('ndscheduler', 'version.py'))  # set __version__


# -*- Hooks -*-

class CleanHook(clean):

    def run(self):
        clean.run(self)

        def maybe_rm(path):
            if os.path.exists(path):
                shutil.rmtree(path)

        maybe_rm('ndscheduler.egg-info')
        maybe_rm('build')
        maybe_rm('.venv')
        maybe_rm('dist')
        subprocess.call('rm -rf *.egg', shell=True)
        subprocess.call('find . -name "*.pyc" -exec rm -rf {} \;',
                        shell=True)

# -*- Classifiers -*-

classes = """
    Development Status :: 5 - Production/Stable
    License :: OSI Approved :: BSD License
    Topic :: System :: Distributed Computing
    Topic :: Software Development :: Object Brokering
    Programming Language :: Python
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: OS Independent
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

# -*- %%% -*-

setup(
    name=PACKAGE,
    version=__version__,
    description='ndscheduler: A cron-replacement library from Nextdoor',
    long_description=open('README.md').read(),
    author='Nextdoor Engineering',
    author_email='eng@nextdoor.com',
    url='https://github.com/Nextdoor/ndscheduler',
    download_url='http://pypi.python.org/pypi/ndscheduler#downloads',
    license='Apache License, Version 2',
    keywords='scheduler nextdoor cron python',
    packages=find_packages(),
    package_data={'ndscheduler': [
        'static/css/*.css',
        'static/js/*.js',
        'static/*.html'
    ]},
    tests_require=[
        'funcsigs',
        'mock',
        'nose',
    ],
    test_suite='nose.collector',
    install_requires=[
        'setuptools == 17.1',
        'APScheduler == 3.0.0',
        'SQLAlchemy == 0.9.7',
        'tornado == 4.0.1',
        'python-dateutil == 2.2'
    ],
    classifiers=classifiers,
    cmdclass={'clean': CleanHook},
)
