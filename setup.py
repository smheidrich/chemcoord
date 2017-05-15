#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup file for the chemcoord package.
"""

from __future__ import with_statement
from __future__ import absolute_import
from setuptools import setup, find_packages
from io import open
import os
import subprocess

MAIN_PACKAGE = 'chemcoord'
DESCRIPTION = "Python module for dealing with chemical coordinates."
LICENSE = 'LGPLv3'
AUTHOR = 'Oskar Weser'
EMAIL = 'oskar.weser@gmail.com'
URL = 'https://github.com/mcocdawc/chemcoord'
INSTALL_REQUIRES = ['numpy', 'pandas>=0.20']
KEYWORDS = ['chemcoord', 'transformation', 'cartesian', 'internal',
            'chemistry', 'zmatrix', 'xyz', 'zmat', 'coordinates',
            'coordinate system']

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Chemistry',
    'Topic :: Scientific/Engineering :: Physics']


def give_version():
    """Fetch version from git tags, and write to version.py.
    Also, when git is not available (PyPi package), use stored version.py.
    """
    version_py = os.path.join('.', 'version.py')

    try:
        version_git = subprocess.check_output(["git", "describe"]).rstrip()
        version_git = bytes.decode(version_git)[1:]
        git_hash = subprocess.check_output(['git', 'log', '--format="%H"', '-n', '1']).rstrip()
        git_hash = bytes.decode(git_hash).replace('"', '')
        print(git_hash)
    except:
        with open(version_py, 'r') as f:
            f.readline()
            version_git = f.readline().strip().split('=')[-1]
            git_hash = f.readline().strip().split('=')[-1]

    version_msg = "# Do not edit this file, pipeline versioning is governed by git tags"
    with open(version_py, 'w') as fh:
        fh.write(version_msg + os.linesep
                 + "__version__=" + version_git + os.linesep
                 + "_git_hash=" + git_hash)
    return version_git


def readme():
    '''Return the contents of the README.md file.'''
    with open('README.md') as freadme:
        return freadme.read()


def setup_package():
    setup(
        name=MAIN_PACKAGE,
        version=give_version(),
        url=URL,
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=EMAIL,
        include_package_data=True,
        keywords=KEYWORDS,
        license=LICENSE,
        long_description=readme(),
        classifiers=CLASSIFIERS,
        packages=find_packages(),
        install_requires=INSTALL_REQUIRES
    )


if __name__ == "__main__":
    setup_package()
