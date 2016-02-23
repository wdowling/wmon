""" Setuptools for WebMonitor application.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='wmon',
	version='0.1.0',
	description='Application to monitor website traffic statistics',
	long_description=long_description,

	# Repo is private
	url='https://github.com/wdowling/wmon',
	author='William Dowling',
	author_email='wmdowling@gmail.com',
	license='Other/Proprietary License',

	classifiers=[
		# Project maturity
		'Development Status :: 3 - Alpha',
		'Intended Audience :: System Administrators',
		'Topic :: System :: Systems Administration',
		'License :: Other/Proprietary License',
		'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
	],

	keywords='monitoring websites http traffic',

	packages=find_packages(exclude=['docs', 'tests']),

	entry_points={
		'console_scripts': [
			'wmon=wmon:main',
		],
	},
)
