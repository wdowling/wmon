""" TrafficDatabase class and methods
"""
import sqlite3
import time

from datetime import datetime


class TrafficDatabase(object):

    def __init__(self, filename="/tmp/wmon.db"):
        """ Initialize database.

        Default database file exists under /tmp. The file is not destroyed
        after the application shuts down. The user must move or delete it if
        she would like to start a new database.
        """
        self.dbfile = filename
        db = sqlite3.connect(self.dbfile)
        c = db.cursor()

        # Tables are permanent until the user manually deletes them
        c.execute('''CREATE TABLE IF NOT EXISTS traffic
                         (epochtime real,
                          host text,
                          ident text,
                          authuser text,
                          date text,
                          request text,
                          status text,
                          size int)''')
        c.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                         (section unique, count int)''')
        c.execute('''CREATE TABLE IF NOT EXISTS stats
                         (host unique,
                          bytes int,
                          count int)''')
        c.execute('''CREATE TABLE IF NOT EXISTS alerts
                         (time unique,
                          status text,
                          avghits real)''')
        db.commit()
        c.close()

    def getInsertTime(self):
        """ Return time in seconds since epoch
        """
        return time.time()

    def addRecord(self, table, params):
        """ Insert records to tables.

        Each table has its own unique constraints which means we must
        define different INSERT statements for each.
        """
        self.table = table
        self.epochtime = self.getInsertTime()
        self.datetime = datetime.today().strftime("%H:%M")
        self.params = params
        db = sqlite3.connect(self.dbfile)
        c = db.cursor()
        if self.table == 'traffic':
            c.execute('''INSERT INTO traffic VALUES (?,?,?,?,?,?,?,?)''',
                       (self.epochtime,
                       self.params['host'],
                       self.params['ident'],
                       self.params['authuser'],
                       self.params['date'],
                       self.params['request'],
                       self.params['status'],
                       self.params['size']))
        elif self.table == 'leaderboard':
            c.execute('''INSERT OR REPLACE INTO leaderboard (section, count) VALUES
                             (:section,
                              COALESCE((SELECT count + 1 FROM leaderboard WHERE section=:section), 1))''', {
                              "section": self.params['section']})
        elif self.table == 'stats':
            c.execute('''INSERT OR REPLACE INTO stats (host, bytes, count) VALUES
                            (:host,
                              COALESCE((SELECT bytes + :bytes FROM stats WHERE host=:host), 0),
                              COALESCE((SELECT count + 1 FROM stats WHERE host=:host), 1))''', {
                              "host": self.params['host'],
                              "bytes": self.params['size']})
        elif self.table == 'alerts':
            c.execute('''INSERT OR REPLACE INTO alerts(time, status, avghits) VALUES 
                           (:time,
                            :status,
                            :avghits)''', {
                            "time": self.datetime,
                            "status": self.params['status'],
                            "avghits": self.params['avghits']})

        db.commit()
        c.close()

    def listRecord(self, table):
        """ List database records.
        """
        self.table = table
        db = sqlite3.connect(self.dbfile)
        c = db.cursor()
        if self.table == 'leaderboard':
            c.execute('''SELECT * FROM leaderboard ORDER BY count DESC LIMIT 10''')
        elif self.table == 'stats':
            c.execute('''SELECT * FROM stats ORDER BY count DESC LIMIT 10''')
        elif self.table == 'traffic':
            self.prev = time.time() - 120
            c.execute('''SELECT COUNT(*) FROM traffic WHERE epochtime>:prev''', {"prev": self.prev})
        elif self.table == 'alerts':
            c.execute('''SELECT DISTINCT time, status, avghits FROM alerts
                      WHERE status="Alert" ORDER BY time DESC LIMIT 10''')

        records = c.fetchall()
        c.close()
        return records
