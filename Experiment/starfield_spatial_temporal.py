"""
This is part of the FlyFlix server.
"""

import warnings
import math
import time

from . import Duration

class StarfieldSpatialTemporal():
    """
    Description of spatial and temporal stimulation for starfield trials.
    """
    
    def __init__(self,
        sphere_count=500, sphere_radius=30,
        shell_radius=850,
        color=0x00ff00,
        rotate_deg_hz=0,
        osc_width=0, osc_freq=0
    ) -> None:
        """
        Constructor for a spatial-temporal description of a starfield stimulus. The assumption is that
        the spherical area surrounds the fly's position and spheres surround it in random positions but 
        with uniform distance.

        :param in sphere_count: Amount of spheres surrounding the fly's position.
        :param float sphere_radius: The radius size of each of the spheres surrounding the fly
        :param float rotate_deg_hz: Rotation speed in degree per second.
        :rtype: None
        """
        # todo: add warnings
        
        self.sphere_count = sphere_count
        self.sphere_radius = sphere_radius
        self.shell_radius = shell_radius
        self.color = color
        self.rotate_deg_hz = rotate_deg_hz
        self.osc_width = osc_width
        self.osc_freq = osc_freq
    
    def is_oscillation(self) -> bool:
        if self.osc_freq > 0:
            return True
        return False

    def get_oscillation_duration(self) -> Duration:
        return Duration(1.0/self.osc_freq * 2 * 1000)
    
    def trigger_rotation(self, socket_io) -> None:
        """
        Triggers the start of the spatial-temporal pattern by sending the according command through
        the socket.

        :param socket socket_io: Socket used for sending the update
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('speed', (shared_key, math.radians(self.rotate_deg_hz)))
        
    def trigger_oscillation(self, socket_io) -> None:
        shared_key = time.time_ns()
        socket_io.emit('oscillation', (shared_key, self.osc_freq, self.osc_width))
        
    def trigger_stop(self, socket_io) -> None:
        """
        Stops the movement of the spatial-temporal pattern by sending a stop command through the
        socket.

        :param socket socket_io: Socket for sending the update.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('speed', (shared_key, 0))
        socket_io.emit('oscillation', (shared_key, 0, 0))
        
    def trigger_spatial(self, socket_io) -> None:
        """
        Sends the starfield setup via the socket.

        :param socket socket_io: Socket for sending the update.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('spatial-setup', (
            shared_key,
            self.sphere_count,
            self.sphere_radius,
            self.shell_radius,
            self.color,
        ))