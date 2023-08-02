# FlyFlix

This repository is a supplement to our publication [An Inexpensive, High-Precision, Modular Spherical Treadmill Setup Optimized for _Drosophila_ Experiments](https://doi.org/10.3389/fnbeh.2021.689573).

Here we will first give a quick introduction [how to use FlyFlix](#usage), followed by a description [how to install FlyFLix](#installation), and finally an [overview about the architecture](#architecture) of FlyFlix.

We also have a [description of the available stimuli](stimulus-descriptions.md) and a brief introduction on how to [get started if you want to modify FlyFlix](getting-started-with-development.md) to your own needs.

## Usage

### Run FlyFlix

Once installed, you should be able to run FlyFlix by executing a python script on the terminal: `python flyflix.py` (on Linux and Mac you can also run `make localhost`, which will also show you your local IP address). Once the application is up and running, the client can be started by pointing a web browser to an URL with the IP address of the server at port `17000` (you can specify the port by appending `:17000` to the address). If you run the browser on the same machine as FlyFlix is running, such as your laptop or your workstation, you can use the address of the localhost and point your browser to <http://127.0.0.1:17000> or <http://localhost:17000>.

If you want to run the client on another device than your FlyFlix server, for example a tablet, a smartphone, or another computer, you will need to find out the IP address of the FlyFlix server – which is shown once you start flyflix.

### Control Panel

Flyflix experiments can be controlled either through the experiment page or remotely if the control panel page is open on another device connected to the same server. The control panel has a buttons to control the experiment, a status bar, and a metadata section. 

The start, stop, and restart buttons on the control panel should only be pressed when the other device is connected to the server and has opened the page of the experiment you intend to run. If the other device has opened an experiment page other than the one you intend on testing, starting the experiment can cause both to run simulaneously; rerun `flyflix` and reconnect to fix this. The status bar will display the current state of the stimulus being shown to the fly. The metadata section contains input fields that are prefilled with the defaultsconfig.yaml data as well as 5 additional empty rows. The prefilled rows can be edited for each experiment, only what is entered in the metadata section will be saved for the experiment. The metadata is saved when the experiment is started so update it before starting the experiment.

### Saving Data

Data about trials can be saved by entering information in the control panel or by editing defaultsconfig.yaml. The defaultsconfig.yaml file sends data to the server in key-value pairs in the following format, key: value. Data is saved as a string unless it matches a different datatype recognized by yaml. If you run into any issues with data being stored as the wrong type, put single or double quotes around it to ensure it is saved as a string. Additionally, any keys without a value in the defaultsconfig file (key: ) will display in the control panel with the empty value highlighted red until the user enters something into the input. Information stored in defaultsconfig.yaml will be stored for all trials and is good for saving information that will be constant across many trials. Any information saved to the trial through the control panel will only be saved for that experiment. If a key in the information about the experiment is repeated in the control panel and/or defaultsconfig.yaml, only the last entered key-value pair from the control panel will be saved under that key.

## Installation

To run the FlyFlix server, a recent version of [python](https://www.python.org/) is required. The server was written in Python-3 and only tested in [Python-3.7](https://devguide.python.org/#status-of-python-branches) and newer (up to Python-3.11.3). The [installation of a recent python interpreter](https://wiki.python.org/moin/BeginnersGuide/Download) or another type of [python distribution](https://www.anaconda.com/products/individual) is outside the scope of this documentation.

Check for the current version of python by running the following command. The result should show a version number > 3.7.0

```sh
python --version
```

To install dependencies, a python package management system compatible with [pip](https://pip.pypa.io/en/stable/) is required. Using a [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment) is encouraged although optional and once again outside the scope of this documentation. In most cases it should be sufficient to run `python -m venv .venv` to create a virtual environment. To activate, run `source .venv/bin/activate` (`.venv\Scripts\activate.bat` or `.venv\Scripts\activate.ps1` if you are on Windows).

The following descriptions assume that pip is used as a package manager and the `pip` script is available in the path. Otherwise load pip as a module, for example by calling `python3 -m pip` followed by the pip command.

The file `requirements.txt` contains the dependencies for FlyFlix. If you have make installed, run `make install-dependencies`, otherwise:

```sh
pip install -r requirements.txt
```

### Upgrade

If you experience issues when running FlyFlix, you might want to upgrade installed packages With `make` installed, you can run `make update-dependencies`, otherwise the following two commands run from the terminal should achieve the same:

```sh
pip install --upgrade pip
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
```

## Architecture

FlyFlix follows the [Client-Server model](https://en.wikipedia.org/wiki/Client%E2%80%93server_model).

FlyFlix' server component is written in python-3 and requires a computer to run. The client is a web application that runs in most modern web browsers. The client is implemented in JavaScript inside an HTML website.

Once the server is started (see Run FlyFlix)[#run-flyflix], FlyFlix shows the IP address the server is running at. The landing page of FlyFlix is a sitemap containing all the possible options for the client.

Through a bidirectional communication server and client exchange status information. Consequently, several clients can connect to the same server. The communication between client and server uses the low-latency library [Socket.IO](https://socket.io/), technology build around the [WebSocket protocol](https://en.wikipedia.org/wiki/WebSocket), for bidirectional communication.

### Server

The server is implemented as a [Flask](https://flask.palletsprojects.com) web application. Flask itself is primarily used to deliver the client application. The server application is responsible for keeping track of the experiment, delivering the visual updates to the client, and data logging. The communication with the client is done through the additional [Flask-SocketIO](https://flask-socketio.readthedocs.io) layer.

The main implementation of the server is done in the `flyflix.py` script. Once this is started, it shows the URL to use for the client.

### Client

The client is implemented as a javascript application inside a HTML website. The application runs in most modern web browsers, although we recommend [Firefox](https://en.wikipedia.org/wiki/Firefox) or [Chromium](https://en.wikipedia.org/wiki/Chromium_(web_browser)), which are available on most platforms from Linux, to iOS, macOS, BSDs, Windows, and Android. The landing page contains a list of client applications, from the "Control-Panel" to the different experimental protcols. For the display(s) that are used for stimulus presentation, select the protocol you want to run. On the experimental computer point the web browser to the [control panel](#control-panel).

The FlyFlix client uses two external libraries, [Socket.IO](https://socket.io/) and [Three.js](https://threejs.org/). Recent versions of both libraries are part of this repository and are locally delivered through the Flask web server. They can be found in the `static/vendor` directory. You might want to check if more recent versions are available since they might improve performance and fix bugs.

An example application that uses the Three.js library is delivered through the `templates/three-container-bars.html` file and implemented in the `static/bars.js` file.
