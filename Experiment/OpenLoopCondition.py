"""Open loop condition, implementing """
import warnings
import time

from . import Duration, SpatialTemporal

class OpenLoopCondition():
    """
    Description of open loop condition
    """

    def __init__(
        self,
        spatial_temporal=None, trial_duration=None, fps=60,
        pretrial_duration=Duration(500), posttrial_duration=Duration(500)
        ) -> None:
        """
        Constructor for open loop condition.

        :param SpatialTemporal spatial_temporal: Spatial and temporal definition of the stimulus
        :param Duration trial_duration: duration of the stimulus
        :param float fps: frame rate of the system
        :param Duration pretrial_duration: waiting period of the pretrial, the time when the
            stimulus is shown without movement
        :param  Duration posttrial_duration: waiting period of the post trial.
        :rtype: None
        """
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

    def trigger_fps(self, socket_io) -> None:
        """
        Trigger the fps setting.

        :param Socket socket_io: Socket.IO used for communication with the client. It is part of
            the standard interface, but not used in this particular method.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('fps', (shared_key, self.fps))

    def trigger(self, socket_io) -> None:
        """
        Trigger the open loop condition. This means, that configuration of stimulus and frame rate
            are sent to the client, then the display is stopped for the duration of the pre-trial
            period, then the trial is triggered, followed by the post-trial duration.

        :param Socket socket_io: Socket.IO used for communication with the client.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit("meta", (shared_key, "openloop-start", 1))
        self.trigger_fps(socket_io)
        self.spatial_temporal.trigger_spatial(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.pretrial_duration.trigger_delay(socket_io)
        self.spatial_temporal.trigger_rotation(socket_io)
        self.trial_duration.trigger_delay(socket_io)
        self.spatial_temporal.trigger_stop(socket_io)
        self.posttrial_duration.trigger_delay(socket_io)
        socket_io.emit("meta", (shared_key, "openloop-end", 1))
