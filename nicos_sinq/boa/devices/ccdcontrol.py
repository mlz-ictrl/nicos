#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
import time

from nicos import session
from nicos.core import Param, nicosdev

from nicos_sinq.devices.detector import ControlDetector


class BoaControlDetector(ControlDetector):
    """"
    A detector control class which implements the BOA CCD counting specific
    features:
    - delay start of the el737 after starting the CCD
    - restart counting when the countrate was to low
    - abort and restart when the CCD does not finish timely after the el737
      finished
    """

    parameters = {
        'minimum_rate': Param('Minimum count rate for frame',
                              type=int,
                              settable=True,
                              mandatory=True),
        'rate_monitor': Param('Monitor to check rate against',
                              type=nicosdev,
                              mandatory=True),
        'elapsed_time': Param('Channel to read time from',
                              type=nicosdev,
                              mandatory=True)
    }

    _triggerFinished = None

    def doStart(self):
        self._triggerFinished = None
        if self._attached_slave_detectors:
            self._attached_slave_detectors[0].start()
        time.sleep(.5)
        # session.log.info('Started CCD\n')
        self._attached_trigger.start()
        # session.log.info('Started Trigger\n')

    def _testRate(self):
        dev = session.getDevice(self.rate_monitor)
        mon = dev.read(0)[0]
        dev = session.getDevice(self.elapsed_time)
        t = dev.read(0)[0]
        if mon < t * self.minimum_rate:
            session.log.info('%s, should %d cts/sec, is %f cts/dec',
                             'Restarting because of insuffient count rate',
                             self.minimum_rate, float(mon)/float(t))
            self.start()
            return False
        else:
            return True

    def doIsCompleted(self):
        if not self._triggerFinished:
            if self._attached_trigger.isCompleted():
                # session.log.info('Trigger finished\n')
                self._triggerFinished = time.time()
                # This is needed with the AD simulation as it is not controlled
                # by the counter box
                # self._attached_slave_detectors[0].stop()
                return False
        else:
            if all(det.isCompleted for det in self._attached_detectors):
                return self._testRate()
            else:
                if time.time() > self._triggerFinished + 180:
                    session.log.info('CCD overrun, restarting counting...')
                    self.stop()
                    start = time.monotonic()
                    while time.monotonic() - start < 200:
                        time.sleep(1.)
                        if self._attached_slave_detectors[0].isCompleted():
                            break
                    self.start()
                return False
