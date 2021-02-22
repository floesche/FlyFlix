import warnings
import time
import socket


class ClosedLoopCondition():

    def __init__(self, spatialTemporal=None, trialDuration=None, gain=1.0, fps=60, preTrialDuration=Duration(500), postTrialDuration=Duration(500)) -> None:
        if spatialTemporal is None:
            warnings.warn("Spatial Temporal not set")
        if trialDuration is None:
            warnings.warn("Duration not set")
        if fps <=0 or fps > 60:
            warnings.warn(f"fps ({fps}) outside meaningful constraints")
        self.spatialTemporal = spatialTemporal
        self.trialDuration = trialDuration
        self.gain = gain
        self.fps = fps
        self.preTrialDuration = preTrialDuration
        self.postTrialDuration = postTrialDuration
        self.isTriggering = False

    def trigger(self, io):
        self.triggerFPS(io)
        self.spatialTemporal.triggerSpatial(io)
        self.spatialTemporal.triggerStop(io)
        self.spatialTemporal.triggerClosedStartPosition(io)
        self.preTrialDuration.triggerDelay(io)
        self.isTriggering = True
        loopthread = io.start_background_task(self.loop, io)
        self.trialDuration.triggerDelay(io)
        self.isTriggering = False
        self.spatialTemporal.triggerStop(io)
        self.postTrialDuration.triggerDelay(io)

    def triggerFPS(self, io):
        sharedKey = time.time_ns()
        io.emit('fps', (sharedKey, self.fps))

    def loop(self, io):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.1)
            prevheading = None
            data = ""
            try:
                sock.bind(( '127.0.0.1', 1717))
                new_data = sock.recv(1)
                data = new_data.decode('UTF-8')
            except: # If Fictrac doesn't exist
                warnings.warn("Fictrac is not running on 127.0.0.1:1717")
                return

            while self.isTriggering:
                new_data = sock.recv(1024)
                if not new_data:
                    break
                data += new_data.decode('UTF-8')
                endline = data.find("\n")
                line = data[:endline]
                data = data[endline+1:]
                toks = line.split(", ")
                if ((len(toks) < 24) | (toks[0] != "FT")):
                    continue # This is not the expected fictrac data package
                cnt = int(toks[1])
                heading = float(toks[17])
                ts = float(toks[22])
                if prevheading:
                    updateval = (heading-prevheading) #* fictracGain * -1
                    #savedata(ts, "heading", heading)
                    #if self.isTriggering:
                    #savedata(cnt, "fictrac-change-speed", updateval)
                    io.emit('speed', (cnt, updateval * self.gain))
                prevheading = heading
