#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup for the inReach Cursor-on-Target Gateway.

:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2021 Greg Albrecht
:license: Apache License, Version 2.0
:source: https://github.com/ampledata/inrcot
"""

import os
import sys

import setuptools

__title__ = "inrcot"
__version__ = "1.0.0b1"
__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


def publish():
    """Function for publishing package to pypi."""
    if sys.argv[-1] == "publish":
        os.system("python setup.py sdist")
        os.system("twine upload dist/*")
        sys.exit()


publish()


setuptools.setup(
    version=__version__,
    name=__title__,
    packages=[__title__],
    package_dir={__title__: __title__},
    url=f"https://github.com/ampledata/{__title__}",
    description="inReach Cursor-on-Target Gateway.",
    author="Greg Albrecht",
    author_email="oss@undef.net",
    package_data={"": ["LICENSE"]},
    license="Apache License, Version 2.0",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "pytak >= 3.0.0",
        "aiohttp"
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License"
    ],
    keywords=[
        "Satellite", "Cursor on Target", "ATAK", "TAK", "CoT"
    ],
    entry_points={"console_scripts": ["inrcot = inrcot.commands:cli"]}
)
