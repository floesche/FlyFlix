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
import random
from datetime import datetime, timedelta
import atexit
from logging import FileHandler
from flask.logging import default_handler

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from csv_formatter import CsvFormatter

app = Flask(__name__)

start = False
updateFictrac = False
fictracGain = 100



from engineio.payload import Payload
Payload.max_decode_packets = 500


# Using eventlet breaks UDP reading thread unless patched. See http://eventlet.net/doc/basic_usage.html?highlight=monkey_patch#patching-functions for more.
#
# Alternatively disable eventlet and use development libraries via `socketio = SocketIO(app, async_mode='threading')`
import eventlet
eventlet.monkey_patch()
socketio = SocketIO(app)


# socketio = SocketIO(app, async_mode='threading')


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
    app.logger.info(["shared", "key", "value"])

def savedata(shared, key, value=0):
    app.logger.info([shared, key, value])

def trial(spatial, temporal, fictracGain):
    startOffTime = 1000
    trialLength = 3000
    endOffTime = 500
    closedLoopTime = 1500
    sharedKey = time.time()
    savedata(sharedKey, "screen-spat-off", startOffTime)
    changeSpatOff(spatial, startOffTime)
    savedata(sharedKey, "move-speed", temporal)
    savedata(sharedKey, "move-duration", trialLength)
    rotateStripes(trialLength, temporal)
    savedata(sharedKey, "screen-off-end", endOffTime)
    turnOffScreen(endOffTime)
    savedata(sharedKey, "screen-on-end")
    socketio.emit('screen', 1)
    savedata(sharedKey, "fictrac-on", fictracGain)
    turnOnFictrac(closedLoopTime, fictracGain)
    savedata(sharedKey, "fictrac-off")

def calibrate():
    sharedKey = time.time()
    savedata(sharedKey, "protocol", "calibration-closed-loop")
    changeSpatOff(3, 3000)
    turnOnFictrac(60000, 50)
    savedata(sharedKey, "screen-off")
    socketio.emit('screen', 0)


def experiment():
    sharedKey = time.time()
    savedata(sharedKey, "init-screen-off")
    

    savedata(sharedKey, "starvation-start", "2020-11-22 11:40:00")
    savedata(sharedKey, "fly-strain", "DL")
    savedata(sharedKey, "fly", 70)
    #savedata(sharedKey, "tether-start", "15:05:00")
    #savedata(sharedKey, "sex", "")
    
    # savedata(sharedKey, "fly-strain", "empty-split")
    # savedata(sharedKey, "ball", "13")
    # savedata(sharedKey, "air", "pump")
    # savedata(sharedKey, "glue", "KOA")    
    # savedata(sharedKey, "starvation-start", "2020-11-29 16:25:00")
    
    # savedata(sharedKey, "fly", 130)
    # savedata(sharedKey, "tether-start", "2020-11-29 16:45:00")
    # savedata(sharedKey, "fly", 131)
    # savedata(sharedKey, "tether-start", "2020-11-29 16:50:00")
    # savedata(sharedKey, "fly", 132)
    # savedata(sharedKey, "tether-start", "2020-11-29 16:55:00")
    # savedata(sharedKey, "fly", 133)
    # savedata(sharedKey, "tether-start", "2020-11-29 17:00:00")
    # savedata(sharedKey, "fly", 134)
    # savedata(sharedKey, "tether-start", "2020-11-29 17:05:00")


    savedata(sharedKey, "temperature", 34)
    savedata(sharedKey, "distance", 35)

    socketio.emit('screen', 0)
    while not start:
        time.sleep(0.1)
    savedata(sharedKey, "init-screen-on")
    socketio.emit('screen', 1)
    savedata(sharedKey, "display", "fire")
    savedata(sharedKey, "color", "#00FF00")
    savedata(sharedKey, "screen-brightness", 25)
    savedata(sharedKey, "protocol", 3)
    
    # ### Experiment
    startOffTime = 15000
    savedata(0, "screen-off-experiment-start", startOffTime)
    turnOffScreen(startOffTime)
    trialnr = 1
    conditionnr = 1
    while trialnr < 5:
        trialnr = trialnr + 1
        savedata(sharedKey, "trial-nr-start", trialnr)
        for i in random.sample([10, 7, 15, 5, 2, 20, 1], k=7):
            for j in random.sample([1, 0.5, 2, 0.3, 3, 0.1, 5], k=7):
                for k in random.sample([-1, 1], k=2):
                    savedata(sharedKey, "condition-nr-start", conditionnr)
                    trial(i, j*k, random.randrange(10, 100, 10))
                    savedata(sharedKey, "condition-nr-end", conditionnr)
                    conditionnr = conditionnr + 1
        savedata(sharedKey, "trial-nr-end", trialnr)
        
    savedata(sharedKey, "end-screen-off")
    socketio.emit('screen', 0)
    ### Calibration
    # calibrate()
    
    

def rotateStripes(duration=3000, direction=1):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    while datetime.now() < ttime:
        sharedKey = time.time_ns()
        savedata(sharedKey, "send-stripe-update", direction)
        socketio.emit('direction', (sharedKey, 0, direction))
        time.sleep(0.01)

def turnOffScreen(duration=1000, background="#000000"):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    socketio.emit('screen', (0, background))
    while datetime.now() < ttime:
        time.sleep(0.01)
    # socketio.emit('screen', 1)

def changeSpatOff(spatial, duration=1000, background="#000000"):
    sharedKey = time.time()
    ttime = datetime.now() + timedelta(milliseconds=duration)
    savedata(sharedKey, "changeSpatOff-duration", duration)
    socketio.emit('screen', (0, background))
    time.sleep(0.01)
    savedata(sharedKey, "changeSpatOff-spatial", spatial)
    socketio.emit('spatfreq', spatial)
    while datetime.now() < ttime:
        time.sleep(0.01)
    savedata(sharedKey, "changeSpatOff-on")
    socketio.emit('screen', 1)

def turnOnFictrac(duration=3000, gain=100):
    sharedKey = time.time()
    ttime = datetime.now() + timedelta(milliseconds=duration)
    global updateFictrac
    global fictracGain
    updateFictrac = True
    fictracGain = gain
    savedata(sharedKey, "fictrac-gain", gain)
    while datetime.now() < ttime:
        time.sleep(0.01)
    updateFictrac = False
    savedata(sharedKey, "fictrac-end")
    
    

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
            updateval = (heading-prevheading) * fictracGain * -1
            savedata(ts, "heading", heading)
            if updateFictrac:
                savedata(cnt, "updateval", updateval)
                socketio.emit('direction', (cnt, ts, updateval))

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

@socketio.on('start-experiment')
def finally_start(number):
    # FIXME: bad practice. Will break at some point
    global start
    start = True

@socketio.on('slog')
def server_log(key, value):
    sharedKey = time.time()
    savedata(sharedKey, key, value)

@socketio.on('display')
def display_event(json):
    savedata(json['cnt'], "display-receive", json['counter'])

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
    fthread = Thread(target=listenFictrac)
    fthread.daemon = True
    fthread.start()
    try:
        #return render_template('fictrac.html')
        return render_template('fictrac_canvas.html')
    except TemplateNotFound:
        abort(404)

def localmove():
    while True:
        nmbr = random.randint(1, 20)
        socketio.emit('screen', 0)
        socketio.emit('spatfreq', nmbr)
        time.sleep(0.5)
        socketio.emit('screen', 1)
        dstn = random.choice([1, 0.5, 2, 0.3, 3])
        direction = random.choice([-1, 1])
        rotateStripes(10000, dstn * direction)


@app.route('/ldev/')
def local_dev():
    mthread = Thread(target=localmove)
    mthread.daemon = True
    mthread.start()
    return render_template('fictrac_canvas.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port = 17000)
