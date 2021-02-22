import warnings
import time

from . import Duration, SpatialTemporal

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
        sharedKey = time.time_ns()
        io.emit("meta", (sharedKey, "openloop-start", 1))
        self.triggerFPS(io)
        self.spatialTemporal.triggerSpatial(io)
        self.spatialTemporal.triggerStop(io)
        self.preTrialDuration.triggerDelay(io)
        self.spatialTemporal.triggerRotation(io)
        self.trialDuration.triggerDelay(io)
        self.spatialTemporal.triggerStop(io)
        self.postTrialDuration.triggerDelay(io)
        io.emit("meta", (sharedKey, "openloop-end", 1))