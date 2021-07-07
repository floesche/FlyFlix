""" Duration is part of FlyFLix """

import time

from datetime import datetime, timedelta

class Duration():
    """
    Representation of a duration in FlyFlix
    """

    def __init__(self, time_duration=3000) -> None:
        """
        Constructor for Duration

        :param float time_duration: duration in ms, default 3000 (= 3 sec)
        :rtype: None
        """
        self.time_duration = time_duration

    def trigger_delay(self, socket_io) -> None:
        """
        Triggers the duration. This is basically a server-side delay for the amount of time
        specified in the constructor.

        :param socket socket_io: Socket.IO used for communication with the client. It is part of
                                 the standard interface, but not used in this particular method.
        :rtype: None
        """
        ttime = datetime.now() + timedelta(milliseconds=self.time_duration)
        while datetime.now() < ttime:
            time.sleep(0.01)
