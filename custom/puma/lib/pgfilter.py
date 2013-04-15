
from nicos.core import Moveable, Readable, status, NicosError

import time

class PGFilter(Moveable):

    attached_devices = {
        'io_status':    (Readable, 'status of the limit switches'),
        'io_set':       (Moveable, 'output to set'),
    }

    def doStart(self, position):
        try:

            if self.doStatus()[0] != status.OK:
                raise NicosError(self, 'filter returned wrong position')

            if position == self.read(0):
                return

            if position == 'in':
                self._adevs['io_set'].move(1)
            elif position == 'out':
                self._adevs['io_set'].move(0)
            else:
                self.log.info('PG filter: illegal input')
                return

            time.sleep(2)

            if self.doStatus()[0] == status.ERROR:
                raise NicosError(self, 'PG filter is not readable, check device!')
        finally:
            self.log.info('PG filter: ', self.read(0))

    def doRead(self, maxage=0):
        result = self._adevs['io_status'].doRead(0)
        if result == 1:
            return 'in'
        elif result == 2:
            return 'out'
        else:
            raise NicosError(self, 'PG filter is not readable, check device!')


    def doStatus(self, maxage=0):
        s = self._adevs['io_status'].doRead(0)
        if s in [1,2]:
            return (status.OK, 'idle')
        else:
            return (status.ERROR, 'filter is in error state')
