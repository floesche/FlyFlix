# FlyFlix Development Guide

This guide serves as a basic introduction to developing with FlyFlix. It wil cover the main structure as well as the most important files.

## File Overview

### `flyflix.py`

This is the main file that the server is hosted on. It handles the majority of communication with clients through [Socket.IO](https://socket.io/) events. Socket.IO is a library using the [WebSocket](https://en.wikipedia.org/wiki/WebSocket) standard or, if not available, falls back on HTTP polling.

Socket.IO provides a bidirectional low-latency event-based communication channel between server and client. For example, when the server recieves the event 'start-pressed' from one of the clients, it emits the event `start-triggered`. This event is then read by a client in `experiment_control.js`, which triggers some action to start the stimulus movement.

The file `flyFlix.py` also handles routing to the different websites that FlyFlix provides. For example, it reads the `control-panel.html` template, fills in the variables, and sends the final HTML website to the client's web browser. For experiment pages, `flyflix.py` starts a background function that stays alive during the experiment.

### `arena.js`

The `Arena` class in [`static/arena/arena.js`](static/arena/arena.js) defines the virtual environment that the experiment takes place in. This includes the creation of the `camera`, `scene`, `renderer`, and `loop`. These are all [three.js](https://threejs.org/) components to handle 3D rendering. `Arena` also creates any additional classes used in the experiment like the `Panels` class in [`static/arena/components/panels.js`](static/arena/components/panels.js) (used for [bar stimuli](stimulus-descriptions.md#bars)) or the `Spheres` class in [`static/arena/components/spheres.js`](static/arena/components/spheres.js) in the `starfield` branch (used for [starfield stimuli](stimulus-descriptions.md#starfield)).

### trial.py

The `Trial` class in [`Experiment/trial.py`](Experiment/trial.py) is used to define each trial in an experiment. A trial consists of an open loop and closed loop condition. The trial class is compatible with all types of stimulus, however each type has its own parameters to trigger it's use. It also creates the spatial-temporal descriptions of each trial that are used to create the open and closed loop conditions. When a trial is triggered through `trigger()`, it starts the trial through calling methods in `open_loop_condition.py` and `closed_loop_condition.py`. For more information, look at the documentation within `trial.py`.

### data_exchanger.js

The data exchanger class handles communication between the spatial temporal classes (like `spatial_temporal.py` or `starfield_spatial_temporal.py` in the starfield branch) and the stimulus classes (like `panels.js` or `starfield.js`) through [Flask-SocketIO](https://pypi.org/project/Flask-SocketIO/) events. The `DataExchanger` waits for events (that were emitted by the spatial temporal class) and then calls stimulus methods accordingly. For example, the event `spatial-setup` or `panels-spatial-setup` results in `panels.changePanels(barWidth, spaceWidth, fgColor, bgColor, barHeight)` being called. Here is an example of one of these event handlers for setting the speed of panels for a vertical bar trial:

```javascript
/**
 * Event handler for `speed` sets rotational speed and loop ID for the panels object.
 * 
 * @param {bigint} lid - Loop ID
 * @param {number} speed - set rotational speed for panels in radians per second
 */
 this.socket.on('speed', (lid, speed) => {
    panels.setLid(lid);
    panels.setRotateRadHz(speed);
    this.log(lid, 'de-panel-speed', speed);
 });
``` 

### control-panel.html

This is the template file for the control panel. The control panel serves as a remote operating system that can start/stop experiments, update trial data, and give the user status updates about the experiment. It uses socket to communicate with `flyflix.py` for all of these features.

## How to guides

### Implementing Existing Stimulus / Creating New Experiments

Implementing existing stimulus in FlyFlix is simpler than creating new stimulus. The only file that you will need to edit is `flyflix.py` and you will create 2 new files.

In order to implement existing stimulus, follow these steps:

1. Create a new javascript file in the static folder that creates the arena as well as the experiment buttons. The following code can be used as a template and does not require any changes:

```javascript

import { Arena } from './arena/arena.js';

import { FullScreener } from './arena/systems/full_screener.js';
import { ExperimentControl } from './arena/systems/experiment_control.js';

/**
 * Create the experiment in the client, inside the HTML-ID `scene-container`.
 */

var socket = io();


function main() {
    const container = document.querySelector('#scene-container');
  
    const arena = new Arena(container, 310);

    const fullScreenButton = new FullScreener(container);
    const experimentController = new ExperimentControl(container, socket);
    
    arena.start();

    socket.on('stop-triggered', function(empty){
      arena.stop();
    })
}

main();

```
2. Create a new html file in templates that uses the previously created file for the script. The following is a template for this file:

```html
<!DOCTYPE html>
<html>
  <head>
    {# example-template.html #}
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset="utf-8">
    <title>FlyFlix | Three.JS Scene Container</title>
    <link href="/static/style/bars.css" rel="stylesheet" type="text/css">
    <script src="/static/vendor/socket.io.min.js"></script>
    <script type="module" src="/static/example_static_file.js"></script>
  </head>
  <body>
    <div id="scene-container"></div>
  </body>
</html>
```

3. Create a new page in `flyflix.py` that returns the template file and starts a background task which is a function in `flyflix.py`. An example on how to do this is:

```javascript
@app.route('/example-experiment/')
def local_example_experiment():
    """
    An example experiment
    """
    _ = socketio.start_background_task(target=example_experiment)
    return render_template('example-template.html')
```

4. Create the function that was set as the background task for the experiment. All trials will be created and triggered in this function. To create trials, look at the documentation within `trial.py` to determine what variables need to be set for the type of stimulus you are using. There are more options for stimulus and better documentation within the starfield branch. Follow the following format for the function:

```python
def example_experiment():
    print(time.strftime("%H:%M:%S", time.localtime()))
    block = []
    counter = 0

    ## create trials, usually this is done using for loops with different variables
    trial = Trial(
        #enter parameters here    
    )
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
```

### Implementing New Stimulus

In order to implement new stimulus, follow these steps:

1. Create a new class in components that defines your stimulus. Examples of these classes that already exist are `panels.js` and `spheres.js` (in the starfield branch). The stimulus will need to be made using [three.js](https://threejs.org/) systems and imported accordingly. In addition to the constructor, the class will need _setup method in which the [three.js](https://threejs.org/) object meshes will be created. This is necessary because the same object will need to be updated for each trial so it is easier to have one method to set up each trial. You will also need to create a `changeClassName` method that clears the object and calls setup again with the new parameters. Another crucial method to include is the `tick()` method. The `tick()` method is used to animate the class and should trigger movement based on the time interval since last tick. For additional methods and guidance, I reccommend looking at the `panels.js` class and creating a counterpart for all methods there as well as any additional methods you want for your stimulus.

2. Create a class that describes the spatial and temporal stimulation and update `data_exchanger.js` as you create diffrent methods. To do this it is easiest to model the class after the vertical bar stimulus' `spatial_temporal.py` class. The spatial temporal class will emit different socket events that will be recieved by the `data_exchanger` which will in turn call methods of the stimulus class in components. For example, when `SpatialTemporal.trigger_rotation(socket)` is called, the `SpatialTemporal` class emits the `speed` or `panels-speed` event along with a speed. This event is then recieved by the data exchanger and calls `panels.setRotateRadHz(speed)`. The data exchanger class is the only class that calls methods in the stimulus classes like `panels.js` or `spheres.js`. The spatial temporal class you create should emit events that trigger these changes. Make sure that each type of stimulus has unique event names to avoid errors or triggering multiple types of trials at once.

3. Update the Trial class (`trial.py`). First, add new parameters that will be needed to initialize the 2 classes you created previously. Second, if the Trial class is created with those parameters, create a spatial temporal object with those parameters. This will then be used to create `open_loop_condition.py` and `closed_loop_condition.py`. These classes may need altered based on the needs of your stimulus (closed loop almost definetely will need updated). These conditions should then be added to `self.conditions` which is iterated through in the `trigger()` method.

4. Update the `arena.js` class to import and initialize your stimulus class, add it to the scene, add it to `loop.updateables`, set `loggable` to `io`, and add it to the `DataExchanger` constructor.

5. From there, follow instructions in the Implementing Existing Stimulus Guide to add it in an experiment.

Additional information: In most branches of FlyFlix, vertical bars/panels are the only type of stimulus. Currently, only the starfield branch implements a second type. It may be helpful to work extending off of the starfield branch when implementing more stimulus for additional documentation and comparison.