import warnings
import math
import time

class SpatialTemporal():

    def __init__(self, bar_deg=60, space_deg=60, rotate_deg_hz=0) -> None:
        if (bar_deg < 0 or space_deg <0):
            warnings.war("bar size or space is negative")
        if (360 % (bar_deg + space_deg) != 0):
            warnings.warn(f"Spatial pattern is not seamless with bar {bar_deg}° and space {space_deg}")
        if (rotate_deg_hz is None):
            warnings.warn("temporal components needs to be set.")
        self.bar_deg = bar_deg
        self.space_deg = space_deg
        self.rotate_deg_hz = rotate_deg_hz

    def isBarSweep(self):
        if (self.bar_deg<self.space_deg and self.bar_deg+self.space_deg==360):
            return True
        return False

    def isSpaceSweep(self):
        if (self.bar_deg>self.space_deg and self.bar_deg+self.space_deg==360):
            return True
        return False

    def isOpposingBarSweep(self):
        if (self.bar_deg + self.space_deg == 180):
            return True
        return False

    def getBarSweepDuration(self, sweep_angle_deg=180):
        return ((sweep_angle_deg + 2*self.bar_deg) / abs(self.rotate_deg_hz))*1000

    def getSpaceSweepDuration(self, sweep_angle_deg=180):
        return ((sweep_angle_deg + 2* self.space_deg) / abs(self.rotate_deg_hz)*1000)

    def triggerRotation(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit('speed', (shared_key, math.radians(self.rotate_deg_hz)))

    def triggerStop(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit('speed', (shared_key, 0))

    def triggerSpatial(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit('spatial-setup', (shared_key, math.radians(self.bar_deg), math.radians(self.space_deg)))

    def triggerSweepStartPosition(self, socket_io):
        shared_key = time.time_ns()
        startAngle = 0
        if self.isBarSweep(): 
            if self.rotate_deg_hz > 0:
                startAngle = 90
            else:
                startAngle = 270+self.bar_deg
        elif self.isSpaceSweep(): 
            if self.rotate_deg_hz > 0:
                startAngle = 90 - self.space_deg
            else:
                startAngle = 270
        else:
            warnings.warn("not 2 item pattern. Rotate to 0")
        socket_io.emit('rotate-to', (shared_key, math.radians(startAngle)))

    def triggerClosedStartPosition(self, socket_io):
        shared_key = time.time_ns()
        startAngle = 0
        if self.isBarSweep():
            startAngle = 180
        elif self.isSpaceSweep():
            startAngle = 360-self.space_deg/2
        elif self.isOpposingBarSweep():
            startAngle = 112
        else:
            warnings.warn("not 2 item pattern. Rotate to 0")
        socket_io.emit('rotate-to', (shared_key, math.radians(startAngle)))