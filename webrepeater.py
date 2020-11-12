#!/bin/env python


from flask import Flask, render_template, url_for, request, abort
from flask_socketio import SocketIO
from jinja2 import TemplateNotFound
from threading import Thread
import socket
import csv
import io
import time
import logging
import atexit
from logging import FileHandler
from flask.logging import default_handler

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__)

# Using eventlet breaks UDP reading thread unless patched. See http://eventlet.net/doc/basic_usage.html?highlight=monkey_patch#patching-functions for more.
#
# Alternatively disable eventlet and use development libraries via `socketio = SocketIO(app, async_mode='threading')`
# import eventlet
# eventlet.monkey_patch()
# socketio = SocketIO(app)

socketio = SocketIO(app, async_mode='threading')


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

@app.before_first_request
def before_first_request():
    app.config.update(
        FICTRAC_HOST = '127.0.0.1',
        FICTRAC_PORT = 1717
    )
    csv_handler = FileHandler("repeater_{}.csv".format(time.strftime("%Y%m%d_%H%M%S")))
    csv_handler.setFormatter(CsvFormatter())

    app.logger.removeHandler(default_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(csv_handler)
    # app.logger.info("some text")
    app.logger.info(["a", "request", "start"])

    thread = Thread(target=listenFictrac)
    thread.daemon = True
    thread.start()

@app.before_first_request
def start_scheduler():
    #app.logger.info(["a", "background", "start"])
    scheduler = BackgroundScheduler()
    trigger = IntervalTrigger(seconds=5)
    scheduler.add_job(func=print_date_time, trigger=trigger)
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

def runleft():
    for i in range(100):
        socketio.emit('direction', (i, 0, -.03))
        time.sleep(0.01)
    
    

def print_date_time():
    app.logger.info(["time", "XXX", time.strftime("%A, %d. %B %Y %I:%M:%S %p")])
    thread = Thread(target=runleft)
    thread.daemon = True
    thread.start()

def listenFictrac():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((app.config['FICTRAC_HOST'], app.config['FICTRAC_PORT']))
        data = ""
        prevheading = 0
        while True:
            new_data = sock.recv(1024)
            if not new_data:
                break
            data += new_data.decode('UTF-8')
            # Find the first frame of data
            endline = data.find("\n")
            line = data[:endline]       # copy first frame
            data = data[endline+1:]     # delete first frame
            # Tokenise
            toks = line.split(", ")
		    # Check that we have sensible tokens
            if ((len(toks) < 24) | (toks[0] != "FT")):
                continue
            cnt = int(toks[1])
            heading = float(toks[17])
            ts = float(toks[22])
            socketio.emit('direction', (cnt, ts, heading-prevheading))
            #json = {'d': 's', 'cnt': cnt, 'ts': ts, 'head': heading}
            app.logger.info(['s', cnt, ts, heading])
            prevheading = heading

@socketio.on("connect")
def connect():
    print("Client connected", request.sid)

@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@socketio.on('display')
def display_event(json):
    # print("Display is " + str(json))
    # app.logger.info("Display: %s", str(json))
    #json['d'] = "r"
    app.logger.info(["r", json['cnt'], json['counter']])
    

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/playback/')
def playback():
    return render_template('playback.html')

@app.route('/fictrac/')
def hello():
    try:
        return render_template('fictrac.html')
    except TemplateNotFound:
        abort(404)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port = 17000)
