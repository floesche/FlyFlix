"""A trial consists of an open loop and a closed loop condition. Part of FlyFlix"""

import warnings
import time

from . import Duration, SpatialTemporal, OpenLoopCondition, SweepCondition, ClosedLoopCondition

class StarfieldTrial():
    """Single trial, the combination of an open loop and a closed loop condition."""

    def __init__(self,
                 trial_id,
                 sphere_count=500, sphere_radius=30,
                 shell_radius=850,
                 color=0x00ff00,
                 rotate_deg_hz=0,
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
        

        Args:
            trial_id (_type_): _description_
            sphere_count (int, optional): _description_. Defaults to 500.
            sphere_radius (int, optional): _description_. Defaults to 30.
            shell_radius (int, optional): _description_. Defaults to 850.
            color (hexadecimal, optional): _description_. Defaults to 0x00ff00.
            speed (int, optional): _description_. Defaults to 0.
        """
        self.trial_id = trial_id
        self.sphere_count = sphere_count
        self.sphere_radius = sphere_radius
        self.shell_radius = shell_radius
        self.color = color
        self.rotate_deg_hz = rotate_deg_hz
    
    def trigger(self, socket_io) -> None:
        socket_io.emit('spatial-setup', (self.trial_id, self.sphere_count, self.sphere_radius, self.shell_radius, self.color))
        socket_io.emit('speed', ('test', self.rotate_deg_hz))
    
        