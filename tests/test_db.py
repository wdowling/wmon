""" test_by.py

Unittesting for database creation.
"""
import os
import sqlite3
import unittest

__copyright__ = "Copyright 2016 William Dowling"
__version__ = "0.1.0"

class TestDB(unittest.TestCase):
	def setUp(self):
		""" Initialize test DB
		"""
		self.connection = sqlite3.connect('/tmp/wmon_test.db')
		self.cursor = self.connection.cursor()

	def testEntries(self):
		""" Create each table

		The following tables (and entries) are created:
			traffic
			leaderboard
			stats
			alerts
		"""
		self.cursor.execute('''CREATE TABLE traffic
								(epochtime real, host text, ident text, authuser text, date text, request text, status text, size int)''')
		self.cursor.execute('''CREATE TABLE leaderboard
								(section unique, count int)''')
		self.cursor.execute('''CREATE TABLE stats
								(host unique, bytes int, count int)''')
		self.cursor.execute('''CREATE TABLE alerts
								(epochtime real, count int)''')
		self.connection.commit()

	def tearDown(self):
		""" Drop tables
		"""
		self.cursor.execute('''DROP TABLE alerts ''')
		self.cursor.execute('''DROP TABLE stats ''')
		self.cursor.execute('''DROP TABLE leaderboard ''')
		self.cursor.execute('''DROP TABLE traffic ''')
		os.remove('/tmp/wmon_test.db')
		self.connection.commit()
