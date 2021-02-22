import warnings
import math
import time

class SpatialTemporal():

    def __init__(self, barDeg=60, spaceDeg=60, rotateDegHz=0) -> None:
        if (barDeg < 0 or spaceDeg <0):
            warnings.war("bar size or space is negative")
        if (360 % (barDeg + spaceDeg) != 0):
            warnings.warn(f"Spatial pattern is not seamless with bar {barDeg}° and space {spaceDeg}")
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