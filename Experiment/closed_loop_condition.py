"""Closed loop condition, implementing direct feedback from FicTrac"""

import warnings
import time
import socket

from Experiment import Duration

class ClosedLoopCondition():

    """ Description of closed loop condition """

    def __init__(
        self,
        spatial_temporal=None, trial_duration=None,
        gain=1.0, fps=60,
        pretrial_duration=Duration(500), posttrial_duration=Duration(500)) -> None:
        """
        Initialize the closed loop condition.

        :param SpatialTemporal spatial_temporal: spatial and temporal definition of the stimulus
        :param Duration trial_duration: duration of the trial
        :param float gain: multiplier for factor to be multiplied with rotational angle received
            from FicTrac.
        :param float fps: frame rate for client
        :param Duration pretrial_duration: duration of the pre-trial period, when stimulus is
            shown but not animated.
        :param Duration posttrial_duration: duration of the post-trial period.
        :rtype: None
        """

        if spatial_temporal is None:
            warnings.warn("Spatial Temporal not set")
        if trial_duration is None:
            warnings.warn("Duration not set")
        if fps <=0 or fps > 60:
            warnings.warn(f"fps ({fps}) outside meaningful constraints")
        self.spatial_temporal = spatial_temporal
        self.trial_duration = trial_duration
        self.gain = gain
        self.fps = fps
        self.pretrial_duration = pretrial_duration
        self.posttrial_duration = posttrial_duration
        self.is_triggering = False

    def trigger(self, socket_io) -> None:
        """
        Trigger the closed loop condition. Once the ClosedLoopCondition is triggered, the server
        sends updates via the socket specified in `socket_io` and receives updates through the
        same channel.

        Specifically, it sends the required FPS and the setup of the screen by triggering the
        current SpatialTemporal object. This is followed by a delay specified in the
        `pretrial_duration`. Then a another thread attempts to connec to the local FicTrac  (see
        `loop`) and does that for the length of `trial_duration`. At the end the pattern is
        stopped and held at the current position for the duration of `posttrial_duration`.

        The log file contains a `closedloop-start` and a `closedloop-end` with the same timestamp
        (in nanoseconds) at the beginning and the end of the trial.

        :param socket socket_io: The Socket.IO used for communicating with the client.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit("meta", (shared_key, "closedloop-start", 1))
        self.trigger_fps(socket_io)
        self.spatial_temporal.trigger_spatial(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.spatial_temporal.trigger_closedloop_start_position(socket_io)
        self.pretrial_duration.trigger_delay(socket_io)
        self.is_triggering = True
        loopthread = socket_io.start_background_task(self.loop, socket_io)
        self.trial_duration.trigger_delay(socket_io)
        self.is_triggering = False
        loopthread.join()
        self.spatial_temporal.trigger_stop(socket_io)
        self.posttrial_duration.trigger_delay(socket_io)
        socket_io.emit("meta", (shared_key, "closedloop-end", 1))

    def trigger_fps(self, socket_io) -> None:
        """
        Trigger sending the FPS via `socket_io`.

        :param socket socket_io: The Socket.IO used for communicating with the client.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('fps', (shared_key, self.fps))

    def loop(self, socket_io):
        """
        Connect to the local FicTrac, extract the relevant rotational information and forward it
        to the client via `socket_io`.

        For the ClosedLoopCondition to work, Fictrac needs to run locally and has a socket
        communication enabled on port 1717. To achieve this, change `sock_host` to `127.0.0.1`
        and `sock_port` to `1717` in the FicTrac configuration.

        This method reads the 17th column from the FicTrac data, which is the "integrated animal
        heading" and calculates the rotation speed considering the time difference to the previous
        sample. This rotation speed in radians per second is then sent via `socket_io`.

        :param socket socket_io: The Socket.IO used for communicating with the client.
        :rtype: None
        """
        shared_key = time.time_ns()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.1)
            prevheading = None
            prevts = None
            data = ""
            try:
                sock.bind(( '127.0.0.1', 1717))
                new_data = sock.recv(1)
                data = new_data.decode('UTF-8')
                socket_io.emit("meta", (shared_key, "fictrac-connect-ok", 1))
            except: # If Fictrac doesn't exist # FIXME: catch specific exception
                socket_io.emit("meta", (shared_key, "fictrac-connect-fail", 0))
                warnings.warn("Fictrac is not running on 127.0.0.1:1717")
                return

            while self.is_triggering:
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
                heading = float(toks[17])
                timestamp = float(toks[22])
                if prevheading:
                    updateval = (heading-prevheading)/((timestamp-prevts)/1000)
                    socket_io.emit('speed', (cnt, updateval * self.gain))
                prevheading = heading
                prevts = timestamp

        socket_io.emit("meta", (shared_key, "fictrac-disconnect-ok", 1))
