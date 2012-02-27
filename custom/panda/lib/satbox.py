from nicos.core import *
from nicos.panda.wechsler import Beckhoff

class SatBox(Moveable):
    attached_devices = {
        'bus': (Beckhoff, 'modbus'),
    }

    valuetype = int
    widths = [1, 2, 5, 10, 20]

    def doRead(self):
        inx = self._adevs['bus'].ReadBitsOutput(0x1020, len(self.widths))
        return sum([inx[i]*self.widths[i] for i in range(len(self.widths))])
        
        # currently the input bits dont work, since the magnetic field of the monoburg switches them all on
        inx = self._adevs['bus'].ReadBitsInput(0x1000, 10)
        self.log.debug('position: %s' % inx)
        width = 0
        for i in range(len(self.widths)):
            if not inx[i*2]:
                if inx[i*2+1]:
                    width += self.widths[i]
                else:
                    self.log.warning('%d mm blade in inconsistent state' % widths[i])
        return width

    def doStatus(self):
        return status.OK, ''
        in1 = self._adevs['bus'].ReadBitsInput(0x1000, 8)
        in2 = self._adevs['bus'].ReadBitsInput(0x1008, 2)
        inx = in1 + in2
        widths = [1, 2, 5, 10, 20]
        for i in range(5):
            if inx[i*2] and inx[i*2+1]:
                return status.BUSY, '%d mm blade moving' % widths[i]
        return status.OK, ''
    
    def doStart(self, rpos):
        if rpos>sum(self.widths):
            raise InvalidValueError(self, 'Value %d too big!, maximum is %d' % (rpos,sum(self.widths)))
        which = [0] * len(self.widths)
        pos=rpos
        for i in range(len(self.widths)-1,-1,-1):
            if pos>=self.widths[i]:
                which[i]=1
                pos-=self.widths[i]
        if pos != 0:
            self.log.warning('Value %d impossible, trying %d instead!'%(rpos,rpos+1))
            return self.doStart( rpos+1)
        self.log.debug('setting blades: %s' % [which[i]*self.widths[i] for i in range(len(which))])
        self._adevs['bus'].WriteBitsOutput(0x1020, which)
