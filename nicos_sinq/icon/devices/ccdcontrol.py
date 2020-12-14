#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
from nicos.core import Attach, Moveable, Readable

from nicos_sinq.devices.detector import ControlDetector


class NIAGControl(ControlDetector):
    """"
    A detector control class which implements the NIAG CCD counting
    features:
    - restart counting when the countrate was to low
    """

    attached_devices = {
        'rate_monitor': Attach('Monitor to check rate against',
                               Readable),
        'rate_threshold': Attach('Threshold defining the minimum acceptable '
                                 'rate',
                                 Moveable),
        'exp_ok': Attach('Indication of sufficient exposure',
                         Readable),
    }
    _triggerFinished = None
    _start_time = None
    _stopped = False

    def doStart(self):
        self._start_time = time.time()
        self._stopped = False
        ControlDetector.doStart(self)

    def doStop(self):
        self._stopped = True
        ControlDetector.doStop(self)

    def _testRate(self):
        mon = self._attached_rate_monitor.read(0)
        thres = self._attached_rate_threshold.read(0)
        exp_ok = self._attached_exp_ok.read(0)
        if isinstance(mon, list):
            mon = mon[0]
        if exp_ok != 1:
            session.log.info('%s, should be > %d uA, is %f uA',
                             'Restarting because of insuffient count rate',
                             thres, mon)
            self.start()
            return False
        self._start_time = None
        return True

    def doIsCompleted(self):
        ret = ControlDetector.doIsCompleted(self)
        if ret and self._start_time and not self._stopped:
            return self._testRate()
        return ret

    def doRead(self, maxage=0):
        res = [self._attached_trigger.read(maxage)]
        for det in self._attached_slave_detectors:
            res = res.append(det.read(maxage))
        return res
