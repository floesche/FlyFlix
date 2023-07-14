"""A trial consists of an open loop and a closed loop condition. Part of FlyFlix"""

import warnings
import time

from . import Duration, SpatialTemporal, OpenLoopCondition, SweepCondition, ClosedLoopCondition

class StarTrial():
    """Single trial, the combination of an open loop and a closed loop condition."""

    def __init__(self,
                 trial_id,
                 sphere_count=30, 
                 sphere_radius=None, 
                 shell_radius=None,
                 color = 0x00ff00,
                 rotate_deg_hz=0,
                 openloop_duration=Duration(3000), 
                 sweep=None,
                 closedloop_bar_deg = None, 
                 closedloop_duration=Duration(5000), 
                 gain=1,
                 osc_freq=0, 
                 osc_width=0,
                 fps=60,
                 pretrial_duration=Duration(500), 
                 posttrial_duration=Duration(500),
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

        self.conditions = []
        self.trial_id = trial_id
        self.comment = comment
        self.sphere_count = sphere_count
        self.sphere_radius = sphere_radius
        self.shell_radius = shell_radius
        self.color = color
        


    def trigger(self, socket_io) -> None:
        """
        Execute Trial. This consists of sending a number of logging-related messages to the client
        before iterating through the list of conditions and trigger one after another.

        :param Socket socket_id: Socket.IO used for communication with the client.
        :rtype: None
        """
        socket_io.emit('spatial-setup', ("self.lid", self.sphere_count, self.sphere_radius, self.shell_radius, self.color))
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
