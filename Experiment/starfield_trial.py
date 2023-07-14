"""A trial consists of an open loop and a closed loop condition. Part of FlyFlix"""

import warnings
import time

from . import Duration, SpatialTemporal, OpenLoopCondition, SweepCondition, ClosedLoopCondition

class StarfieldTrial():
    """Single trial, the combination of an open loop and a closed loop condition."""

    def __init__(self,
                 trial_id,
                 sphere_count=500,
                 sphere_radius=30,
                 shell_radius=850,
                 color=0x00ff00
    ) -> None:
        self.trial_id = trial_id
        self.sphere_count = sphere_count
        self.sphere_radius = sphere_radius
        self.shell_radius = shell_radius
        self.color = color
    
    def trigger(self, socket_io) -> None:
        socket_io.emit('spatial-setup', (self.trial_id, self.sphere_count, self.sphere_radius, self.shell_radius, self.color))
    
        