import warnings
import time

from . import Duration, SpatialTemporal, OpenLoopCondition, SweepCondition, ClosedLoopCondition

class Trial():

    def __init__(self,
                 id,
                 barDeg=30, spaceDeg=None, 
                 rotateDegHz=0, 
                 openLoopDuration=Duration(3000), sweep=None, 
                 clBarDeg = None,
                 closedLoopDuration=Duration(5000), gain=1, 
                 fps=60, 
                 preTrialDuration=Duration(500), postTrialDuration=Duration(500),
                 comment=None) -> None:

        if sweep is not None and openLoopDuration is not None:
            warnings.warn("Cannot set sweep and duration. Duration will take precedence.")
        if spaceDeg is None and barDeg > 0:
            spaceDeg = barDeg
        if 360 % (barDeg + spaceDeg) != 0:
            warnings.warn(f"Pattern is not seamless: Bars are {barDeg}°, space is {spaceDeg}°.")
        self.conditions = []
        self.id = id
        self.comment = comment

        olST = SpatialTemporal(barDeg=barDeg, spaceDeg=spaceDeg, rotateDegHz=rotateDegHz)
        if openLoopDuration is not None:
            olc = OpenLoopCondition(spatialTemporal=olST, trialDuration=openLoopDuration, fps=fps, preTrialDuration=preTrialDuration, postTrialDuration=postTrialDuration)
            self.conditions.append(olc)
        elif sweep is not None:
            olc = SweepCondition(spatialTemporal=olST, sweepCount=1, fps=fps, preTrialDuration=preTrialDuration, postTrialDuration=postTrialDuration)
            self.conditions.append(olc)
        else:
            warnings.warn("Either sweep or duration needs to be set")

        clST = olST
        if clBarDeg is not None:
            if clBarDeg > 0 and clBarDeg <= 180:
                clST = SpatialTemporal(barDeg=clBarDeg, spaceDeg=(180-clBarDeg))
            elif clBarDeg > 180 and clBarDeg <=360:
                clST = SpatialTemporal(barDeg=clBarDeg-180, spaceDeg=360-clBarDeg)
        clc = ClosedLoopCondition(spatialTemporal=clST, trialDuration=closedLoopDuration, gain=gain, fps=fps, preTrialDuration=preTrialDuration, postTrialDuration=postTrialDuration)
        self.conditions.append(clc)

    def trigger(self, io) -> None:
        sharedKey = time.time_ns()
        io.emit("ssync", (sharedKey))
        io.emit("meta", (sharedKey, "trial-start", self.id))
        if self.comment:
            io.emit("meta", (sharedKey, "comment", self.comment))
        for count, condition in enumerate(self.conditions):
            if (isinstance(condition, OpenLoopCondition) or isinstance(condition, SweepCondition)):
                io.emit("meta", (sharedKey, "condition-type", "open-loop"))
            elif isinstance(condition, ClosedLoopCondition):
                io.emit("meta", (sharedKey, "condtiion-type", "closed-loop"))
            io.emit("meta", (sharedKey, "condition-start", f"{self.id}.{count}"))
            condition.trigger(io)
            io.emit("meta", (sharedKey, "condition-end", f"{self.id}.{count}"))
        io.emit("meta", (sharedKey, "trial-end", self.id))

    def setID(self, id) -> None:
        self.id = id