""" sitemon.py

Base class for site traffic monitoring and alerting.
"""
import logging
import shlex
import sqlite3
import sys
import time

from threading import Thread

__copyright__ = "Copyright 2016 William Dowling"
__version__ = "0.1.0"

logger = logging.getLogger(__name__)

class SiteMon(object):

	def __init__(self, filehandle, threshold):
		""" Basic initialization.
		"""
		self.fh = filehandle
		self.th = threshold
		try:
			self.initializeDB()
		except sqlite3.Error as e:
			logger.debug(str(e))

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

	def getInsertTime(self):
		""" Return current time in seconds since the epoch.
		"""
		return time.time()

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
		self.c2, self.conn2 = self.getCursor()
		print "Access Log Traffic Statistics"
		while True:
			time.sleep(10)
			for self.row in self.c2.execute("SELECT * FROM leaderboard ORDER BY count DESC"):
				print self.row

	def scanLog(self):
		""" Read access.log and parses data.

		This function reads the access.log file, parses each line and writes
		the data to the traffic and leaderboard tables. 
		"""
		self.c1, self.conn1 = self.getCursor()
		self.loglines = self.follow(self.fh)
		for self.l in self.loglines:
			self.epochtime = self.getInsertTime()
			self.params = self.parseLine(self.l)
			self.c1.execute("INSERT INTO traffic VALUES (?,?,?,?,?,?,?,?)", 
						(self.epochtime, self.params['host'], self.params['ident'], self.params['authuser'], self.params['date'], self.params['request'], self.params['status'], self.params['size']))

			# Update the leaderboard table with the section of the site that has been accessed.
			self.section = self.getSection(self.params['request'])
			self.c1.execute("INSERT OR REPLACE INTO leaderboard (section, count, host) VALUES (:section, :host, COALESCE((SELECT count + 1 FROM leaderboard WHERE section=:section AND host=:host), 1))", {"section": self.section, "host": self.params['host']})
			self.conn1.commit()
		
	def alert(self):
		pass

	def getCursor(self):
		""" Return database cursor.

		Return a cursor for each database connection opened.
		"""
		self.connection = sqlite3.connect('/tmp/wmon.db')
		self.cursor = self.connection.cursor()
		return self.cursor, self.connection

	def initializeDB(self):
		""" Initialize database and tables.

		Create the following tables in the wmon database:
			traffic
			leaderboard
			alerts
		"""
		self.c, self.conn = self.getCursor()
		self.c.execute('''CREATE table traffic
					(epochtime real, host text, ident text, authuser text, date text, request text, status text, size int)''')
		#self.c.execute('''CREATE table leaderboard
		#			(section unique, count int, host text)''')
		self.c.execute('''CREATE TABLE leaderboard
					(section text, count int, host text, UNIQUE(section, host) ON CONFLICT REPLACE)''')
		self.c.execute('''CREATE table alerts
					(epochtime real, count int)''')
		self.conn.commit()

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
			Thread(target = self.alert).start()
		except KeyboardInterrupt:
			logger.debug("Exiting")
			sys.exit(1)
