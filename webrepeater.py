#!/bin/env python



from flask import Flask, render_template, url_for, request, abort
from flask_socketio import SocketIO
from jinja2 import TemplateNotFound
from threading import Thread
import socket

app = Flask(__name__)

import eventlet
eventlet.monkey_patch()
# socketio = SocketIO(app, async_mode='threading')
socketio = SocketIO(app)

app.config.update(
    FICTRAC_HOST = '127.0.0.1',
    FICTRAC_PORT = 1717
)

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
            heading = float(toks[17])
            socketio.emit('direction', heading-prevheading)
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
    thread = Thread(target=listenFictrac)
    thread.daemon = True
    thread.start()
    socketio.run(app)
