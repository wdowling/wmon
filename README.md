## wmon
WebMon - Monitors HTTP traffic on a server

### Requirements

* Consume an actively written-to w3c-formatted HTTP access log (https://en.wikipedia.org/wiki/Common_Log_Format)
* Every 10s, display in the console the sections of the web site with the most hits (a section is defined as being what's before the second '/' in a URL. i.e. the section for "http://my.site.com/pages/create' is "http://my.site.com/pages"), as well as interesting summary statistics on the traffic as a whole.
* Make sure a user can keep the console app running and monitor traffic on their machine
* Whenever total traffic for the past 2 minutes exceeds a certain number on average, add a message saying that “High traffic generated an alert - hits = {value}, triggered at {time}”
* Whenever the total traffic drops again below that value on average for the past 2 minutes, add another message detailing when the alert recovered
* Make sure all messages showing when alerting thresholds are crossed remain visible on the page for historical reasons.
* Write a test for the alerting logic
* Explain how you’d improve on this application design

### Building

  python setup.py sdist --format=gztar

### Installing

  pip install wmon-<VERSION>.tar.gz

### Improvements

* Use Python Curses library. This would provide a more powerful interface for the user allowing
  them to scroll, select, or even provide basic input.
* Refine and refactor code for performance. It has not been tested on large production scale systems
  so there is a chance that it would fail in unusual ways.
* Use more Pythonic code where applicable (maps, generators, decorators etc).
* Offer suggestion to keep the SQLite database permenantly.
* Offer option to create database where the user prefers.
* Possibly use threading which allows for multiple functions to work concurrently (scanLog and displayTraffic).
* Better error handling.
* Improved Unittesting.
