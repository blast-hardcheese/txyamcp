#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="txyamcp",
    version="0.1",
    description="Connection pool around txyam, a Twisted memcached client.",
    author="Devon Stewart",
    author_email="blast@hardchee.se",
    license="MIT",
    url="http://github.com/blast-hardcheese/txyamcp",
    packages=find_packages(),
    requires=["txyam"],
    install_requires=['txyam>=0.3']
)
