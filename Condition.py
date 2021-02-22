import warnings
import math
import time
import socket

from datetime import datetime, timedelta


class SpatialTemporal():

    def __init__(self, barDeg=60, spaceDeg=60, rotateDegHz=0) -> None:
        if (barDeg < 0 or spaceDeg <0):
            warnings.war("bar size or space is negative")
        if (360 % (barDeg + spaceDeg) != 0):
            warnings.warn("Spatial pattern is not seamless")
        if (rotateDegHz is None):
            warnings.warn("temporal components needs to be set.")
        self.barDeg = barDeg
        self.spaceDeg = spaceDeg
        self.rotateDegHz = rotateDegHz

    def isBarSweep(self):
        if (self.barDeg<self.spaceDeg and self.barDeg+self.spaceDeg==360):
            return True
        return False

    def isSpaceSweep(self):
        if (self.barDeg>self.spaceDeg and self.barDeg+self.spaceDeg==360):
            return True
        return False

    def getBarSweepDuration(self, sweepAngleDeg=180):
        return ((sweepAngleDeg + 2*self.barDeg) / abs(self.rotateDegHz))*1000

    def getSpaceSweepDuration(self, sweepAngleDeg=180):
        return ((sweepAngleDeg + 2* self.spaceDeg) / abs(self.rotateDegHz)*1000)

    def triggerRotation(self, io):
        sharedKey = time.time_ns()
        io.emit('speed', (sharedKey, math.radians(self.rotateDegHz)))

    def triggerStop(self, io):
        sharedKey = time.time_ns()
        io.emit('speed', (sharedKey, 0))

    def triggerSpatial(self, io):
        sharedKey = time.time_ns()
        io.emit('spatial-setup', (sharedKey, math.radians(self.barDeg), math.radians(self.spaceDeg)))

    def triggerSweepStartPosition(self, io):
        sharedKey = time.time_ns()
        startAngle = 0
        if self.isBarSweep(): 
            if self.rotateDegHz > 0:
                startAngle = 90
            else:
                startAngle = 270+self.barDeg
        elif self.isSpaceSweep(): 
            if self.rotateDegHz > 0:
                startAngle = 90 - self.spaceDeg
            else:
                startAngle = 270
        else:
            warnings.warn("not 2 item pattern. Rotate to 0")
        io.emit('rotate-to', (sharedKey, math.radians(startAngle)))

    def triggerClosedStartPosition(self, io):
        sharedKey = time.time_ns()
        startAngle = 0
        if self.isBarSweep():
            startAngle = 180
        elif self.isSpaceSweep():
            startAngle = 360-self.spaceDeg/2
        else:
            warnings.warn("not 2 item pattern. Rotate to 0")
        io.emit('rotate-to', (sharedKey, math.radians(startAngle)))



class Duration():

    def __init__(self, timeDuration=3000) -> None:
        self.timeDuration = timeDuration

    def triggerDelay(self, io):
        ttime = datetime.now() + timedelta(milliseconds=self.timeDuration)
        while datetime.now() < ttime:
            time.sleep(0.01)


class OpenLoopCondition():

    def __init__(self, spatialTemporal=None, trialDuration=None, fps=60, preTrialDuration=Duration(500), postTrialDuration=Duration(500)) -> None:
        if spatialTemporal is None:
            warnings.warn("Spatial Temporal not set")
        if trialDuration is None:
            warnings.warn("Duration not set")
        if fps <=0 or fps > 60:
            warnings.warn("fps outside meaningful constraints")
        self.spatialTemporal = spatialTemporal
        self.trialDuration = trialDuration
        self.preTrialDuration = preTrialDuration
        self.postTrialDuration = postTrialDuration
        self.fps = fps

    def triggerFPS(self, io):
        sharedKey = time.time_ns()
        io.emit('fps', (sharedKey, self.fps))

    def trigger(self, io):
        self.triggerFPS(io)
        self.spatialTemporal.triggerSpatial(io)
        self.spatialTemporal.triggerStop(io)
        self.preTrialDuration.triggerDelay(io)
        self.spatialTemporal.triggerRotation(io)
        self.trialDuration.triggerDelay(io)
        self.spatialTemporal.triggerStop(io)
        self.postTrialDuration.triggerDelay(io)


class SweepCondition():

    def __init__(self, spatialTemporal=None, sweepCount=1, fps=60, preTrialDuration=Duration(500), postTrialDuration=Duration(500)) -> None:
        if spatialTemporal is None:
            warnings.warn("Spatial Temporal not set")
        if fps <=0 or fps > 60:
            warnings.warn(f"fps ({fps}) outside meaningful constraints")
        self.spatialTemporal = spatialTemporal
        if self.spatialTemporal.isBarSweep():
            self.trialDuration = Duration(self.spatialTemporal.getBarSweepDuration())
            self.isBarSweep = True
        elif self.spatialTemporal.isSpaceSweep():
            self.trialDuration = Duration(self.spatialTemporal.getSpaceSweepDuration())
            self.isBarSweep = False
        self.preTrialDuration = preTrialDuration
        self.postTrialDuration = postTrialDuration
        self.fps = fps

    def triggerFPS(self, io):
        sharedKey = time.time_ns()
        io.emit('fps', (sharedKey, self.fps))

    def trigger(self, io):
        self.triggerFPS(io)
        self.spatialTemporal.triggerSpatial(io)
        self.spatialTemporal.triggerStop(io)
        self.spatialTemporal.triggerSweepStartPosition(io)
        self.preTrialDuration.triggerDelay(io)
        self.spatialTemporal.triggerRotation(io)
        self.trialDuration.triggerDelay(io)
        self.spatialTemporal.triggerStop(io)
        self.postTrialDuration.triggerDelay(io)


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
    
