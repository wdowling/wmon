""" sitemon.py

Base class for site traffic monitoring and alerting.
"""
import logging
import shlex
import sqlite3
import sys
import time
import os

from trafficdatabase import TrafficDatabase
from display import Display

__copyright__ = "Copyright 2016 William Dowling"
__version__ = "0.1.0"

logger = logging.getLogger(__name__)

class SiteMon(object):

	def __init__(self, filehandle, threshold):
		""" Basic initialization.

		Ensure we can pass filehandle and threshold below and initialize database.
		"""
		self.fh = filehandle
		self.th = threshold
		self.dbObj = TrafficDatabase()
		self.dsObj = Display(self.dbObj, self.fh, self.th)

	def parseLine(self, l):
		""" Parse logline.

		Break up the logline in to defined fields and return a dictionary that
		can be fed into SQL queries.
		"""
		self.params = {}
		# Split into a whitespace separated list and remove square brackets.
		self.logline = shlex.split(l.translate(None, "[]"))
		self.params['host'] = self.logline[0]
		self.params['ident'] = self.logline[1]
		self.params['authuser'] = self.logline[2]
		self.params['date'] = self.logline[3]
		# We skip self.logline[4] because it represents the timezone i.e '+0000'
		self.params['request'] = self.logline[5]
		self.params['status'] = self.logline[6]
		self.params['size'] = self.logline[7]

		return self.params		

	def getSection(self, request):
		""" Return section of website.

		Parse access log request and pull out section of the site hit.
		"""
		self.r = request
		return self.r.split()[1].split("/")[1]

	def follow(self, logfile):
		""" Tail the logfile.

		This is a nice piece of code I lifted from StackOverflow which essentially
		tails a file specified. I used this piece of code before in production and it
		works quite well. It uses the seek() method which takes two parameters, 0 and 2.
		0 represents the offset while 2 represents the end of the file. So it means the 
		0th offset from the end of the file. It reads each line from this offset and it
		nothing appears, sleep for 0.1 seconds and try again. If a line is found, return
		the line.
		"""
		self.lgfile = logfile
		self.lgfile.seek(0,2)
		while True:
			self.line = self.lgfile.readline()
			if not self.line:
				time.sleep(0.1)
				continue
			yield self.line

	def popTraffic(self, params):
		table = 'traffic'
		self.traffic = params
		self.dbObj.addRecord(table, self.traffic)

	def popLeaderBoard(self, section):
		table = 'leaderboard'
		self.lb = section
		self.dbObj.addRecord(table, self.lb)

	def popStats(self, params):
		table = 'stats'
		self.stats = params
		self.dbObj.addRecord(table, self.stats)

	def scanLog(self):
		""" Read access.log and parses data.

		This function reads the access.log file, parses each line and writes
		the data to the traffic and leaderboard tables. 
		"""
		self.loglines = self.follow(self.fh)
		try:
			for self.l in self.loglines:
				self.params = self.parseLine(self.l)

				# Populate each table
				self.popTraffic(self.params)

				# Update the leaderboard table with the section of the site that has been accessed.
				self.section = { 'section': self.getSection(self.params['request'])}
				self.popLeaderBoard(self.section)

				# Update the statistics table with the number of hits coming from a single IP
				# Address and the total bytes sent.
				self.popStats(self.params)

				# Update screen with traffic statistics and alerts
				self.dsObj.displayTraffic()
		except KeyboardInterrupt:
			print "Shutting down cleanly..."
			self.fh.close()
			return
