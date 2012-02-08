from nicos.core import *
from nicos.panda.wechsler import Beckhoff

class SatBox(Moveable):
    attached_devices = {
        'bus': (Beckhoff, 'modbus'),
    }

    valuetype = int

    def doRead(self):
        # XXX ReadBitsInput(..., 10) does not return anything beyond the 8th bit
        in1 = self._adevs['bus'].ReadBitsInput(0x1000, 8)
        in2 = self._adevs['bus'].ReadBitsInput(0x1008, 2)
        inx = in1 + in2
        self.log.debug('position: %s' % inx)
        width = 0
        widths = [1, 2, 5, 10, 20]
        for i in range(5):
            if not inx[i*2]:
                if inx[i*2+1]:
                    width += widths[i]
                else:
                    self.log.warning('%d mm blade in inconsistent state' % widths[i])
        return width

    def doStatus(self):
        in1 = self._adevs['bus'].ReadBitsInput(0x1000, 8)
        in2 = self._adevs['bus'].ReadBitsInput(0x1008, 2)
        inx = in1 + in2
        widths = [1, 2, 5, 10, 20]
        for i in range(5):
            if inx[i*2] and inx[i*2+1]:
                return status.BUSY, '%d mm blade moving' % widths[i]
        return status.OK, ''
    
    def doStart(self, pos):
        which = [0] * 5
        if pos > 38:
            raise InvalidValueError(self, 'too thick')
        if pos >= 20:
            pos -= 20
            which[4] = 1
        if pos >= 10:
            pos -= 10
            which[3] = 1
        if pos >= 5:
            pos -= 5
            which[2] = 1
        if pos >= 2:
            pos -= 2
            which[1] = 1
        if pos == 1:
            which[0] = 1
        elif pos != 0:
            raise InvalidValueError(self, 'impossible: %d' % pos)
        self.log.debug('setting which: %s' % which)
        for i in which:
            self._adevs['bus'].WriteBitOutput(0x1020 + i, which[i])
