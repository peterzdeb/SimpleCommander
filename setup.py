#!/usr/bin/env python3

from setuptools import setup

setup(
    name='web_gamepad',
    version='0.1.18',
    packages=['web_gamepad', 'web_gamepad.core', 'web_gamepad.gamepad'],
    include_package_data=True,
    package_dir={'': 'src'},
    package_data={'templates': ['*'], 'static': ['*']},
    install_requires={
        'aiohttp == 0.21.6',
        'aiohttp-jinja2 == 0.5.0'
    },
    zip_safe=False,
    url='https://github.com/peterzdeb/WebGamepad',
    license='Apache License, Version 2.0',
    author='Petro Zdeb',
    author_email='peterzdeb@gmail.com',
    description='Gamepad controller library based on lightweight AsyncIO web server'
)
