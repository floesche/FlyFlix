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
from datetime import datetime, timedelta
import atexit
from logging import FileHandler
from flask.logging import default_handler

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from csv_formatter import CsvFormatter

app = Flask(__name__)

# Using eventlet breaks UDP reading thread unless patched. See http://eventlet.net/doc/basic_usage.html?highlight=monkey_patch#patching-functions for more.
#
# Alternatively disable eventlet and use development libraries via `socketio = SocketIO(app, async_mode='threading')`
# import eventlet
# eventlet.monkey_patch()
# socketio = SocketIO(app)

socketio = SocketIO(app, async_mode='threading')


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



def runleft():
    for i in range(100):
        socketio.emit('direction', (i, 0, -.03))
        time.sleep(0.01)

def experiment():
    app.logger.info(["Left", "", ""])
    rotateStripes(3000)
    turnOffScreen(500)
    app.logger.info(["Right", "", ""])
    socketio.emit('spatfreq', 10);
    rotateStripes(3000, 0.01)
    app.logger.info(["Fictrac", "", ""])
    listenFictrac()
    app.logger.info(["Right", "", ""])
    rotateStripes(3000, 0.08)

def rotateStripes(duration=3000, direction=-0.03):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    while datetime.now() < ttime:
        socketio.emit('direction', (0, 0, direction))
        time.sleep(0.01)

def turnOffScreen(duration=1000, background="#000000"):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    socketio.emit('screen', (0, background))
    while datetime.now() < ttime:
        time.sleep(0.01)
    socketio.emit('screen', 1)

def listenFictrac(duration=3000):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.1)
        prevheading = 0
        data = ""
        try:
            sock.bind((app.config['FICTRAC_HOST'], app.config['FICTRAC_PORT']))
            new_data = sock.recv(1)
            data = new_data.decode('UTF-8')
        except: # If Fictrac doesn't exist
            while datetime.now() < ttime: # wait nevertheless
                pass
            return

        while datetime.now() < ttime:
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
    ethread = Thread(target=experiment)
    ethread.daemon = True
    ethread.start()
    try:
        return render_template('fictrac.html')
    except TemplateNotFound:
        abort(404)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port = 17000)
