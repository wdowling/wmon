""" test_alert.py

Test alert module.
"""
import os
import unittest
import sqlite3
from wmon import sitemon

class TestAlert(unittest.TestCase):

	def setUp(self):
		""" Generate 60 seconds of false data for testing.
		"""
		self.testlogfile = open('./tests/dummydata.txt')
		self.connection = sqlite3.connect('/tmp/wmon_test.db')
		self.cursor = self.connection.cursor()
		self.cursor.execute('''CREATE TABLE traffic
									(epochtime real, host text, ident text, authuser text, date text, request text, status text, size int)''')
		for self.line in self.testlogfile:
			self.logline = self.line.split(',')
			self.cursor.execute("INSERT INTO traffic VALUES (?,?,?,?,?,?,?,?)",
										(self.logline[0], self.logline[1], self.logline[2], self.logline[3], self.logline[4], self.logline[5], self.logline[6], self.logline[7]))

	def testData(self):
		""" Test data inserted.

		Read back data in traffic table.
		"""
		self.count = 0
		for self.row in self.cursor.execute("SELECT * FROM traffic"):
			for self.field in self.row:
				self.count = self.count + 1

		self.assertEqual(self.count, 112)

	def testAlert(self):
		""" Scan previous 30 seconds for high traffic.
		"""

	def tearDown(self):
		""" Drop table and delete DB
		"""
		self.cursor.execute('''DROP TABLE traffic''')
		os.remove('/tmp/wmon_test.db')
		

if __name__ == '__main__':
    unittest.main(verbosity=2)

