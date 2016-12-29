# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='almanac-bot',
    version='0.0.1',
    description='Almanac Bot for Twitter',
    long_description=readme,
    author='Julio C. Barrera',
    author_email='logoff@logoff.cat',
    url='https://github.com/logoff/almanac-bot',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)