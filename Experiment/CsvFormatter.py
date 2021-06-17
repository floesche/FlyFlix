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
        """Define the file format"""
        # self.writer.writerow([record.levelname] + [v for k,v in record.msg.items()])
        #self.writer.writerow([v for k,v in record.msg.items()])
        self.writer.writerow([time.time_ns()] + record.msg)
        # self.writer.writerow([record.levelname, record.msg])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()
