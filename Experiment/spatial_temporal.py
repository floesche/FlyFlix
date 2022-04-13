"""
This is part of the FlyFlix server.
"""

import warnings
import math
import time

from . import Duration

class SpatialTemporal():
    """
    Description of spatial and temporal stimulation.
    """

    def __init__(self, bar_deg=60, space_deg=60, rotate_deg_hz=0, start_mask_deg=0, end_mask_deg=0) -> None:
        """
        Constructor for a spatial-temporal description of a stimulus. The assumption is that the
        arena covers 360° and the bars and spaces alternate. All bars and all spaces are of the
        same size, for example the bars could be 30°, the space between bars 15°. In this example,
        the bars and spaces would be repeated 8 times to fill the whole cylinder (30+15)*8=360.

        :param float bar_deg: Size of the colored  bar in degree.
        :param float space_deg: Size of the space between bars in degree
        :param float rotate_deg_hz: Rotation speed in degree per second.
        :rtype: None
        """
        if bar_deg < 0 or space_deg <0:
            warnings.warn("bar size or space is negative")
        if 360 % (bar_deg + space_deg) != 0:
            warnings.warn(
                f"Spatial pattern is not seamless with bar {bar_deg}° and space {space_deg}")
        if rotate_deg_hz is None:
            warnings.warn("temporal components needs to be set.")
        if start_mask_deg > end_mask_deg:
            warnings.warn("mask has invalid range.")
        self.bar_deg = bar_deg
        self.space_deg = space_deg
        self.rotate_deg_hz = rotate_deg_hz
        self.start_mask_deg = start_mask_deg
        self.end_mask_deg = end_mask_deg

    def is_bar_sweep(self) -> bool:
        """
        Check if the current spatial-temporal description is most likely a bar sweep. This is the
        case if there is no repetition of the pattern and the bar (bright) is smaller than the
        space (dark).

        :rtype: bool
        """
        if self.bar_deg<self.space_deg and self.bar_deg+self.space_deg==360:
            return True
        return False

    def is_space_sweep(self) -> bool:
        """
        Check if the  current spatial-temporal stimulus is most likely a space sweep. This is the
        case if there is no repetition of the pattern and the bar (bright) is bigger than the
        space (dark).

        :rtype: bool
        """
        if self.bar_deg>self.space_deg and self.bar_deg+self.space_deg==360:
            return True
        return False

    def is_opposing_bar_sweep(self) -> bool:
        """
        Check if there is a opposing bar sweep – a special condition where one bar and one space
        fill half of the cylinder.

        :rtype: bool
        """
        if self.bar_deg + self.space_deg == 180:
            return True
        return False

    def get_bar_sweep_duration(self, sweep_angle_deg=180) -> Duration:
        """
        Calculates the duration for a bar sweep and returns the duration in seconds.

        :param float sweep_angle_deg: size of the viewing angle for the sweep. Defaults to half a
            cylinder (180°).
        :rtype: Duration
        """
        return Duration(((sweep_angle_deg + 2*self.bar_deg) / abs(self.rotate_deg_hz))*1000)

    def get_space_sweep_duration(self, sweep_angle_deg=180) -> Duration:
        """
        Calculates the duration for a space sweep and returns the duration in seconds.

        :param float sweep_angle_deg: size of the viewing angle for the sweep. Defaults to half a
            cylinder (180°).
        :rtype: Duration
        """
        return Duration((sweep_angle_deg + 2* self.space_deg) / abs(self.rotate_deg_hz)*1000)

    def trigger_rotation(self, socket_io) -> None:
        """
        Triggers the start of the spatial-temporal pattern by sending the according command through
        the socket.

        :param socket socket_io: Socket used for sending the update
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('speed', (shared_key, math.radians(self.rotate_deg_hz)))

    def trigger_stop(self, socket_io) -> None:
        """
        Stops the movement of the spatial-temporal pattern by sending a stop command through the
        socket.

        :param socket socket_io: Socket for sending the update.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('speed', (shared_key, 0))

    def trigger_spatial(self, socket_io) -> None:
        """
        Sends the bar size and space size via the socket to setup up the client.

        :param socket socket_io: Socket for sending the update.
        :rtype: None
        """
        shared_key = time.time_ns()
        socket_io.emit('spatial-setup', (
            shared_key,
            math.radians(self.bar_deg),
            math.radians(self.space_deg),
            math.radians(self.start_mask_deg),
            math.radians(self.end_mask_deg)))

    def trigger_sweep_start_position(self, socket_io) -> None:
        """
        Rotates the pattern to the starting position for a single sweep. The starting position is
        estimated based on the assumed viewing port size of roughly 180°, the size of bars (bright)
        and space (dark), and the direction of movement.

        :param socket socket_io: Socket for sending the update to the client.
        :rtype: None
        """
        shared_key = time.time_ns()
        start_angle = 0
        if self.is_bar_sweep():
            if self.rotate_deg_hz > 0:
                start_angle = 90
            else:
                start_angle = 270+self.bar_deg
        elif self.is_space_sweep():
            if self.rotate_deg_hz > 0:
                start_angle = 90 - self.space_deg
            else:
                start_angle = 270
        else:
            warnings.warn("not 2 item pattern. Rotate to 0")
        socket_io.emit('rotate-to', (shared_key, math.radians(start_angle)))

    def trigger_closedloop_start_position(self, socket_io) -> None:
        """
        Rotates the pattern to a sensible starting position for a closed loop experiment, which
        means that there is an edge between dark and bright in front of the animal.

        :param socket socket_io: Socket for sending the update to the client.
        :rtype: None
        """
        shared_key = time.time_ns()
        start_angle = 0
        if self.is_bar_sweep():
            start_angle = 180
        elif self.is_space_sweep():
            start_angle = 360-self.space_deg/2
        elif self.is_opposing_bar_sweep():
            start_angle = 112
        else:
            warnings.warn("not 2 item pattern. Rotate to 0")
        socket_io.emit('rotate-to', (shared_key, math.radians(start_angle)))
