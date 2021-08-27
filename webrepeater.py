#!/bin/env python

import socket
import math
import time
import logging
import random

from datetime import datetime, timedelta
from pathlib import Path
from logging import FileHandler

import eventlet

from flask import Flask, render_template, request, abort
from flask.logging import default_handler
from flask_socketio import SocketIO

from jinja2 import TemplateNotFound

from engineio.payload import Payload

from Experiment import SpatialTemporal, Duration, OpenLoopCondition, SweepCondition, ClosedLoopCondition, Trial, CsvFormatter

app = Flask(__name__)

start = False
UPDATE_FICTRAC = False
FICTRAC_GAIN = 100
SWEEPCOUNTERREACHED = False


Payload.max_decode_packets = 500

# Using eventlet breaks UDP reading thread unless patched. 
# See http://eventlet.net/doc/basic_usage.html?highlight=monkey_patch#patching-functions for more.
# Alternatively disable eventlet and use development libraries via 
# `socketio = SocketIO(app, async_mode='threading')`

eventlet.monkey_patch()
# socketio = SocketIO(app)
# FIXME: find out if CORS is needed
socketio = SocketIO(app, cors_allowed_origins='*')

# socketio = SocketIO(app, async_mode='threading')

@app.before_first_request
def before_first_request():
    app.config.update(
        FICTRAC_HOST = '127.0.0.1',
        FICTRAC_PORT = 1717
    )
    data_path = Path("data")
    if data_path.exists():
        if not data_path.is_dir():
            errmsg = "'data' exists as a file, but we need to create a directory with that name to log data"
            app.logger.error(errmsg)
            raise Exception("'data' exists as a file, but we need to create a directory with that name to log data")
    else:
        data_path.mkdir()
    csv_handler = FileHandler("data/repeater_{}.csv".format(time.strftime("%Y%m%d_%H%M%S")))
    csv_handler.setFormatter(CsvFormatter())
    app.logger.removeHandler(default_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(csv_handler)
    app.logger.info(["client_timestamp", "request_timestamp", "key", "value"])


def savedata(shared, key, value=0):
    app.logger.info([shared, key, value])


def logdata(client_timestamp, request_timestamp, key, value):
    app.logger.info([client_timestamp, request_timestamp, key, value])


def trial(spatial, temporal, FICTRAC_GAIN, nthframe=1):
    pretrial_duration = 500
    trial_duration = 3000
    posttrial_duration = 500
    closedLoopTime = 5000
    shared_key = time.time()
    savedata(shared_key, "pre-trial-duration", pretrial_duration)
    socketio.emit('speed', (shared_key, 0))
    change_spatial_freq_during_screen_off(spatial, pretrial_duration, 1)
    savedata(shared_key, "move-speed", temporal)
    savedata(shared_key, "open-loop-duration", trial_duration)
    if spatial<1 :
        move_sweep(2, temporal, nthframe)
    else :
        move_open_loop(trial_duration, temporal, nthframe)
    savedata(shared_key, "post-trial-duration", posttrial_duration)
    socketio.emit('speed', (shared_key, 0))
    turn_screen_off(posttrial_duration, 1)
    savedata(shared_key, "post-trial-end")
    socketio.emit('screen', 1)
    savedata(shared_key, "closed-loop-start", FICTRAC_GAIN)
    turn_on_fictrac(closedLoopTime, FICTRAC_GAIN)
    savedata(shared_key, "closed-loop-end")

def calibrate():
    shared_key = time.time()
    savedata(shared_key, "protocol", "calibration-closed-loop")
    change_spatial_freq_during_screen_off(3, 3000)
    turn_on_fictrac(60000, 50)
    savedata(shared_key, "screen-off")
    socketio.emit('screen', 0)


def experiment():
    shared_key = time.time()
    savedata(shared_key, "pre-experiment-begin")

    savedata(shared_key, "day-start", "7:00:00")
    savedata(shared_key, "fly-strain", "DL")
    savedata(shared_key, "distance", 35)

    savedata(shared_key, "temperature", 32)
    savedata(shared_key, "ball", "1")
    savedata(shared_key, "air", "wall")
    savedata(shared_key, "glue", "KOA")

    savedata(shared_key, "birthdate-from", "2021-02-17 19:00:00")
    savedata(shared_key, "birthdate-to", "2021-02-18 20:00:00")
    savedata(shared_key, "starvation-start", "2021-02-11 14:00:00")
    savedata(shared_key, "fly-batch", "2021-01-23")
    # savedata(shared_key, "fly", 230)
    # savedata(shared_key, "tether-start", "2012-02-11 15:55:00")
    # savedata(shared_key, "sex", "")

    # savedata(shared_key, "fly", 231)
    # savedata(shared_key, "tether-start", "2012-02-11 16:00:00")
    # savedata(shared_key, "sex", "")

    # savedata(shared_key, "fly", 232)
    # savedata(shared_key, "tether-start", "2012-02-11 16:09:00")
    # savedata(shared_key, "sex", "")

    # savedata(shared_key, "fly", 233)
    # savedata(shared_key, "tether-start", "2012-02-11 18:52:00")
    # savedata(shared_key, "sex", "")

    # savedata(shared_key, "fly", 234)
    # savedata(shared_key, "tether-start", "2012-02-11 18:56:00")
    # savedata(shared_key, "sex", "")

    # savedata(shared_key, "fly", 235)
    # savedata(shared_key, "tether-start", "2012-02-11 19:04:00")
    # savedata(shared_key, "sex", "")

    savedata(shared_key, "fly", 236)
    savedata(shared_key, "tether-start", "2012-02-11 19:09:00")
    savedata(shared_key, "sex", "")

    savedata(shared_key, "display", "fire")
    savedata(shared_key, "color", "#00FF00")
    savedata(shared_key, "screen-brightness", 25)
    savedata(shared_key, "protocol", 6)

    savedata(shared_key, "pre-experiment-screen-off")
    socketio.emit('screen', 0)
    while not start:
        time.sleep(0.1)
    savedata(shared_key, "pre-experiment-screen-on")
    socketio.emit('screen', 1)
    # ### Experiment
    preExperimentDuration = 15000
    savedata(0, "pre-experiment-duration", preExperimentDuration)
    turn_screen_off(preExperimentDuration)
    blockRepetitionCount = 1
    trialCount = 1
    while blockRepetitionCount < 5:
        blockRepetitionCount = blockRepetitionCount + 1
        savedata(shared_key, "block-repetition-count-start", blockRepetitionCount)
        trials = list()
        for i in [1, 2, 4, 8, 16]: # Nr of bars
            for j in [0.1, 0.5, 1, 2, 4, 8, 16, 32]: # in Hz
                for k in [-1, 1]: # direction
                    trials.append([i, j*k])

        trials = random.sample(trials, k=len(trials))

        for current_trial in trials:
            savedata(shared_key, "trial-count-start", trialCount)
            trial(current_trial[0], current_trial[1], random.randrange(10, 100, 10))
            savedata(shared_key, "trial-count-end", trialCount)
            trialCount = trialCount + 1
        savedata(shared_key, "block-repetition-count-end", blockRepetitionCount)
        
    savedata(shared_key, "end-screen-off")
    socketio.emit('screen', 0)
    ### Calibration
    # calibrate()


def move_open_loop(duration=3000, direction=1, nthframe = 1):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    shared_key = time.time_ns()
    savedata(shared_key, "send-stripe-update", direction)
    socketio.emit('speed', (shared_key, direction))
    savedata(shared_key, "show-only-nth-frame", nthframe)
    socketio.emit('nthframe', nthframe)
    while datetime.now() < ttime:
        time.sleep(0.01)


def move_sweep(sweep_count=1, direction=1, nthframe = 1):
    shared_key = time.time_ns()
    savedata(shared_key, "send-stripe-update", direction)
    socketio.emit('speed', (shared_key, direction))
    savedata(shared_key, "send-sweep-reset", sweep_count)
    socketio.emit('sweepcount', sweep_count)
    savedata(shared_key, "show-only-nth-frame", nthframe)
    socketio.emit('nthframe', nthframe)
    global SWEEPCOUNTERREACHED
    SWEEPCOUNTERREACHED = False
    while not SWEEPCOUNTERREACHED:
        time.sleep(0.01)


def turn_screen_off(duration=1000, offvalue=0, background="#000000"):
    ttime = datetime.now() + timedelta(milliseconds=duration)
    socketio.emit('screen', (offvalue, background))
    while datetime.now() < ttime:
        time.sleep(0.01)
    # socketio.emit('screen', 1)


def change_spatial_freq_during_screen_off(spatial, duration=1000, offvalue=0, background="#000000"):
    shared_key = time.time()
    ttime = datetime.now() + timedelta(milliseconds=duration)
    savedata(shared_key, "change_spatial_freq_during_screen_off-duration", duration)
    socketio.emit('screen', (offvalue, background))
    time.sleep(0.01)
    savedata(shared_key, "change_spatial_freq_during_screen_off-spatial", spatial)
    socketio.emit('spatfreq', spatial)
    while datetime.now() < ttime:
        time.sleep(0.01)
    savedata(shared_key, "change_spatial_freq_during_screen_off-on")
    socketio.emit('screen', 1)


def turn_on_fictrac(duration=3000, gain=100):
    shared_key = time.time()
    ttime = datetime.now() + timedelta(milliseconds=duration)
    global UPDATE_FICTRAC
    global FICTRAC_GAIN
    UPDATE_FICTRAC = True
    FICTRAC_GAIN = gain
    savedata(shared_key, "fictrac-gain", gain)
    while datetime.now() < ttime:
        time.sleep(0.01)
    UPDATE_FICTRAC = False
    savedata(shared_key, "fictrac-end")


def listen_to_fictrac():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.1)
        prevheading = 0
        data = ""
        try:
            sock.bind((app.config['FICTRAC_HOST'], app.config['FICTRAC_PORT']))
            new_data = sock.recv(1)
            data = new_data.decode('UTF-8')
        except: # If Fictrac doesn't exist
            print("Fictrac is not running.")
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
            if (len(toks) < 24) | (toks[0] != "FT"):
                continue
            cnt = int(toks[1])
            heading = float(toks[17])
            timestamp = float(toks[22])
            updateval = (heading-prevheading) * FICTRAC_GAIN * -1
            savedata(timestamp, "heading", heading)
            if UPDATE_FICTRAC:
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
    shared_key = time.time()
    savedata(shared_key, json['key'], json['value'])

@socketio.on('csync')
def server_client_sync(client_timestamp, request_timestamp, key):
    logdata(client_timestamp, request_timestamp, key, time.time_ns())


@socketio.on('dl')
def data_logger(client_timestamp, request_timestamp, key, value):
    logdata(client_timestamp, request_timestamp, key, value)


@socketio.on('display')
def display_event(json):
    savedata(json['cnt'], "display-offset", json['counter'])


@socketio.on('sweep-counter')
def set_sweep_counter_reached():
    global SWEEPCOUNTERREACHED
    SWEEPCOUNTERREACHED = True


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/playback/')
def playback():
    return render_template('playback.html')


@app.route('/fictrac/')
def hello():
    _ = socketio.start_background_task(target = experiment)
    _ = socketio.start_background_task(target = listen_to_fictrac)
    try:
        pass
    except TemplateNotFound:
        abort(404)
    return render_template('fictrac_canvas.html')


def localmove():
    while not start:
        time.sleep(0.1)
    sptmp1 = SpatialTemporal(bar_deg=10, space_deg=10, rotate_deg_hz = 0)
    dur = Duration(500000)
    cond1 = OpenLoopCondition(spatial_temporal=sptmp1, trial_duration=dur)
    cond1.trigger(socketio)
    sweeptmp1 = SpatialTemporal(bar_deg=3, space_deg=357, rotate_deg_hz=-30)
    cond2 = SweepCondition(spatial_temporal=sweeptmp1)
    cond2.trigger(socketio)


@app.route('/ldev/')
def local_dev():
    _ = socketio.start_background_task(target = localmove)
    return render_template('fictrac_canvas.html')

@app.route('/bdev/')
def threedee_dev():
    _ = Trial(1, bar_deg=30)
    _ = socketio.start_background_task(target=localmove)
    return render_template('bars.html')


def localfictrac():
    while not start:
        time.sleep(0.1)
    sptmp1 = SpatialTemporal(bar_deg=15, space_deg=105)
    cnd = ClosedLoopCondition(
        spatial_temporal=sptmp1, 
        trial_duration=Duration(60000), 
        gain=-1.0)
    cnd.trigger(socketio)
    socketio.emit('rotate-to', (0, math.radians(-15)))

@app.route('/fdev/')
def local_fictrac_dev():
    _ = socketio.start_background_task(target = localfictrac)
    return render_template('bars.html')

@socketio.on('pong')
def pinpongs(seq, dttime):
    dff = time.time_ns() -dttime
    print(f"{seq}, {dff}", )

def pingpong():
    seq = 0
    while 1:
        socketio.emit("ping", (seq, time.time_ns()))
        seq = seq + 1
        time.sleep(0.1)



@app.route('/ping/')
def local_ping_dev():
    _ = socketio.start_background_task(target = pingpong)
    return render_template('ping.html')


def localexperiment():
    while not start:
        time.sleep(0.1)
    print(time.strftime("%H:%M:%S", time.localtime()))
    log_metadata()

    block = []
    counter = 0

    # ## Grating spatial tuning 1Hz
    # for alpha in [60, 45,  30, 15, 10, 5, 2.5]:
    #     for direction in [-1, 1]:
    #         speed = 7.5
    #         rotation_speed = alpha*2*speed*direction
    #         clBar = (360 + alpha * direction) % 360
    #         gain = 1.0
    #         #gain = 1.0 + (((gaincount % 2)-0.5) * -2) * gains[(gaincount//2) % len(gains)]
    #         #gaincount += 1
    #         t = Trial(counter, bar_deg=alpha, rotate_deg_hz=rotation_speed, closedloop_bar_deg=clBar, closedloop_duration=Duration(1000), gain=gain, comment=f"spatialtuning alpha {alpha} direction {direction} gain {gain}")
    #         block.append(t)
    
    # ## grating 45° soeed tuning
    # for speed in [0.25, 1, 2, 4, 7.5, 15, 30]:
    #     for direction in [-1, 1]:
    #         alpha = 45
    #         rotation_speed = alpha*2*speed*direction
    #         clBar = (360 + alpha * direction*-1) % 360
    #         gain = 1.0 + (((gaincount % 2)-0.5) * -2) * gains[(gaincount//2) % len(gains)]
    #         gaincount += 1
    #         t = Trial(counter, bar_deg=alpha, rotate_deg_hz=rotation_speed, closedloop_bar_deg=clBar, gain=gain, comment=f"speedtuning speed {speed} direction {direction} gain {gain}")
    #         block.append(t)

    # ## Stepsize tuning
    # for fps in [60, 30, 15, 10, 5]:
    #     for direction in [-1, 1]:
    #         alpha = 45
    #         speed = 7.5
    #         rotation_speed = alpha*2*speed*direction
    #         clBar = (360 + alpha * direction) % 360
    #         gain = 1.0 + (((gaincount % 2)-0.5) * -2) * gains[(gaincount//2) % len(gains)]
    #         gaincount += 1
    #         t = Trial(counter, bar_deg=alpha, rotate_deg_hz=rotation_speed, closedloop_bar_deg=clBar, fps=fps, gain=gain, comment = f"stepsize fps {fps} direction {direction} gain {gain}")
    #         block.append(t)

    ## BarSweep
    speedcount = 0
    speeds = [0.25, 1, 4, 7.5, 15, 30, -0.25, -1, -4, -7.5, -15, -30]
    alpha = 180
    #for gain in [0, 0.5, 1, 1.5, 2, 10]:
    for gain in [-1, -0.5, 0.5, 1, 1.5, 2, 4, 8]:
        for cl_start in [0, 90, 180, 270]:
            speed = speeds[speedcount % len(speeds)]
            speedcount += 1
            rotation_speed = alpha*2*speed            
            current_trial = Trial(
                counter, 
                bar_deg=60, 
                space_deg=300, 
                openloop_duration=None, 
                sweep=1, 
                rotate_deg_hz=rotation_speed, 
                closedloop_bar_deg=alpha, 
                #closedloop_space_deg=alpha,    ## FIXME: doesn't exist anymore?
                #cl_start_position=cl_start,    ## FIXME: doesn't exist anymore?
                closedloop_duration=Duration(30000), 
                gain=gain, 
                comment = f"object speed {speed} bar {alpha} gain {gain}")
            block.append(current_trial)
    repetitions = 2
    opening_black_screen = Duration(10000)
    opening_black_screen.trigger_delay(socketio)
    for i in range(repetitions):
        socketio.emit("meta", (time.time_ns(), "block-repetition", i))
        block = random.sample(block, k=len(block))
        for current_trial in block:
            counter = counter + 1
            print(f"Condition {counter} of {len(block*repetitions)}")
            current_trial.set_id(counter)
            current_trial.trigger(socketio)
    print(time.strftime("%H:%M:%S", time.localtime()))


@app.route('/edev/')
def local_experiment_dev():
    """Runs function `localexperiment` for the route `/edev` in a background task and deliver the bars.html template."""
    print("Starting edev")
    _ = socketio.start_background_task(target = localexperiment)
    return render_template('bars.html')


def log_metadata():
    """
    The content of the `metadata` dictionary gets logged.
    
    This is a rudimentary way to save information related to the experiment to a file. Edit the content of the dictionary for each experiment.

    TODO: Editing code to store information is not good. Needs to change.
    """
    metadata = {
        "fly-strain": "DL",
        "fly-batch": "2021-03-02",
        # "day-start": "7:00:00",
        # "day-end": "19:00:00",
        "day-night-since": "2021-02-12",

        "birth-start": "2021-03-10 21:00:00",
        "birth-end": "2021-03-11 20:00:00",

        "starvation-start": "2021-03-16 16:50:00",

        # "tether-start": "2021-03-15 17:08:00",
        # "fly": 370,
        # "tether-end"  : "2021-03-15 17:16:00",
        # "sex": "f",
        # "fly": 371,
        # "tether-end"  : "2021-03-15 17:19:00",
        # "sex": "m",
        # "fly": 372,
        # "tether-end"  : "2021-03-15 17:22:00",
        # "sex": "m",
        # "fly": 373,
        # "tether-end"  : "2021-03-15 17:25:00",
        # "sex": "m",
        # "fly": 374,
        # "tether-end"  : "2021-03-15 17:27:00",
        # "sex": "m",

        "day-start": "21:00:00",
        "day-end": "13:00:00",
        "tether-start": "2021-03-16 20:11:00",

        # "fly": 375,
        # "tether-end"  : "2021-03-16 20:20:00",
        # "sex": "m",
        # "fly": 376,
        # "tether-end"  : "2021-03-16 20:23:00",
        # "sex": "f",
        # "fly": 377,
        # "tether-end"  : "2021-03-16 20:26:00",
        # "sex": "f",
        # "fly": 378,
        # "tether-end"  : "2021-03-16 20:29:00",
        # "sex": "f",
        "fly": 379,
        "tether-end"  : "2021-03-16 20:32:00",
        "sex": "f",

        "ball": "1",
        "air": "wall",
        "glue": "KOA",
        
        "temperature": 32,
        "distance": 35,
        "protocol": 12,
        "screen-brightness": 100,
        "display": "fire",
        "color": "#FFFFFF",
    }
    shared_key = time.time_ns()
    for key, value in metadata.items():
        logdata(0, shared_key, key, value)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port = 17000)
