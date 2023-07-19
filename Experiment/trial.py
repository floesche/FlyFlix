"""A trial consists of an open loop and a closed loop condition. Part of FlyFlix"""

import warnings
import time
import random

from . import Duration, SpatialTemporal, OpenLoopCondition, SweepCondition, ClosedLoopCondition
from Experiment.starfield_spatial_temporal import StarfieldSpatialTemporal

class Trial():
    """Single trial, the combination of an open loop and a closed loop condition."""

    def __init__(self,
                 #variables used in both starfield and panel trials
                 trial_id,
                 rotate_deg_hz=0,
                 osc_freq=0, osc_width=0,
                 fg_color=0x00ff00, 
                 openloop_duration=Duration(3000), closedloop_duration=Duration(5000), 
                 gain=1, fps=60, 
                 pretrial_duration=Duration(500), posttrial_duration=Duration(500),
                 comment=None,
                 
                 #panel/bar variables
                 bar_deg=None, space_deg=None,
                 start_mask_deg=0, end_mask_deg=0,
                 sweep=None,
                 closedloop_bar_deg = None,
                 bg_color=0x000000,
                 bar_height=0.8,
                 
                 #starfield variables
                 sphere_count=None, sphere_radius_deg=None,
                 shell_radius=None, seed=None,
                 starfield_closedloop=False
                ) -> None:
        """
        Define trial

        params used in both panel and starfield cases:
        :param str trial_id: unique identifier for trial, preferably an integer number
        :param float rotate_deg_hz: movement speed in degree per second, positive is clockwise
        :param float osc_freq: frequency of oscillations - overrides rotate_deg_hz
        :param float osc_width: the width of an oscillation in degrees
        :param Duration openloop_duration: duration of the openloop condition
        :param Duration closedloop_duration: duration of the closed loop condition
        :param float gain: multiplier for orientation change read from the FicTrac instance
        :param float fps: client frame rate
        :param Duration pretrial_duration: duration of the pre-trial, where the stimulus is shown
            but not animated. Applies to open loop and closed loop conditions.
        :param Duration posttrial_duration: duration of the post-trial.
        :param str comment: additional comment that can be logged with the data
        
        params used only in trials with panels
        :param float bar_deg: size of the bar (bright) in degree
        :param float space_deg: size of the space (dark) in degree
        :param bool sweep: set to true, if the open loop condition is supposed to be a single
            stimulus sweep
        :param float closedloop_bar_deg: size of the bar (bright) for the closed loop condition
            in degree
            
        params used only in trials with starfield
        :param int sphere_count: the number of spheres surrounding the fly's position
        :param float sphere_radius_deg: the radius of the spheres surrounding the fly's position in degrees
        :param float shell_radius: the distance between the fly's position and the spheres
        :param int seed: a seed that generates a set of random points
        :param bool starfield_closedloop: boolean that determines if there is a closed loop condition for the trial
    
        :rtype: None
        """

        
        if bar_deg is not None and sphere_count is not None:
            warnings.warn("Cannot set bar degrees and sphere count. Bars will take precedence.")
        
        if sweep is not None and openloop_duration is not None:
            warnings.warn("Cannot set sweep and duration. Duration will take precedence.")
        if space_deg is None and bar_deg is not None and bar_deg > 0:
            space_deg = bar_deg
        if bar_deg is not None and 360 % (bar_deg + space_deg) != 0:
            warnings.warn(f"Pattern is not seamless: Bars are {bar_deg}°, space is {space_deg}°.")
        
        if rotate_deg_hz != 0 and osc_freq != 0:
            warnings.warn("Cannot set rotation degrees hz and oscillation frequency, oscillation will take precedence")
        
        self.conditions = []
        self.trial_id = trial_id
        self.comment = comment

        if bar_deg:
            openloop_spatial_temporal = SpatialTemporal(
                bar_deg=bar_deg,
                space_deg=space_deg,
                rotate_deg_hz=rotate_deg_hz,
                start_mask_deg=start_mask_deg, end_mask_deg=end_mask_deg,
                osc_freq=osc_freq, osc_width=osc_width,
                fg_color=fg_color, bg_color=bg_color,
                bar_height=bar_height)
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
        else: #if sphere_count
            if seed is None:
                warnings.warn("No seed set, generating random seed")
                seed = random.randint(0, 10000)
            #create starfield spatial-temporal
            openloop_spatial_temporal = StarfieldSpatialTemporal(
                sphere_count=sphere_count, 
                sphere_radius_deg=sphere_radius_deg,
                shell_radius=shell_radius,
                seed=seed,
                color=fg_color,
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
            if starfield_closedloop:
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
