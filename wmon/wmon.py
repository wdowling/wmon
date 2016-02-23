#!/usr/bin/env python
""" wmon.py

Application which monitors website traffic and provides a curses based window
for the user.
"""
import argparse
import logging
import sys
import time

from console import console
 
__copyright__ = "Copyright 2016 William Dowling"
__version__ = "0.1.0"

# Global logging details for this module
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('/var/log/wmon.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - \
%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def start_console(filehandle, threshold):
	""" Start the monitoring console

	Define the window design and initialize the console to display data.
	"""

	cObj = console.Console()
	console = consoleSetup()
	logger.debug('Initalizing console...')
	
if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Website Traffic Monitor')
	parser.add_argument('-f', '--file',required=True, help='Path to HTTP access log', type=file)
	parser.add_argument('-t', '--threshold', required=False, help='Threshold for total number of hits', type=int)
	args = vars(parser.parse_args())

	filehandle = args['file']
	if args['threshold']:
		threshold = args['threshold']

	initialize_console(filehandle, threshold)
