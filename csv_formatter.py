
import logging
import io
import csv
import time

# from https://stackoverflow.com/questions/19765139/what-is-the-proper-way-to-do-logging-in-csv-file
class CsvFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.output = io.StringIO()
        self.writer = csv.writer(self.output, quoting=csv.QUOTE_ALL)

    def format(self, record):
        # self.writer.writerow([record.levelname] + [v for k,v in record.msg.items()])
        #self.writer.writerow([v for k,v in record.msg.items()])
        self.writer.writerow([time.monotonic_ns()] + record.msg)
        # self.writer.writerow([record.levelname, record.msg])
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()