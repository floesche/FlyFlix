#!/bin/env python

import socket
import math
import time
import logging
import random
import inspect
import warnings

from datetime import datetime, timedelta
from pathlib import Path
from logging import FileHandler

import eventlet

from flask import Flask, render_template, request, abort, url_for
from flask.logging import default_handler
from flask_socketio import SocketIO

from jinja2 import TemplateNotFound

from engineio.payload import Payload

from Experiment import SpatialTemporal, Duration, OpenLoopCondition, SweepCondition, ClosedLoopCondition, Trial, CsvFormatter

app = Flask(__name__)

start = False
SWEEPCOUNTERREACHED = False
RUN_FICTRAC = False


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
    """
    Server initiator: check for paths  and initialize logger.
    """
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
    app.logger.info(["client_id", "client_timestamp", "request_timestamp", "key", "value"])


def savedata(sid, shared, key, value=0):
    """
    Store data on disk. It is intended to be key-value pairs, together with a shared knowledge
    item. Data storage is done through the logging.FileHandler. 

    :param str shared: intended for shared knowledge between client and server
    :param str key: Key from the key-value pair
    :param str value: Value from the key-value pair.
    """
    app.logger.info([sid, shared, key, value])


def logdata(sid, client_timestamp, request_timestamp, key, value):
    """
    Store data on disk. In addition to a key-value pair, the interface allows to store a client
    timestamp and an additional timestamp, for example from the initial server request. In 
    practice, all these values are just logged to disk and stored no matter what they are.

    :param str client_timestamp: timestamp received from the client
    :param str request_timestamp: server timestamp that initiated the client action
    :param str key: key of the key-value pair
    :param str value: value of the key-value pair
    """
    app.logger.info([sid, client_timestamp, request_timestamp, key, value])


@socketio.on("connect")
def connect():
    """
    Confirm SocketIO connection by printing "Client connected"
    """
    print("Client connected", request.sid)


@socketio.on("disconnect")
def disconnect():
    """
    Verify SocketIO disconnect
    """
    print("Client disconnected", request.sid)


@socketio.on('start-experiment')
def finally_start(number):
    """
    When the server receives a `start-experiment` message via SocketIO, the global variable start
    is set to true

    :param number: TODO find out what it does
    """
    # FIXME: bad practice. Will break at some point
    print("Started")
    global start
    start = True
    socketio.emit('experiment-started');


@socketio.on('slog')
def server_log(json):
    """
    Save `key` and `value` from the dictionary received inside the SocketIO message `slog` to disk.

    :param json: dictionary received from the client via SocketIO
    """
    shared_key = time.time()
    savedata(request.sid, shared_key, json['key'], json['value'])

@socketio.on('csync')
def server_client_sync(client_timestamp, request_timestamp, key):
    """
    Save parameters to disk together with a current timestamp. This can be used for precisely 
    logging the round trip times.

    :param client_timestamp: timestamp from the client
    :param request_timestamp: timestamp that the client initially received from the server and 
        which started the process
    :param key: key that should be logged. 
    """
    logdata(request.sid, client_timestamp, request_timestamp, key, time.time_ns())


@socketio.on('dl')
def data_logger(client_timestamp, request_timestamp, key, value):
    """
    data logger routine for data sent from the client.

    :param client_timestamp: timestamp from the client
    :param request_timestamp: timestamp that the client initially received from the server and 
        which started the process
    :param key: key from key-value pair
    :param value: value from key-value pair
    """
    logdata(request.sid, client_timestamp, request_timestamp, key, value)


@socketio.on('display')
def display_event(json):
    savedata(request.sid, json['cnt'], "display-offset", json['counter'])


@app.route('/demo-sounds/')
def hello_world():
    """
    Demo of using sounds to transmit rotational information between components.
    """
    return render_template('sounds.html')

def closed_loop():
    """
    Closed loop condition with local fictrac client. Part of the `/fdev` route.
    """
    while not start:
        time.sleep(0.1)
    sptmp1 = SpatialTemporal(bar_deg=15, space_deg=105)
    cnd = ClosedLoopCondition(
        spatial_temporal=sptmp1, 
        trial_duration=Duration(60000), 
        gain=-1.0)
    cnd.trigger(socketio)
    socketio.emit('rotate-to', (0, math.radians(-15)))


def log_fictrac_timestamp():
    shared_key = time.time_ns()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.1)
        data = ""
        prevts = 0
        prevfrm = 0
        try:
            sock.bind(( '127.0.0.1', 1717))
            new_data = sock.recv(1)
            data = new_data.decode('UTF-8')
            socketio.emit("meta", (shared_key, "fictrac-connect-ok", 1))
        except: # If Fictrac doesn't exist # FIXME: catch specific exception
            socketio.emit("meta", (shared_key, "fictrac-connect-fail", 0))
            warnings.warn("Fictrac is not running on 127.0.0.1:1717")
            return

        while RUN_FICTRAC:
            new_data = sock.recv(1024)
            if not new_data:
                break
            data += new_data.decode('UTF-8')
            endline = data.find("\n")
            line = data[:endline]
            data = data[endline+1:]
            toks = line.split(", ")
            if (len(toks) < 24) | (toks[0] != "FT"):
                continue # This is not the expected fictrac data package
            cnt = int(toks[1])
            #if cnt-prevfrm > 100:
            socketio.emit("meta", (shared_key, "fictrac-frame", cnt))
            #    prevfrm = cnt



@app.route('/closed-loop/')
def local_fictrac_dev():
    """
    Closed loop condition through the `closed_loop` function and `three-container-bars.html`
        template.
    """
    _ = socketio.start_background_task(target = closed_loop)
    return render_template('three-container-bars.html')


@socketio.on('pong')
def pingpong_time_diff(seq, dttime):
    """
    Calculate time difference between timestamp received via socketIO and the current timestamp.

    :param float dttime: timestamp in ns
    """
    dff = time.time_ns() -dttime
    print(f"{seq}, {dff}", )


def pingpong():
    """
    Send a ping to the client with an attached sequence and a timestamp (in ns). Part of the 
    `/ping` route application.
    """
    seq = 0
    while 1:
        socketio.emit("ping", (seq, time.time_ns()))
        seq = seq + 1
        time.sleep(0.1)


@app.route('/ping/')
def local_ping_dev():
    """
    The function `` sends `ping` messages with an attached timestamp via socket to the 
    client. The client, which has rendered the `ping.html` template, responds to each `ping` 
    with a `pong` and sends the original timestamp back to the server. The function 
    `pingpong_time_diff` receives the socketIO message and calculates the roundtrip time.
    """
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
    repetitions = 3
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

def l4l5left():
    print(time.strftime("%H:%M:%S", time.localtime()))
    block = []
    gains = [0.9, 1, 1.1]
    counter = 0
    gaincount = 0
    log_metadata()

    ## rotation 
    for alpha in [20 5]: #the total duty cycle is also implemented here in alpha
        for speed in [2]:
            for direction in [-1, 1]:
                if speed == 0 and direction == -1:
                    continue
                for clrs in [(107, 147)]:
                    bright = clrs[1]
                    contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                    fg_color = clrs[1] << 8
                    bg_color = clrs[0] << 8
                    rotation_speed = alpha*2*speed*direction
                    t = Trial(
                        counter, 
                        bar_deg=alpha, 
                        space_deg = (40 - alpha),
                        rotate_deg_hz=rotation_speed,
                        pretrial_duration=Duration(250), posttrial_duration=Duration(250),
                        fg_color=fg_color, bg_color=bg_color,
                        comment=f"Rotation alpha {alpha} speed {speed} direction {direction} brightness {bright} contrast {contrast}")
                    block.append(t)
                    counter += 1
    ## progressive / regressive
    #for alpha in [40]:
    #    for speed in [2]:
    #        for direction in [-1, 1]: # Progressive and regressive
    #            for start_deg in [0, 180]: # Left / right
    #                for clrs in [(107, 147)]:
    #                    bright = clrs[1]
    #                    contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
    #                    fg_color = clrs[1] << 8
    #                    bg_color = clrs[0] << 8
    #                    rotation_speed = alpha*2*speed*direction
    #                    t = Trial(
    #                        counter, 
    #                        bar_deg=alpha, 
    #                        rotate_deg_hz=rotation_speed,
    #                        pretrial_duration=Duration(250), posttrial_duration=Duration(250),
    #                        start_mask_deg=start_deg, end_mask_deg=start_deg+180,
    #                        fg_color=fg_color, bg_color=bg_color,
    #                        comment=f"Progressive-Regressive speed {speed} direction {direction} left-right {start_deg} brightness {bright} contrast {contrast}")
                        #block.append(t)
                        #counter = counter + 1
    # dark bar tracking
    #for freq in [0.16, 0.333, 0.666]:
    #    for direction in [-1, 1]:
    #        for clrs in [(102, 152), (64, 190), (0, 254)]:
    #            bright = clrs[1]
    #            contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
    #            fg_color = clrs[1] << 8
    #            bg_color = clrs[0] << 8
    #            t = Trial(
    #                counter, 
    #                bar_deg=345, space_deg=15, 
    #                osc_freq=freq, osc_width=90*direction,
    #                pretrial_duration=Duration(250), posttrial_duration=Duration(250),
    #                fg_color=fg_color, bg_color=bg_color,
    #                comment=f"Oscillation with frequency {freq} direction {direction} brightness {bright} contrast {contrast}")
    #            block.append(t)
    #            counter = counter + 1

    while not start:
        time.sleep(0.1)
    global RUN_FICTRAC
    RUN_FICTRAC = True
    _ = socketio.start_background_task(target = log_fictrac_timestamp)

    repetitions = 3
    counter = 0
    opening_black_screen = Duration(100)
    opening_black_screen.trigger_delay(socketio)
    for i in range(repetitions):
        socketio.emit("meta", (time.time_ns(), "block-repetition", i))
        block = random.sample(block, k=len(block))
        for current_trial in block:
            counter = counter + 1
            print(f"Condition {counter} of {len(block*repetitions)}")
            current_trial.set_id(counter)
            current_trial.trigger(socketio)

    RUN_FICTRAC = False
    print(time.strftime("%H:%M:%S", time.localtime()))

def l4l5right():
    pass
    # while not start:
    #     time.sleep(0.1)
    # #cond1.trigger(socketio)

@app.route('/l4l5left/')
def local_l4l5_left():
    _ = socketio.start_background_task(target=l4l5left)
    return render_template('l4l5left.html')

@app.route('/l4l5right/')
def local_l4l5_right():
    _ = socketio.start_background_task(target=l4l5right)
    return render_template('l4l5right.html')

@app.route('/open-loop/')
def local_experiment_dev():
    """
    Runs function `localexperiment` for the route `/edev` in a background task and deliver the
    three-container-bars.html template.
    """
    print("Starting edev")
    _ = socketio.start_background_task(target = localexperiment)
    return render_template('three-container-bars.html')


def log_metadata():
    """
    The content of the `metadata` dictionary gets logged.
    
    This is a rudimentary way to save information related to the experiment to a file. Edit the 
    content of the dictionary for each experiment.

    TODO: Editing code to store information is not good. Needs to change.
    """
    metadata = {
        "fly-strain": "ctr-merry-Ri",
        "fly-batch": "x3",
        "day-night-since": "2022-04-05",

        "birth-start": "2022-04-16 16:30:00",
        "birth-end": "2022-04-17 13:30:00",

        "starvation-start": "2022-04-19 12:09:00",

        "tether-start": "2022-04-19 16:28:00",
        "fly": 7,
        "tether-end"  : "2022-04-19 16:41:00",
        "sex": "f",
        
        "day-start": "1:00:00",
        "day-end": "17:00:00",
        

        "ball": "25",
        "air": "wall",
        "glue": "KOA",
        
        "temperature": 32,
        "distance": 35,
        "protocol": 3,
        "screen-brightness": 67,
        "display": "fire",
        "color": "#00FF00",
        "filter": "trace-paper",
    }
    shared_key = time.time_ns()
    for key, value in metadata.items():
        logdata(1, 0, shared_key, key, value)


@app.route("/")
def sitemap():
    """ List all routes and associated functions that FlyFlix currently supports. """
    links = []
    for rule in app.url_map.iter_rules():
        #breakpoint()
        if len(rule.defaults or '') >= len(rule.arguments or ''):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            desc = inspect.getdoc(eval(rule.endpoint))
            links.append((url, rule.endpoint, desc))
    return render_template("sitemap.html", links=links)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port = 17000)
