"""Experimental condition with a single stimulus sweep"""

import warnings
import time

from .Duration import Duration

class SweepCondition():
    """ Description of a condition with a single stimulus sweep."""

    def __init__(
        self,
        spatial_temporal=None, sweep_count=1,
        fps=60,
        pretrial_duration=Duration(500), posttrial_duration=Duration(500)
        ) -> None:
        """
        Initialization of the condition.

        :param SpatialTemporal spatial_temporal: spatial and temporal definition of the stimulus
        :param int sweep_count: number of sweeps (currently unused)
        :param float fps: frame rate of client
        :param Duration pretrial_duration: duration of the pre-trial period, where the stimulus is
            shown but not animated.
        :param Duration posttrial_duration: duration of the post-trial period.
        """
        if spatial_temporal is None:
            warnings.warn("Spatial Temporal not set")
        if fps <=0 or fps > 60:
            warnings.warn(f"fps ({fps}) outside meaningful constraints")
        self.spatial_temporal = spatial_temporal
        if self.spatial_temporal.is_bar_sweep():
            self.trial_duration = self.spatial_temporal.get_bar_sweep_duration()
            self.is_bar_sweep = True
        elif self.spatial_temporal.is_space_sweep():
            self.trial_duration = self.spatial_temporal.get_space_sweep_duration()
            self.is_bar_sweep = False
        self.pretrial_duration = pretrial_duration
        self.posttrial_duration = posttrial_duration
        self.fps = fps

    def trigger_fps(self, socket_io):
        """
        Set the client frame rate.

        :param Socket socket_io: The Socket.IO used for communicating with the client.
        """
        shared_key = time.time_ns()
        socket_io.emit('fps', (shared_key, self.fps))

    def trigger(self, socket_io):
        """
        Trigger the condition. Specifically, this means setting the client's frame rate and show
        the stimulus without moving it for the duration of the pre-trial. Then run the sweep,
        followed by stopping the stimulus for the duration of the post-trial period.
        """
        self.trigger_fps(socket_io)
        self.spatial_temporal.trigger_spatial(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.spatial_temporal.trigger_sweep_start_position(socket_io)
        self.pretrial_duration.trigger_delay(socket_io)
        self.spatial_temporal.trigger_rotation(socket_io)
        self.trial_duration.trigger_delay(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.posttrial_duration.trigger_delay(socket_io)
