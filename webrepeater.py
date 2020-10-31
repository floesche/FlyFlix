#!/bin/env python

from flask import Flask, render_template, url_for
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# url_for('static', filename='socket.io.slim.js')

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/playback/')
def playback():
    return render_template('playback.html')

@app.route('/hello/')
def hello():
    return render_template('hello.html')


if __name__ == '__main__':
    socketio.run(app)
