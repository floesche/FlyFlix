# from __future__ import annotations
# from abc import ABC, abstractmethod, abstractproperty
# from typing import Any

# class Builder(ABC):

#     @abstractproperty
#     def makePrecondition(self) -> None:
#         pass


# class OpenLoopBuilder(Builder):

#     def makePrecondition(self)




# class OpenLoopCondition():

#     def __init__(self) -> None:
        

# class Condition():
    
#     def __init__(self, duration=0, fps=60):
#         pass


#     def setDuration(self, duration=)

#     def run(self, socketio):
#         pass




# class OpenLoopCondition(Condition):

#     def __init__(self, duration=0, fps=60, barAngle=60, spaceAngle=60, rotateHz=0, rotateRad=0, rotateDeg=0):
#         super().__init__(self)
#         self.
    



# class OpenLoopSweepCondition(Condition):

#     def __init__(self):
#         super().__init__(self)


# class ClosedLoopCondition(Condition):
#     pass

import warnings
import math
import time

from datetime import datetime, timedelta


# class Spatial():

#     def __init__(self, barDeg=60, spaceDeg=60) -> None:
#         if (barDeg < 0 or spaceDeg <0):
#             warnings.war("bar size or space is negative")
#         if (360 % (barDeg + spaceDeg) != 0):
#             warnings.warn("Spatial pattern is not seamless")
#         self.barRad = math.radians(barDeg)
#         self.spaceRad = math.radians(spaceDeg)


# class Temporal():

#     def __init__(self, rotateDegPerSec) -> None:
#         if (rotateDegPerSec<-360 or rotateDegPerSec>360):
#             warnings.arn("rotational angle too small or too large")
#         self.rotateRad = math.radians(rotationDegPerSec)



class SpatialTemporal():

    def __init__(self, barDeg=60, spaceDeg=60, rotateDegHz=None, rotateBarHz=None, rotateSpaceHz=None) -> None:
        if (barDeg < 0 or spaceDeg <0):
            warnings.war("bar size or space is negative")
        if (360 % (barDeg + spaceDeg) != 0):
            warnings.warn("Spatial pattern is not seamless")

        if (rotateDegHz is not None and (rotateBarHz is not None or rotateSpaceHz is not None)):
            warnings.warn("Only one temporal values can be set. Degree per second takes precedence now.")

        self.barRad = math.radians(barDeg)
        self.spaceRad = math.radians(spaceDeg)

        if (rotateDegHz is not None):
            self.rotateRadHz = math.radians(rotateDegHz)
        elif (rotateBarHz is not None):
            self.rotateRadHz = barRad * 2;
        elif (rotateSpaceHz is not None):
            self.rotateRadHz = spaceRad * 2;
        else:
            warnings.warn("at least one temporal components needs to be set.")

    def run(self):
        pass

    def triggerRotation(self, io):
        sharedKey = time.time_ns()
        io.emit('speed', (sharedKey, self.rotateRadHz))

    def triggerStop(self, io):
        sharedKey = time.time_ns()
        io.emit('speed', (sharedKey, 0))


class Duration():

    def __init__(self, timeDuration=3000, sweepRotation=None, sweepTarget=None) -> None:
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
        self.spatialTemporal.triggerStop(io)
        self.preTrialDuration.triggerDelay(io)
        self.spatialTemporal.triggerRotation(io)
        self.trialDuration.triggerDelay(io)
        self.spatialTemporal.triggerStop(io)
        self.postTrialDuration.triggerDelay(io)
        # ttime = datetime.now() + timedelta(milliseconds=self.trialDuration.timeDuration)
        # sharedKey = time.time_ns()
        # savedata(sharedKey, "send-stripe-update", direction)
        # io.emit('speed', (sharedKey, self.spatialTemporal.rotateRadHz))
        # savedata(sharedKey, "show-only-nth-frame", nthframe)
        # io.emit('nthframe', nthframe)
        # while datetime.now() < ttime:
            # time.sleep(0.01)
