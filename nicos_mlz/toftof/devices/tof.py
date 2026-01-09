# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""TOFTOF image channel devices."""

from nicos.core import Override, Param, intrange, status
from nicos.devices.entangle import TOFChannel

from nicos_mlz.toftof.lib import calculations as calc


class TOFTOFChannel(TOFChannel):
    # This class is, unfortunately, not agnostic to hw specifics
    parameters = {
        'frametime': Param('Total width of all time bins in s',
                           type=float, mandatory=False, volatile=True,
                           default=0.1, category='general', settable=True,),
        'monitorchannel': Param('Channel number of the monitor counter',
                                type=intrange(1, 1024), settable=False,
                                default=956,
                                ),
    }
    parameter_overrides = {
        'timechannels': Override(default=1024),
        'timeinterval': Override(type=float, unit='s', volatile=True),
        'delay':        Override(type=float, unit='s', volatile=True),
    }

    def doReadFrametime(self):
        return self.doReadTimeinterval() * self.doReadTimechannels()

    def doWriteFrametime(self, value):
        self.doStop()

        # as the HW can only realize selected values for timeinterval, probe
        # until success
        wanted_timeinterval = int(
            (value / self.doReadTimechannels()) / calc.ttr) * calc.ttr
        self.doWriteTimeinterval(wanted_timeinterval)
        # note: if a doReadTimeinterval differs in value from a previous
        #       doWriteTimeinterval,
        #       HW does actually use the returned value, not the wanted.
        #       (in this case: returned < set) so, increase the wanted value
        #       until the used one is big enough
        actual_timeinterval = self.doReadTimeinterval()
        while actual_timeinterval * self.timechannels < value:
            wanted_timeinterval += calc.ttr
            self.doWriteTimeinterval(wanted_timeinterval)
            actual_timeinterval = self.doReadTimeinterval()

    def doStop(self):
        if self.doStatus()[0] == status.BUSY:
            self._dev.Stop()

    def doWriteTimechannels(self, value):
        self.doStop()
        self._dev.timeChannels = value

    def doReadTimeinterval(self):
        # our timeinterval is in s, entangle is in ns, in multiple of calc.ttr
        return self._dev.timeInterval * 1e-9

    def doWriteTimeinterval(self, value):
        # our timeinterval is in s, entangle is in ns, in multiple of calc.ttr
        self.doStop()
        self._dev.timeInterval = int(value / calc.ttr) * int(calc.ttr * 1e9)

    def doReadDelay(self):
        # our delay is in s, entangle is in ns, in multiple of calc.ttr
        return self._dev.delay * 1e-9

    def doWriteDelay(self, value):
        # our delay is in s, entangle is in ns, in multiple of calc.ttr
        self.doStop()
        self.log.debug('set counter delay: %f s', value)
        value = int(value / calc.ttr) * int(calc.ttr * 1e9)
        self.log.debug('set counter delay: %d ns', value)
        self._dev.delay = value

    def doReadArray(self, quality):
        ndata = TOFChannel.doReadArray(self, quality)
        self.readresult = [d[2:self.monitorchannel].sum() +
                           d[self.monitorchannel + 1:].sum() for d in ndata]
        return ndata
