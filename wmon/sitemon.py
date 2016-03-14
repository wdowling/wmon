""" sitemon.py

Base class for site traffic monitoring and alerting.
"""
import logging
import shlex
import sqlite3
import sys
import time
import os

from datetime import datetime
from trafficdatabase import TrafficDatabase

__copyright__ = "Copyright 2016 William Dowling"
__version__ = "0.1.0"

logger = logging.getLogger(__name__)

class SiteMon(object):

	def __init__(self, filehandle, threshold):
		""" Basic initialization.
		"""
		self.fh = filehandle
		self.th = threshold
		self.dbObj = TrafficDatabase()

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

	def displayTraffic(self):
		""" Display section of the website with most hits.
		"""
		os.system('clear')
		count = 0
		self.activeAlert = False
		try:
			print " wmon - Website Monitor."
			print " Observe traffic statistics for your site and alert on high traffiic."                        
			print " File opened: /var/log/apache2/access.log "
			self.prev = time.time() - 120
			self.alertrecords = self.dbObj.listRecord('traffic')
			for self.row in self.alertrecords:
				self.avghits = float(self.row[0]) / 120.0
				self.alert = { 'count': self.row[0]}
				if self.avghits > 0.1 and self.activeAlert == False:
					print " High traffic generated on alert - hits = %.3f" % (self.avghits)
					self.alert['status'] = 'Alert'
					self.alert['avghits'] = self.avghits
					self.dbObj.addRecord('alerts', self.alert)
					self.activeAlert = True
				else:
					print " Traffic rate normal - hits = %.3f" % (self.avghits)	
					self.alert['status'] = 'Normal'
					self.alert['avghits'] = self.avghits
					self.dbObj.addRecord('alerts', self.alert)
					self.activeAlert = False
			print " --[Top Hits]-------------------------------------------------------------------"
			print " {0:20} {1:20}".format('Section','Hits')
			self.lbrecords = self.dbObj.listRecord('leaderboard')
			if not self.lbrecords:
				print " Waiting for traffic..."
			else:
				for self.row in self.lbrecords:
					print " {0:20} {1:20} ".format(self.row[0], str(self.row[1]).ljust(0))        
			print "\n"
			print " --[Traffic Statistics]---------------------------------------------------------"
			print " {0:20} {1:20} {2:20}".format('Host','Total Bytes Sent','Hits') 
			self.statrecords = self.dbObj.listRecord('stats')
			if not self.statrecords:
				print " Waiting for traffic..."
			else:
				for self.row in self.statrecords:
					print " {0:20} {1:20} {2:20}".format(self.row[0], str(self.row[1]).ljust(0), str(self.row[2]).ljust(0))	
			print "\n"
			print " --[Alert History]---------------------------------------------------------------------"
			print " {0:20} {1:10} {2:20}".format('Time', 'Status', 'Avg Hits')
			self.alrecords = self.dbObj.listRecord('alerts')	
			for self.row in self.alrecords:
				print " {0:20} {1:10} {2:20}".format(str(self.row[0]), str(self.row[1]).ljust(0), str(self.row[2]).ljust(0))

		except KeyboardInterrupt:
			print "Shutting down cleanly..."
			return

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
		#self.c1, self.conn1 = self.getCursor()
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

				#Ping
				#self.ping()
				self.displayTraffic()
		except KeyboardInterrupt:
			print "Shutting down cleanly..."
			self.fh.close()
			return
