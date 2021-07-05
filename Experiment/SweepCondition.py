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
        if self.spatial_temporal.is_bar_sweep():
            self.trial_duration = Duration(self.spatial_temporal.get_bar_sweep_duration())
            self.is_bar_sweep = True
        elif self.spatial_temporal.is_space_sweep():
            self.trial_duration = Duration(self.spatial_temporal.get_space_sweep_duration())
            self.is_bar_sweep = False
        self.pretrial_duration = pretrial_duration
        self.posttrial_duration = posttrial_duration
        self.fps = fps

    def trigger_fps(self, socket_io):
        shared_key = time.time_ns()
        socket_io.emit('fps', (shared_key, self.fps))

    def trigger(self, socket_io):
        self.trigger_fps(socket_io)
        self.spatial_temporal.trigger_spatial(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.spatial_temporal.trigger_sweep_start_position(socket_io)
        self.pretrial_duration.trigger_delay(socket_io)
        self.spatial_temporal.trigger_rotation(socket_io)
        self.trial_duration.trigger_delay(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.posttrial_duration.trigger_delay(socket_io)