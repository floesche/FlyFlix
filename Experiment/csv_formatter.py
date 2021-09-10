"""
Log data into a file

This implementation follows a receipe from
https://stackoverflow.com/questions/19765139/what-is-the-proper-way-to-do-logging-in-csv-file
"""

import logging
import io
import csv
import time

class CsvFormatter(logging.Formatter):
    """Subclass of logging.Formatter to write to a CSV file"""

    def __init__(self):
        """Simple constructor"""
        super().__init__()
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)

    def format(self, record):
        """
        Convert the record to a CSV row and return this row as a string.

        :param dict record: dictionary with all the content in the `msg` key
        :rtype: str
        """
        self.writer.writerow([time.time_ns()] + record.msg) # write CSV row to StringIO "fake file"
        data = self.output.getvalue() # get str from StringIO
        self.output.truncate(0) # empty output
        self.output.seek(0)
        return data.strip()
