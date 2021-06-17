import warnings
import time

from .Duration import Duration
from .SpatialTemporal import SpatialTemporal

class SweepCondition():

    def __init__(self, spatial_temporal=None, sweepCount=1, fps=60, pretrial_duration=Duration(500), posttrial_duration=Duration(500)) -> None:
        if spatial_temporal is None:
            warnings.warn("Spatial Temporal not set")
        if fps <=0 or fps > 60:
            warnings.warn(f"fps ({fps}) outside meaningful constraints")
        self.spatial_temporal = spatial_temporal
        if self.spatial_temporal.isBarSweep():
            self.trial_duration = Duration(self.spatial_temporal.getBarSweepDuration())
            self.isBarSweep = True
        elif self.spatial_temporal.isSpaceSweep():
            self.trial_duration = Duration(self.spatial_temporal.getSpaceSweepDuration())
            self.isBarSweep = False
        self.pretrial_duration = pretrial_duration
        self.posttrial_duration = posttrial_duration
        self.fps = fps

    def trigger_fps(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit('fps', (shared_key, self.fps))

    def trigger(self, socket_io):
        self.trigger_fps(socket_io)
        self.spatial_temporal.triggerSpatial(socket_io)
        self.spatial_temporal.triggerStop(socket_io)
        self.spatial_temporal.triggerSweepStartPosition(socket_io)
        self.pretrial_duration.triggerDelay(socket_io)
        self.spatial_temporal.triggerRotation(socket_io)
        self.trial_duration.triggerDelay(socket_io)
        self.spatial_temporal.triggerStop(socket_io)
        self.posttrial_duration.triggerDelay(socket_io)