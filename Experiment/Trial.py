"""A trial consists of an open loop and a closed loop condition. Part of FlyFlix"""

import warnings
import time

from . import Duration, SpatialTemporal, OpenLoopCondition, SweepCondition, ClosedLoopCondition

class Trial():
    """Single trial, the combination of an open loop and a closed loop condition."""

    def __init__(self,
                 trial_id,
                 bar_deg=30, space_deg=None, rotate_deg_hz=0,
                 openloop_duration=Duration(3000), sweep=None,
                 closedloop_bar_deg = None, closedloop_duration=Duration(5000), gain=1,
                 fps=60,
                 pretrial_duration=Duration(500), posttrial_duration=Duration(500),
                 comment=None) -> None:
        """
        Define trial

        :param str trial_id: unique identifier for trial, preferably an integer number
        :param float bar_deg: size of the bar (bright) in degree
        :param float space_deg: size of the space (dark) in degree
        :param float rotate_deg_hz: movement speed in degree per second, positive is clockwise
        :param Duration openloop_duration: duration of the openloop condition
        :param bool sweep: set to true, if the open loop condition is supposed to be a single
            stimulus sweep
        :param float closedloop_bar_deg: size of the bar (bright) for the closed loop condition
            in degree
        :param Duration closedloop_duration: duration of the closed loop condition
        :param float gain: multiplier for orientation change read from the FicTrac instance
        :param float fps: client frame rate
        :param Duration pretrial_duration: duration of the pre-trial, where the stimulus is shown
            but not animated. Applies to open loop and closed loop conditions.
        :param Duration posttrial_duration: duration of the post-trial.
        :param str comment: additional comment that can be logged with the data
        :rtype: None
        """

        if sweep is not None and openloop_duration is not None:
            warnings.warn("Cannot set sweep and duration. Duration will take precedence.")
        if space_deg is None and bar_deg > 0:
            space_deg = bar_deg
        if 360 % (bar_deg + space_deg) != 0:
            warnings.warn(f"Pattern is not seamless: Bars are {bar_deg}°, space is {space_deg}°.")
        self.conditions = []
        self.trial_id = trial_id
        self.comment = comment

        openloop_spatial_temporal = SpatialTemporal(
            bar_deg=bar_deg,
            space_deg=space_deg,
            rotate_deg_hz=rotate_deg_hz)
        if openloop_duration is not None:
            olc = OpenLoopCondition(
                spatial_temporal=openloop_spatial_temporal,
                trial_duration=openloop_duration,
                fps=fps,
                pretrial_duration=pretrial_duration, posttrial_duration=posttrial_duration)
            self.conditions.append(olc)
        elif sweep is not None:
            olc = SweepCondition(
                spatial_temporal=openloop_spatial_temporal,
                sweep_count=1, fps=fps,
                pretrial_duration=pretrial_duration, posttrial_duration=posttrial_duration)
            self.conditions.append(olc)
        else:
            warnings.warn("Either sweep or duration needs to be set")

        closedloop_spatial_temporal = openloop_spatial_temporal
        if closedloop_bar_deg is not None:
            if 0 < closedloop_bar_deg <= 180:
                closedloop_spatial_temporal = SpatialTemporal(
                    bar_deg=closedloop_bar_deg, space_deg=(180-closedloop_bar_deg))
            elif 180 < closedloop_bar_deg <= 360:
                closedloop_spatial_temporal = SpatialTemporal(
                    bar_deg=closedloop_bar_deg-180, space_deg=360-closedloop_bar_deg)
        clc = ClosedLoopCondition(
            spatial_temporal=closedloop_spatial_temporal, trial_duration=closedloop_duration,
            gain=gain, fps=fps,
            pretrial_duration=pretrial_duration, posttrial_duration=posttrial_duration)
        self.conditions.append(clc)


    def trigger(self, socket_io) -> None:
        """
        Execute Trial. This consists of sending a number of logging-related messages to the client
        before iterating through the list of conditions and trigger one after another.

        :param Socket socket_id: Socket.IO used for communication with the client.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit("ssync", (shared_key))
        socket_io.emit("meta", (shared_key, "trial-start", self.trial_id))
        if self.comment:
            socket_io.emit("meta", (shared_key, "comment", self.comment))
        for count, condition in enumerate(self.conditions):
            # TODO: move to OpenLoop and Sweep?
            if isinstance(condition, (OpenLoopCondition, SweepCondition)):
                socket_io.emit("meta", (shared_key, "condition-type", "open-loop"))
            elif isinstance(condition, ClosedLoopCondition):
                socket_io.emit("meta", (shared_key, "condition-type", "closed-loop"))
            socket_io.emit("meta", (shared_key, "condition-start", f"{self.trial_id}.{count}"))
            condition.trigger(socket_io)
            socket_io.emit("meta", (shared_key, "condition-end", f"{self.trial_id}.{count}"))
        socket_io.emit("meta", (shared_key, "trial-end", self.trial_id))


    def set_id(self, trial_id) -> None:
        """
        set ID for trial

        :param str trial_id: ID of the trial, preferably an integer
        :rtype: None
        """
        self.trial_id = trial_id
