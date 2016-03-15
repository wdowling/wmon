## wmon
WebMon - Monitors HTTP traffic on a server

### Requirements

* Consume an actively written-to w3c-formatted HTTP access log 
  (https://en.wikipedia.org/wiki/Common_Log_Format)
* Every 10s, display in the console the sections of the web site with the most 
  hits (a section is defined as being what's before the second '/' in a URL. 
  i.e. the section for "http://my.site.com/pages/create' is 
  "http://my.site.com/pages"), as well as interesting summary statistics on the 
  traffic as a whole.
* Make sure a user can keep the console app running and monitor traffic on 
  their machine
* Whenever total traffic for the past 2 minutes exceeds a certain number on 
  average, add a message saying that 
  “High traffic generated an alert - hits = {value}, triggered at {time}”
* Whenever the total traffic drops again below that value on average for the 
  past 2 minutes, add another message detailing when the alert recovered
* Make sure all messages showing when alerting thresholds are crossed remain 
  visible on the page for historical reasons.
* Write a test for the alerting logic
* Explain how you’d improve on this application design

### Design

 The application is made up of a main file (wmon) which is the entry point. It
 initializes the logging, takes in command line options and instantiates the
 an object of the SiteMon class. 

 The core of the application is made up of three files:
 1. sitemon.py
    This file represents the bulk of the code. It begins by creating a new
    local sqlite database under /tmp. The details of this class will be
    discussed in the next section. The first function in the SiteMon class
    reads the logfile specified by the command line and carries out an
    operation similar to the UNIX tail command. Every 10th of a second it 
    reads the file and each new line is parsed into a dictionary. The data 
    represents each "hit" against the website (GET and POST) and is populated
    into three tables before finally calling the displayTraffic function.

 2. trafficDatabase.py
    This class was created to separate the basic database operations such as
    table creation, inserting and returning records. Due to the different
    data across each table, the listRecords() function checks for which table
    to return records for before proceeding.

 3. display.py
    The display class is used directly after the tables are populated. It
	defines how the console looks to the user using print statements, iterates
	through each of the tables and prints out the information aslong as there
	is an update in the access.log file. If no data is being written, it does
	not update the console.

### Building

  $ python setup.py sdist --format=gztar

### Installing

  $ pip install wmon-<VERSION>.tar.gz

### Running

  $ sudo wmon -f /var/log/apache2/access.log -t 100

 Due to the wmon.log being written to /var/log/wmon.log and usually the 
 access.log being readable by only root or the webserver user, the application 
 is ran using sudo. An optional threshold can be entered which represents the 
 average hits over the previous 2 minutes to alert on. The default threshold 
 is 100. When the application starts, it will not print anything to the screen 
 until the access.log is updated.

### Testing

 Python Unittesting framework:

  $ tar xzf wmon-0.1.0.tar.gz
  $ cd wmon-0.1.0/
  $ python -m unittest discover

 To test in a demo environment, a basic webserver was built with several 
 sections. The application was tested against this environment using smaller 
 thresholds. It has not been tested in an enterprise environment.

### Improvements

* Use Python Curses library. This would provide a more powerful interface for 
  the user allowing them to scroll, select, or even provide basic input.
* Refine and refactor code for performance. It has not been tested on large 
  production scale systems so there is a chance that it would fail in unusual ways.
* Use more Pythonic code where applicable (maps, generators, decorators etc).
* Offer option to create database where the user prefers.
* Possibly use threading which allows for multiple functions to work 
  concurrently (scanLog and displayTraffic).
* Better error handling.
* Improved Unittesting.
* Add more information to display such as top requests, users etc.
