
from nicos.devices.taco import DigitalOutput

class RefcountDigitalOutput(DigitalOutput):
    def doInit(self, mode):
        self._counter = 0
        #DigitalOutput.doInit(self, mode)

    def doStart(self, target):
        if target:
            self._counter += 1
        else:
            self._counter -= 1
        self._taco_guard(self._dev.write, self._counter >= 1)
