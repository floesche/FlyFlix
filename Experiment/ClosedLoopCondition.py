"""Closed loop condition, implementing direct feedback from FicTrac"""
import warnings
import time
import socket

from .Duration import Duration

class ClosedLoopCondition():

    def __init__(
        self,
        spatial_temporal=None, trial_duration=None,
        gain=1.0, fps=60,
        pretrial_duration=Duration(500), posttrial_duration=Duration(500)) -> None:

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

    def trigger(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit("meta", (shared_key, "closedloop-start", 1))
        self.trigger_fps(socket_io)
        self.spatial_temporal.triggerSpatial(socket_io)
        self.spatial_temporal.triggerStop(socket_io)
        self.spatial_temporal.triggerClosedStartPosition(socket_io)
        self.pretrial_duration.triggerDelay(socket_io)
        self.is_triggering = True
        loopthread = socket_io.start_background_task(self.loop, socket_io)
        self.trial_duration.triggerDelay(socket_io)
        self.is_triggering = False
        loopthread.join()
        self.spatial_temporal.triggerStop(socket_io)
        self.posttrial_duration.triggerDelay(socket_io)
        socket_io.emit("meta", (shared_key, "closedloop-start", 1))

    def trigger_fps(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit('fps', (shared_key, self.fps))

    def loop(self, socket_io):
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
            except: # If Fictrac doesn't exist #FIXME: catch specific exception
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
