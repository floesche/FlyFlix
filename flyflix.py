#!/bin/env python

import socket
import time
import logging
import random
import inspect
import warnings
import json
import netifaces
from threading import Lock


from pathlib import Path
from logging import FileHandler

import yaml
import datetime


import eventlet



from flask import Flask, render_template, request, url_for
from flask.logging import default_handler
from flask_socketio import SocketIO

from engineio.payload import Payload

from Experiment import Duration, Trial, CsvFormatter

app = Flask(__name__)

start = False
SWEEPCOUNTERREACHED = False
RUN_FICTRAC = False

# metadata variable - DO NOT CHANGE
# use control panel to update values or defaultsconfig.yaml to set defaults
metadata = {}
metadata_lock = Lock()

Payload.max_decode_packets = 1500

# metadata variable - DO NOT CHANGE
# use control panel to update values or defaultsconfig.yaml to set defaults
metadata = {}
metadata_lock = Lock()


# Using eventlet breaks UDP reading thread unless patched.
# See http://eventlet.net/doc/basic_usage.html?highlight=monkey_patch#patching-functions for more.
# Alternatively disable eventlet and use development libraries via
# `socketio = SocketIO(app, async_mode='threading')`

eventlet.monkey_patch()
# socketio = SocketIO(app)
# FIXME: find out if CORS is needed
socketio = SocketIO(app, cors_allowed_origins='*')

# socketio = SocketIO(app, async_mode='threading')

def read_metadata():
    """
    read metadata values from a config file
    """
    global metadata
    # read in defaults from defaultsconfig.yaml
    with open("defaultsconfig.yaml", "r") as stream:
        try:
            filedata = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    with metadata_lock:
        metadata = data_as_string(filedata)

def data_as_string(dictionary):
    """
    reformats the data so that dates are saved as strings in ISO format

    Parameters:
    -----------
    dictionary: dict
        The datetimes in this dictionary will be replaced with strings.

    Returns:
    --------
        dictionary without datetime data types
    """
    del_key = []
    f_pairs = {}
    for key in dictionary:
        val = dictionary[key]
        key_type = type(key)
        val_type = type(dictionary[key])
        if (val_type == datetime.date or val_type == datetime.datetime or val_type == datetime.time):
            val = val.isoformat()
            dictionary[key] = val
        elif (val == None):
            dictionary[key] = ""
        if (key_type == datetime.date or key_type == datetime.datetime or key_type == datetime.time):
            key_f = key.isoformat()
            f_pairs[key_f] = val
            del_key.append(key)

    #deletes all keys in datetime format
    for key in del_key:
        del dictionary[key]

    #adds keys that were reformatted to ISO
    dictionary.update(f_pairs)

    return dictionary

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
    read_metadata()
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


@socketio.on('stop-pressed')
def trigger_stop(empty):
    socketio.emit('stop-triggered', empty)

@socketio.on('start-pressed')
def trigger_start(empty):
    socketio.emit('start-triggered', empty)
    #socketio.broadcast.emit('start-triggered', num)
    #print("recieved by flyflix")

@socketio.on('restart-pressed')
def trigger_restart(empty):
    socketio.emit('condition-update', "Once the experiment is started, status will be shown here.")
    socketio.emit('restart-triggered', empty)
    
@socketio.on('manual-restart')
def manual_restart(empty):
    print('manually restarted - recieved')
    socketio.emit('condition-update', "Once the experiment is started, status will be shown here.")


@socketio.on('start-experiment')
def finally_start(number):
    """
    When the server receives a `start-experiment` message via SocketIO, the global variable start
    is set to true

    :param number: TODO find out what it does
    """
    # FIXME: bad practice. Will break at some point
    print("Started at {}".format(time.strftime("%Y%m%d_%H%M%S")))
    global start
    start = True
    socketio.emit('experiment-started')


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
def display_event(data):
    savedata(request.sid, data['cnt'], "display-offset", data['counter'])


@socketio.on('stop-pressed')
def trigger_stop(empty):
    socketio.emit('stop-triggered', empty)
    print("Stopped")
    global start
    start = False


@socketio.on('start-pressed')
def trigger_start(empty):
    socketio.emit('start-triggered', empty)
    #socketio.broadcast.emit('start-triggered', num)
    #print("recieved by flyflix")

@socketio.on('restart-pressed')
def trigger_restart(empty):
    socketio.emit('restart-triggered', empty)


def log_fictrac_timestamp():
    shared_key = time.time_ns()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(0.1)
        data = ""
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


def proto_optomotor_4dir():
    print(time.strftime("%H:%M:%S", time.localtime()))
    block = []
    counter = 0

    ## rotation
    for alpha in [20]:
        for speed in [4]:
            for updown in [False, True]:
                for direction in [-1, 1]:
                    for clrs in [(0, 255)]:
                        bright = clrs[1]
                        contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                        fg_color = clrs[1] << 8
                        bg_color = clrs[0] << 8
                        rotation_speed = alpha*2*speed*direction
                        trial = Trial(
                            counter,
                            bar_deg=alpha,
                            rotate_deg_hz=rotation_speed,
                            openloop_duration=Duration(5000),
                            pretrial_duration=Duration(0), posttrial_duration=Duration(0),
                            fg_color=fg_color, bg_color=bg_color,
                            flip_camera=updown,
                            comment=f"Rotation alpha {alpha} speed {speed} direction {direction} brightness {bright} contrast {contrast} updown {updown}")
                        block.append(trial)
                        counter += 1

    while not start:
        time.sleep(0.1)
    global RUN_FICTRAC
    RUN_FICTRAC = True
    log_metadata()
    _ = socketio.start_background_task(target = log_fictrac_timestamp)

    repetitions = 4
    counter = 0
    opening_black_screen = Duration(100)
    opening_black_screen.trigger_delay(socketio)
    for i in range(repetitions):
        socketio.emit("meta", (time.time_ns(), "block-repetition", i))
        #block = random.sample(block, k=len(block))
        for current_trial in block:
            counter = counter + 1
            progress = f"Condition {counter} of {len(block*repetitions)}"
            print(progress)
            socketio.emit("condition-update", progress)
            current_trial.set_id(counter)
            current_trial.trigger(socketio)
            if not start:
                return

    RUN_FICTRAC = False
    socketio.emit("condition-update", "Completed")
    print(time.strftime("%H:%M:%S", time.localtime()))

def proto_grating():
    print(time.strftime("%H:%M:%S", time.localtime()))
    block = []
    counter = 0

    ## rotation
    for alpha in [22.5, 45]:
        for speed in [2, 4, 8]:
            for clrs in [(0, 255)]:
                for colorshift  in [8, 0]:
                    for direction in [-1, 1]:
                        bright = clrs[1]
                        contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                        fg_color = clrs[1] << colorshift
                        bg_color = clrs[0] << colorshift
                        rotation_speed = alpha*2*speed*direction
                        trial = Trial(
                            counter,
                            bar_deg=alpha,
                            rotate_deg_hz=rotation_speed,
                            openloop_duration=Duration(5000),
                            pretrial_duration=Duration(0), posttrial_duration=Duration(0),
                            fg_color=fg_color, bg_color=bg_color,
                            comment=f"Rotation alpha {alpha} speed {speed} direction {direction} brightness {bright} contrast {contrast}")
                        block.append(trial)
                        counter += 1

    while not start:
        time.sleep(0.1)
    global RUN_FICTRAC
    RUN_FICTRAC = True
    log_metadata()
    _ = socketio.start_background_task(target = log_fictrac_timestamp)

    repetitions = 2
    counter = 0
    opening_black_screen = Duration(100)
    opening_black_screen.trigger_delay(socketio)
    for i in range(repetitions):
        socketio.emit("meta", (time.time_ns(), "block-repetition", i))
        #block = random.sample(block, k=len(block))
        for current_trial in block:
            counter = counter + 1
            progress = f"Condition {counter} of {len(block*repetitions)}"
            print(progress)
            socketio.emit("condition-update", progress)
            current_trial.set_id(counter)
            current_trial.trigger(socketio)
            if not start:
                return

    RUN_FICTRAC = False
    socketio.emit("condition-update", "Completed")
    print(time.strftime("%H:%M:%S", time.localtime()))


def proto_smallfield():
    print(time.strftime("%H:%M:%S", time.localtime()))
    block = []
    counter = 0

    # ## rotation
    for alpha in [15]:
        for speed in [2, 3, 6, 12]:
            for counter in range(3):
                for direction in [-1, 1]:
                    for clrs in [(255, 0)]:
                        bright = clrs[1]
                        contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                        fg_color = clrs[1] << 8
                        bg_color = clrs[0] << 8
                        rotation_speed = alpha*2*speed*direction
                        trial = Trial(
                            counter,
                            bar_deg=alpha,
                            space_deg=360-alpha,
                            sweep=1, openloop_duration=None,
                            rotate_deg_hz=rotation_speed,
                            pretrial_duration=Duration(0), posttrial_duration=Duration(0),
                            fg_color=fg_color, bg_color=bg_color,
                            comment=f"Sweep alpha {alpha} speed {speed} direction {direction} brightness {bright} contrast {contrast}")
                        block.append(trial)
                        counter += 1


    # Small object
    for alpha in [15]:
        for speed in [2, 3, 6, 12]:
            for clrs in [(255, 0)]:
                for counter in range(3):
                    for direction in [-1, 1]:
                        bright = clrs[1]
                        contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                        fg_color = clrs[1] << 8
                        bg_color = clrs[0] << 8
                        rotation_speed = alpha*2*speed*direction
                        trial = Trial(
                            counter,
                            bar_deg=alpha, space_deg=360-alpha,
                            sweep=1, openloop_duration=None,
                            rotate_deg_hz=rotation_speed,
                            pretrial_duration=Duration(0), posttrial_duration=Duration(0),
                            fg_color=fg_color, bg_color=bg_color,
                            bar_height=0.03,
                            comment=f"Object alpha {alpha} speed {speed} direction {direction} brightness {bright} contrast {contrast}")
                        block.append(trial)
                        counter += 1

    while not start:
        time.sleep(0.1)
    global RUN_FICTRAC
    RUN_FICTRAC = True
    log_metadata()
    _ = socketio.start_background_task(target = log_fictrac_timestamp)

    repetitions = 4
    counter = 0
    opening_black_screen = Duration(100)
    opening_black_screen.trigger_delay(socketio)
    for i in range(repetitions):
        socketio.emit("meta", (time.time_ns(), "block-repetition", i))
        #block = random.sample(block, k=len(block))
        for current_trial in block:
            counter = counter + 1
            progress = f"Condition {counter} of {len(block*repetitions)}"
            print(progress)
            socketio.emit("condition-update", progress)
            current_trial.set_id(counter)
            current_trial.trigger(socketio)
            if not start:
                return

    RUN_FICTRAC = False
    socketio.emit("condition-update", "Completed")
    print(time.strftime("%H:%M:%S", time.localtime()))


def proto_cshlfly22():
    print(time.strftime("%H:%M:%S", time.localtime()))
    block = []
    counter = 0

    ## rotation
    for alpha in [15]:
        for speed in [4, 8]:
            for direction in [-1, 1]:
                for clrs in [(64, 190)]:
                    bright = clrs[1]
                    contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                    fg_color = clrs[1] << 8
                    bg_color = clrs[0] << 8
                    rotation_speed = alpha*2*speed*direction
                    trial = Trial(
                        counter,
                        bar_deg=alpha,
                        rotate_deg_hz=rotation_speed,
                        pretrial_duration=Duration(250), posttrial_duration=Duration(250),
                        fg_color=fg_color, bg_color=bg_color,
                        comment=f"Rotation alpha {alpha} speed {speed} direction {direction} brightness {bright} contrast {contrast}")
                    block.append(trial)
                    counter += 1

    # Oscillation
    for alpha in [15]:
        for freq in [0.333]:
            for direction in [-1, 1]:
                for clrs in [(190, 64)]:
                    bright = clrs[1]
                    contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                    fg_color = clrs[1] << 8
                    bg_color = clrs[0] << 8
                    trial = Trial(
                        counter,
                        bar_deg=alpha,
                        osc_freq=freq, osc_width=90*direction,
                        pretrial_duration=Duration(250), posttrial_duration=Duration(250),
                        fg_color=fg_color, bg_color=bg_color,
                        #bar_height=0.04,
                        comment=f"Oscillation with frequency {freq} direction {direction} brightness {bright} contrast {contrast}")
                    block.append(trial)
                    counter += 1



    # Small object
    for alpha in [10]:
        for speed in [2, 4]:
            for direction in [-1, 1]:
                for clrs in [(190, 64)]:
                    bright = clrs[1]
                    contrast = round((clrs[1]-clrs[0])/(clrs[1]+clrs[0]), 1)
                    fg_color = clrs[1] << 8
                    bg_color = clrs[0] << 8
                    rotation_speed = alpha*2*speed*direction
                    trial = Trial(
                        counter,
                        bar_deg=alpha, space_deg=180-alpha,
                        rotate_deg_hz=rotation_speed,
                        pretrial_duration=Duration(250), posttrial_duration=Duration(250),
                        fg_color=fg_color, bg_color=bg_color,
                        bar_height=0.03,
                        comment=f"Object alpha {alpha} speed {speed} direction {direction} brightness {bright} contrast {contrast}")
                    block.append(trial)
                    counter += 1

    while not start:
        time.sleep(0.1)
    global RUN_FICTRAC
    RUN_FICTRAC = True
    log_metadata()
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
            progress = f"Condition {counter} of {len(block*repetitions)}"
            print(progress)
            socketio.emit("condition-update", progress)
            current_trial.set_id(counter)
            current_trial.trigger(socketio)
            if not start:
                return

    RUN_FICTRAC = False
    socketio.emit("condition-update", "Completed")
    print(time.strftime("%H:%M:%S", time.localtime()))


@app.route('/control-panel/')
def control_panel():
    """
    Control panel for experiments.
    """
    return render_template('control-panel.html', metadata=json.dumps(metadata))


@app.route('/optomotor_4-directions/')
def optomotor_4dir():
    """
    Short protocol with optomotor responses moving into four different directions. (~0:50)
    """
    _ = socketio.start_background_task(target=proto_optomotor_4dir)
    return render_template('cshlfly.html')

@app.route('/grating/')
def grating():
    """
    Protocol with different contrasts, bar widths, and movement speed (~7:00)
    """
    _ = socketio.start_background_task(target=proto_grating)
    return render_template('cshlfly.html')


@app.route('/smallfield/')
def smallfield():
    """
    Small field stimuli: first a 15° dark bar and then a small square moves 3× left/rigth at 4 different velocities (~4:30)
    """
    _ = socketio.start_background_task(target=proto_smallfield)
    return render_template('cshlfly.html')


@app.route('/cshlfly22/')
def cshfly22():
    """
    An example protocol from CSHL 2022
    """
    _ = socketio.start_background_task(target=proto_cshlfly22)
    return render_template('cshlfly.html')


@socketio.on('metadata-submit')
def handle_data(data):
    """
    Triggered when metadata is submitted via the control panel
    takes the javascript objects and converts it to a python dictionary
    stores the dictionary in the metadata variable that is used in log_metadata()
    """
    metadata_string = json.dumps(data)
    global metadata
    with metadata_lock:
        metadata.update(json.loads(metadata_string))


@socketio.on('metadata-submit')
def handle_data(data):
    """
    Triggered when metadata is submitted via the control panel
    takes the javascript objects and converts it to a python dictionary
    stores the dictionary in the metadata variable that is used in log_metadata()
    """
    metadata_string = json.dumps(data)
    print(metadata_string)
    global metadata
    metadata.update(json.loads(metadata_string))
    print(metadata)



def log_metadata():
    """
    The content of the `metadata` dictionary gets logged.

    This is a rudimentary way to save information related to the experiment to a file. Edit the
    content of the dictionary for each experiment.
    """
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


def print_ip(port=17000):
    for iface in netifaces.interfaces():
        iface_details = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in iface_details:
            for ip_interfaces in iface_details[netifaces.AF_INET]:
                for key, ip_add in ip_interfaces.items():
                    if key == 'addr' and ip_add != '127.0.0.1':
                        print(f"FlyFlix is available at http://{ip_add}:{port}")

if __name__ == '__main__':
    before_first_request()
    port=17000
    print_ip(port=port)
    socketio.run(app, host='0.0.0.0', port=port)
