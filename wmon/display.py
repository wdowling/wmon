""" Base class for displaying information.

Due to the amount of print statements used, it makes sense to break this out
to its own class.
"""
import logging
import os
import time

from datetime import datetime

__copyright__ = "Copyright 2016 William Dowling"
__version__ = "0.1.0"

logger = logging.getLogger(__name__)

class Display(object):
	def __init__(self, dbObj, fh, th):
		self.dbObj = dbObj
		self.fh = fh
		self.th = th
		
	def displayTraffic(self):
		""" Display section of the website with most hits.

		Not the nicest looking function but it works. The width is kept to 79
		characters to keep with UNIX terminal width convention. To improve this
		we could use the Curses library to provide a more dynamic interface
		similar to Top or Htop. 
		"""
		os.system('clear')
		count = 0
		self.activeAlert = False
		try:
			print " wmon - Website Monitor \n \
Observe traffic statistics for your site and alert on high traffiic. Alert if \n \
threshold is exceeded within the previous 2 minutes.\n"
			print " File opened: %s" % self.fh.name
			print " Current threshold: %d" % self.th
			self.prev = time.time() - 120
			self.alertrecords = self.dbObj.listRecord('traffic')
			for self.row in self.alertrecords:
				self.avghits = float(self.row[0]) / 120.0
				self.alert = { 'count': self.row[0]}
				if self.avghits > 0.1 and self.activeAlert == False:
					self.currtime = datetime.today().strftime("%H:%M:%S")
					print " High traffic generated an alert - average hits = %.3f, triggered at %s \n" % (self.avghits, self.currtime)
					self.alert['status'] = 'Alert'
					self.alert['avghits'] = self.avghits
					self.dbObj.addRecord('alerts', self.alert)
					self.activeAlert = True
				else:
					print " Traffic rate normal - average hits = %.3f \n" % (self.avghits)	
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
			print " --[Alert History]--------------------------------------------------------------"
			print " {0:20} {1:10} {2:20}".format('Time', 'Status', 'Avg Hits')
			self.alrecords = self.dbObj.listRecord('alerts')	
			for self.row in self.alrecords:
				print " {0:20} {1:10} {2:.3f}".format(str(self.row[0]), str(self.row[1]).ljust(0), self.row[2])

		except KeyboardInterrupt:
			print "Shutting down cleanly..."
			return
