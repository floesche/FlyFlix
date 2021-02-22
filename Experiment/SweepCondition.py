import warnings
import time

from .Duration import Duration
from .SpatialTemporal import SpatialTemporal

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