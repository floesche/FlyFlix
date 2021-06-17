import time

from datetime import datetime, timedelta

class Duration():

    def __init__(self, timeDuration=3000) -> None:
        self.timeDuration = timeDuration

    def triggerDelay(self, socket_io):
        ttime = datetime.now() + timedelta(milliseconds=self.timeDuration)
        while datetime.now() < ttime:
            time.sleep(0.01)