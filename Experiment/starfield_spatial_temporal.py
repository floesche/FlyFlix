"""
This is part of the FlyFlix server.
"""

import warnings
import math
import time
import random
import json

from . import Duration

class StarfieldSpatialTemporal():
    """
    Description of spatial and temporal stimulation for starfield trials.
    """
    
    def __init__(self,
        sphere_count=500, sphere_radius_deg=3,
        radius_dev = None,
        shell_radius=10, seed=0,
        fg_color=0x00ff00, bg_color=0x000000,
        rotate_deg_hz=0,
        osc_width=0, osc_freq=0
    ) -> None:
        """
        Constructor for a spatial-temporal description of a starfield stimulus. The assumption is that
        the spherical area surrounds the fly's position and spheres surround it in random positions but 
        with uniform distance.

        :param in sphere_count: Amount of spheres surrounding the fly's position.
        :param float sphere_radius: The radius size of each of the spheres surrounding the fly
        :param float radius_dev: the deviation of possible radius sizes from the sphere_radius_range in degrees
            For example, if sphere_radius is 3 and radius_dev is 1 then the spheres' radius would range in size from 2-4 degrees
        :param float shell_radius: the distance between the fly's position and the spheres
        :param int seed: a seed that generates a set of random points
        :param float rotate_deg_hz: Rotation speed in degree per second.
        :param float osc_freq: frequency of oscillations - overrides rotate_deg_hz
        :param float osc_width: the width of an oscillation in degrees
        
        :rtype: None
        """
        
        if shell_radius>1000:
            warnings.warn("Shell radius is too large and will not display. Set to a size less than or equal to 1000")
        if fg_color == bg_color:
            warnings.warn("Background and foreground colors are the same.")
        
        
        self.sphere_count = sphere_count
        self.sphere_radius_deg = sphere_radius_deg
        self.radius_dev = radius_dev
        self.shell_radius = shell_radius
        self.seed = seed
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.rotate_deg_hz = rotate_deg_hz
        self.osc_width = osc_width
        self.osc_freq = osc_freq
        self.positions = []
    
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
        socket_io.emit('spheres-speed', (shared_key, math.radians(self.rotate_deg_hz)))
        
    def trigger_oscillation(self, socket_io) -> None:
        """
        Triggers the start of the spatial-temporal pattern by sending the according command through
        the socket.

        :param socket socket_io: Socket used for sending the update
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('spheres-oscillation', (shared_key, self.osc_freq, self.osc_width))
        
    def trigger_stop(self, socket_io) -> None:
        """
        Stops the movement of the spatial-temporal pattern by sending a stop command through the
        socket.

        :param socket socket_io: Socket for sending the update.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('spheres-speed', (shared_key, 0))
        socket_io.emit('spheres-oscillation', (shared_key, 0, 0))
        
    def trigger_spatial(self, socket_io) -> None:
        """
        Sends the starfield setup via the socket.

        :param socket socket_io: Socket for sending the update.
        :rtype: None
        """
        
        self.generate_points()

        shared_key = time.time_ns()
        socket_io.emit('spheres-spatial-setup', (
            shared_key,
            self.sphere_count,
            self.sphere_radius_deg,
            self.shell_radius,
            self.seed,
            json.dumps(self.positions),
            self.fg_color,
            self.bg_color
        ))
        
    def generate_points(self):
        """
        Generates a list of coordinates for random points on a sphere of radius shell_radius +- some level of deviation
        based on the seed value and updates the list of positions. Assumes the center of the sphere is at (0,0,0).
        
        Inspired by https://stackoverflow.com/questions/5531827/random-point-on-a-given-sphere answer from user Neil Lamoureux
        
        :rtype: None
        """

        random.seed(self.seed)
        
        for k in range(self.sphere_count):

            t = random.random()
            u = random.random()
            v = random.random()
            w = random.random()
            
            theta = 2 * math.pi * t
            phi = math.acos(2 * u - 1)
            
            if self.radius_dev is not None:
                dev = v*self.radius_dev
                dev *= (w * 2 - 1)
            else:
                dev = 0
            
            x = self.shell_radius * math.sin(phi) * math.cos(theta)
            y = self.shell_radius * math.sin(phi) * math.sin(theta)
            z = self.shell_radius * math.cos(phi)
            
            self.positions.append([x,y,z, dev])
            
            
        