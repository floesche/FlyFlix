#!/bin/env python

from flask import Flask, render_template, url_for, request, abort
from flask_socketio import SocketIO
from jinja2 import TemplateNotFound
from threading import Thread
import socket
import csv
import math
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

from Condition import SpatialTemporal, Duration, OpenLoopCondition

from csv_formatter import CsvFormatter

app = Flask(__name__)

start = False
updateFictrac = False
fictracGain = 100
sweepCounterReached = False

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
    csv_handler = FileHandler("data/repeater_{}.csv".format(time.strftime("%Y%m%d_%H%M%S")))
    csv_handler.setFormatter(CsvFormatter())

    app.logger.removeHandler(default_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(csv_handler)
    app.logger.info(["shared", "key", "value"])

def savedata(shared, key, value=0):
    app.logger.info([shared, key, value])

def trial(spatial, temporal, fictracGain, nthframe=1):
    preTrialDuration = 500
    trialDuration = 3000
    postTrialDuration = 500
    closedLoopTime = 5000
    sharedKey = time.time()
    savedata(sharedKey, "pre-trial-duration", preTrialDuration)
    socketio.emit('speed', (sharedKey, 0))
    changeSpatOff(spatial, preTrialDuration, 1)
    savedata(sharedKey, "move-speed", temporal)
    savedata(sharedKey, "open-loop-duration", trialDuration)
    if spatial<1 :
        moveSweep(2, temporal, nthframe)
    else :
        moveOpenLoop(trialDuration, temporal, nthframe)
    
    savedata(sharedKey, "post-trial-duration", postTrialDuration)
    socketio.emit('speed', (sharedKey, 0))
    turnOffScreen(postTrialDuration, 1)
    savedata(sharedKey, "post-trial-end")
    socketio.emit('screen', 1)
    savedata(sharedKey, "closed-loop-start", fictracGain)
    turnOnFictrac(closedLoopTime, fictracGain)
    savedata(sharedKey, "closed-loop-end")

def calibrate():
    sharedKey = time.time()
    savedata(sharedKey, "protocol", "calibration-closed-loop")
    changeSpatOff(3, 3000)
    turnOnFictrac(60000, 50)
    savedata(sharedKey, "screen-off")
    socketio.emit('screen', 0)


def experiment():
    sharedKey = time.time()
    savedata(sharedKey, "pre-experiment-begin")
    
    
    savedata(sharedKey, "day-start", "7:00:00")
    savedata(sharedKey, "fly-strain", "DL")
    savedata(sharedKey, "distance", 35)

    savedata(sharedKey, "temperature", 32)
    savedata(sharedKey, "ball", "1")
    savedata(sharedKey, "air", "wall")
    savedata(sharedKey, "glue", "KOA")


    savedata(sharedKey, "birthdate-from", "2021-02-17 19:00:00")
    savedata(sharedKey, "birthdate-to", "2021-02-18 20:00:00")
    savedata(sharedKey, "starvation-start", "2021-02-11 14:00:00")
    savedata(sharedKey, "fly-batch", "2021-01-23")
    # savedata(sharedKey, "fly", 230)
    # savedata(sharedKey, "tether-start", "2012-02-11 15:55:00")
    # savedata(sharedKey, "sex", "")

    # savedata(sharedKey, "fly", 231)
    # savedata(sharedKey, "tether-start", "2012-02-11 16:00:00")
    # savedata(sharedKey, "sex", "")

    # savedata(sharedKey, "fly", 232)
    # savedata(sharedKey, "tether-start", "2012-02-11 16:09:00")
    # savedata(sharedKey, "sex", "")

    # savedata(sharedKey, "fly", 233)
    # savedata(sharedKey, "tether-start", "2012-02-11 18:52:00")
    # savedata(sharedKey, "sex", "")

    # savedata(sharedKey, "fly", 234)
    # savedata(sharedKey, "tether-start", "2012-02-11 18:56:00")
    # savedata(sharedKey, "sex", "")

    # savedata(sharedKey, "fly", 235)
    # savedata(sharedKey, "tether-start", "2012-02-11 19:04:00")
    # savedata(sharedKey, "sex", "")

    savedata(sharedKey, "fly", 236)
    savedata(sharedKey, "tether-start", "2012-02-11 19:09:00")
    savedata(sharedKey, "sex", "")

    savedata(sharedKey, "display", "fire")
    savedata(sharedKey, "color", "#00FF00")
    savedata(sharedKey, "screen-brightness", 25)
    savedata(sharedKey, "protocol", 6)


    savedata(sharedKey, "pre-experiment-screen-off")
    socketio.emit('screen', 0)
    while not start:
        time.sleep(0.1)
    savedata(sharedKey, "pre-experiment-screen-on")
    socketio.emit('screen', 1)
    
    # ### Experiment
    preExperimentDuration = 15000
    savedata(0, "pre-experiment-duration", preExperimentDuration)
    turnOffScreen(preExperimentDuration)
    blockRepetitionCount = 1
    trialCount = 1
    while blockRepetitionCount < 5:
        blockRepetitionCount = blockRepetitionCount + 1
        savedata(sharedKey, "block-repetition-count-start", blockRepetitionCount)
        trials = list()
        for i in [1, 2, 4, 8, 16]: # Nr of bars
            for j in [0.1, 0.5, 1, 2, 4, 8, 16, 32]: # in Hz
                for k in [-1, 1]: # direction
                    trials.append([i, j*k])

        trials = random.sample(trials, k=len(trials))

        for currentTrial in trials:
            savedata(sharedKey, "trial-count-start", trialCount)
            trial(currentTrial[0], currentTrial[1], random.randrange(10, 100, 10))
            savedata(sharedKey, "trial-count-end", trialCount)
            trialCount = trialCount + 1
        savedata(sharedKey, "block-repetition-count-end", blockRepetitionCount)
        
    savedata(sharedKey, "end-screen-off")
    socketio.emit('screen', 0)
    ### Calibration
    # calibrate()

def moveOpenLoop(duration=3000, direction=1, nthframe = 1):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    sharedKey = time.time_ns()
    savedata(sharedKey, "send-stripe-update", direction)
    socketio.emit('speed', (sharedKey, direction))
    savedata(sharedKey, "show-only-nth-frame", nthframe)
    socketio.emit('nthframe', nthframe)
    while datetime.now() < ttime:
        time.sleep(0.01)

def moveSweep(sweepCount=1, direction=1, nthframe = 1):
    sharedKey = time.time_ns()
    savedata(sharedKey, "send-stripe-update", direction)
    socketio.emit('speed', (sharedKey, direction))
    savedata(sharedKey, "send-sweep-reset", sweepCount)
    socketio.emit('sweepcount', sweepCount)
    savedata(sharedKey, "show-only-nth-frame", nthframe)
    socketio.emit('nthframe', nthframe)
    global sweepCounterReached
    sweepCounterReached = False
    while not sweepCounterReached:
        time.sleep(0.01)


def turnOffScreen(duration=1000, offvalue=0, background="#000000"):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    socketio.emit('screen', (offvalue, background))
    while datetime.now() < ttime:
        time.sleep(0.01)
    # socketio.emit('screen', 1)

def changeSpatOff(spatial, duration=1000, offvalue=0, background="#000000"):
    sharedKey = time.time()
    ttime = datetime.now() + timedelta(milliseconds=duration)
    savedata(sharedKey, "changeSpatOff-duration", duration)
    socketio.emit('screen', (offvalue, background))
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
                savedata(cnt, "fictrac-change-speed", updateval)
                socketio.emit('speed', (cnt, updateval))

            prevheading = heading

@socketio.on("connect")
def connect():
    print("Client connected", request.sid)

@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)

@socketio.on('start-experiment')
def finally_start(number):
    # FIXME: bad practice. Will break at some point
    print("Started")
    global start
    start = True

@socketio.on('slog')
def server_log(json):
    sharedKey = time.time()
    savedata(sharedKey, json['key'], json['value'])

@socketio.on('display')
def display_event(json):
    savedata(json['cnt'], "display-offset", json['counter'])

@socketio.on('sweep-counter')
def sweepCounterReached(counter):
    global sweepCounterReached
    sweepCounterReached = True

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
    while not start:
        time.sleep(0.1)
    while True:
        #nmbr = random.randint(1, 20)
        # spatial = 0.25
        # frequency = 1 #0.1, 0.5, 1, 2, 4, 8, 16, 32
        # direction = random.choice([-1, 1])
        # direction=-1

        # changeSpatOff(spatial, 500)
        # # socketio.emit('screen', 0)
        # # time.sleep(0.05)
        # # socketio.emit('spatfreq', spatial)
        # # time.sleep(0.5)
        # # socketio.emit('screen', 1)
        # #dstn = random.choice([1, 0.5, 2, 0.3, 3])
        
        # #moveOpenLoop(10000, frequency * direction)
        # moveSweep(1, frequency * direction)
        # time.sleep(1)
        # socketio.emit('spatfreq', 2)
        # time.sleep(1)

        #trial(currentTrial[0], currentTrial[1], random.randrange(10, 100, 10))
        #trial(0.25, -1, 10)

        sptmp = SpatialTemporal(rotateDegHz = 30)
        dur = Duration()

        cond1 = OpenLoopCondition(spatialTemporal=sptmp, trialDuration=dur)
        cond2 = OpenLoopCondition(spatialTemporal=SpatialTemporal(rotateDegHz=-100), trialDuration=dur)

        #cond1.trigger(socketio)
        cond2.trigger(socketio)

        socketio.emit('rotate-to', (0, (-math.pi/2) - 10/180*math.pi))
        time.sleep(3)
        socketio.emit('spatial-setup', (0, 1, 1))
        #socketio.emit('rotate-by', (2, -0.01));

        #trial(2, -1, 10)
        # socketio.emit('spatfreq', 0.25)

        # moveOpenLoop(3000, 1)
        # moveOpenLoop(3000, -1)


        # moveSweep(1, 1)
        # time.sleep(1)
        # moveSweep(1, -1)
        # time.sleep(1)
        
        #moveOpenLoop(1000, frequency * direction)
        


@app.route('/ldev/')
def local_dev():
    
    # mthread = Thread(target=localmove)
    # mthread.daemon = True
    # mthread.start()
    mthread = socketio.start_background_task(target = localmove)
    
    return render_template('fictrac_canvas.html')

@app.route('/bdev/')
def threedee_dev():
    mthread = socketio.start_background_task(target=localmove)
    #mthread = Thread(target=localmove)
    #mthread.daemon = True
    #mthread.start()
    #print(mthread)
    return render_template('bars.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port = 17000)
