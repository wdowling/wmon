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

### Tasks

1. Develop command-line functionality with test:
    $ ./wmon
    usage:
        wmon -f /var/log/apache2/access.log
    $ ./wmon -h
2. Develop using curses, initial layout of window. Implement key binding 'q' for quitting.
3. Function to open access.log and read data into small sqlite DB.
4. Function to scan every 10seconds, the previous 2mins of data. Keep count of amount of
   hits to a section of a page.
5. Function to print string if more than X hits received in previous two minutes.
6. Output data to window.

### Libraries needed

* optparse
* curses
* sqlite3

