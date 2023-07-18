"""A trial consists of an open loop and a closed loop condition. Part of FlyFlix"""

import warnings
import time

from . import Duration, OpenLoopCondition, ClosedLoopCondition
from Experiment.starfield_spatial_temporal import StarfieldSpatialTemporal

class StarfieldTrial():
    """Single trial, the combination of an open loop and a closed loop condition."""

    def __init__(self,
                 trial_id,
                 sphere_count=500, sphere_radius=30,
                 shell_radius=850,
                 color=0x00ff00,
                 rotate_deg_hz=0,
                 osc_freq=0, osc_width=0,
                 openloop_duration=Duration(3000),
                 closedloop_duration=Duration(5000), gain = 1,
                 fps=60,
                 pretrial_duration=Duration(500), posttrial_duration=Duration(500),
                 comment=None          
    ) -> None:
        """
        Define starfield trial
        
        :param str trial_id: unique identifier for trial, preferably an integer number
        :param int sphere_count: the number of spheres surrounding the fly's position
        :param float sphere_radius: the radius of the spheres surrounding the fly's position
        :param float shell_radius: the distance between the fly's position and the spheres
        :param float rotate_deg_hz: movement speed in degree per second, positive is clockwise
        :param float osc_freq: the frequency of the oscillation of a trial
        :param float osc_width: the width of an oscillation in degrees
        :param Duration openloop_duration: duration of the openloop condition
        :param Duration closedloop_duration: duration of the closed loop condition
        :param float gain: multiplier for orientation change read from the FicTrac instance
        :param float fps: client frame rate
        :param Duration pretrial_duration: duration of the pre-trial, where the stimulus is shown
            but not animated. Applies to open loop and closed loop conditions.
        :param Duration posttrial_duration: duration of the post-trial.
        :param str comment: additional comment that can be logged with the data
        :rtype: None
        """
        
        if rotate_deg_hz is not 0 and osc_freq is not 0:
            warnings.warn("Cannot set rotation degrees hz and oscillation frequency, oscillation will take precedence")
        
        self.trial_id = trial_id
        self.conditions = []
        self.comment = comment
        
        #create starfield spatial-temporal
        openloop_spatial_temporal = StarfieldSpatialTemporal(
            sphere_count=sphere_count, 
            sphere_radius=sphere_radius,
            shell_radius=shell_radius,
            color=color,
            rotate_deg_hz=rotate_deg_hz,
            osc_freq=osc_freq,
            osc_width=osc_width
        )
        if openloop_duration is not None:
            olc = OpenLoopCondition(
                spatial_temporal=openloop_spatial_temporal,
                trial_duration=openloop_duration,
                fps=fps,
                pretrial_duration=pretrial_duration, posttrial_duration=posttrial_duration
            )
            self.conditions.append(olc)
        else:
            warnings.warn("Duration needs to be set")
        
        closedloop_spatial_temporal = openloop_spatial_temporal
        if closedloop_duration is not None:
            clc = ClosedLoopCondition(
                spatial_temporal=closedloop_spatial_temporal, trial_duration=closedloop_duration,
                gain=gain, fps=fps,
                pretrial_duration=pretrial_duration, posttrial_duration=posttrial_duration,
                is_starfield=True)
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
            if isinstance(condition, OpenLoopCondition):
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
        