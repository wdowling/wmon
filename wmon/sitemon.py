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
from threading import Thread
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
		#try:
			#self.initializeDB()
		self.dbObj = TrafficDatabase()
		#except sqlite3.Error as e:
		#	logger.debug(str(e))

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
		while True:
			print " wmon - Website Monitor."
			print " Monitor traffic usage on your website."
			print " File opened: /var/log/apache2/access.log "
			print " --------------------------------------------------------------------"
			print " Top Hits - sections with the most hits"
			print " section    | hits "
			self.lbrecords = self.dbObj.listRecord('leaderboard')
			for self.row in self.lbrecords:
				print " %s      | %s " % (self.row[0], self.row[1])        
			print " --------------------------------------------------------------------"
			print " Traffic Statistics"
			print " host        | total bytes sent        | hits    "
			self.statrecords = self.dbObj.listRecord('stats')
			for self.row in self.statrecords:
				print " %s      %s        %s" % (self.row[0], self.row[1], self.row[2])	
			print " --------------------------------------------------------------------"
			print " Alerts"
			self.prev = time.time() - 120
			self.alertrecords = self.dbObj.listRecord('traffic')
			for self.row in self.alertrecords:
				self.avghits = float(self.row[0]) / 120.0
				self.alert = { 'count': self.row[0]}
				if self.avghits > 0.1:
					print " High traffic generated on alert - hits = %.3f" % (self.avghits)
					self.dbObj.addRecord('alerts', self.alert)
				else:
					print " Traffic rate normal - hits = %.3f" % (self.avghits)

			time.sleep(5)
			os.system('clear')

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

	def alert(self):
		""" Alert if threshold is met

		Scan the traffic database for number of hits within the past now - 120 seconds. If
		number exceeds threshold, then populate the alert table with the current time and
		number of hits. If on the next scan the number is below the threshold, update the table
		with the recovery.
		"""
		self.c3, self.conn3 = self.getCursor()
		while True:
			time.sleep(10)
			self.prev = time.time() - 120
			print "\n"
			for self.row in self.c3.execute("SELECT COUNT(*) FROM traffic WHERE epochtime>:prev", {"prev": self.prev}):
				# Calculate the average number of hits across the previous 120 seconds
				self.avghits = float(self.row[0]) / 120.0
				if self.avghits > self.th:
					print "High traffic generated on alert - hits = %s, trigger at %.3f" % (self.avghits, datetime.now().strftime("%I:%M:%S%p"))
					self.c3.execute("INSERT INTO alerts (epochtime, count) VALUES (:epochtime, :count)", {"epochtime": time.time(), "count": self.row[0]})
					self.alertStatus = True
				else:
					print "Traffic volume normal"
					print "Hits on average over past 2mins - %.3f", (self.avghits)
					self.alertStatus = False

	def getCursor(self):
		""" Return database cursor.

		Return a cursor for each database connection opened.
		"""
		self.connection = sqlite3.connect('/tmp/wmon.db')
		self.cursor = self.connection.cursor()
		return self.cursor, self.connection

	def monitorTraffic(self):
		""" Entry point to begin monitoring.

		This module carries out a number of tasks. It starts several threads
		for each of the three main functions of the application:
			displayTraffic()
			scanLog()
			alert()
		"""
		try:
			Thread(target = self.displayTraffic).start()
			Thread(target = self.scanLog).start()
			#Thread(target = self.alert).start()
		except KeyboardInterrupt:
			logger.debug("Exiting")
			sys.exit(1)
