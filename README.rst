wmon - WebMonitor
=================

wmon allows systems administrators to monitor traffic hits on their site. It has the following characteristics:

* Reads an actively written to Apache or Nginx access.log.
* Displays the section of the website with the most hits every 10 seconds.
* Generates an alert to the console when total traffic for the past 2 minutes exceeds a certain number on average.
* Generates a recover alert to the console when the total traffic for the past 2 minutes goes below the threshold.
* Provides historical viewing of previous alerts.
