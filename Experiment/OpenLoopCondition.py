import warnings
import time

from . import Duration, SpatialTemporal

class OpenLoopCondition():

    def __init__(self, spatial_temporal=None, trial_duration=None, fps=60, pretrial_duration=Duration(500), posttrial_duration=Duration(500)) -> None:
        if spatial_temporal is None:
            warnings.warn("Spatial Temporal not set")
        if trial_duration is None:
            warnings.warn("Duration not set")
        if fps <=0 or fps > 60:
            warnings.warn("fps outside meaningful constraints")
        self.spatial_temporal = spatial_temporal
        self.trial_duration = trial_duration
        self.pretrial_duration = pretrial_duration
        self.posttrial_duration = posttrial_duration
        self.fps = fps

    def trigger_fps(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit('fps', (shared_key, self.fps))

    def trigger(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit("meta", (shared_key, "openloop-start", 1))
        self.trigger_fps(socket_io)
        self.spatial_temporal.trigger_spatial(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.pretrial_duration.triggerDelay(socket_io)
        self.spatial_temporal.trigger_rotation(socket_io)
        self.trial_duration.triggerDelay(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.posttrial_duration.triggerDelay(socket_io)
        socket_io.emit("meta", (shared_key, "openloop-end", 1))