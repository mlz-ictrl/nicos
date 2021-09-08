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
"""
This file contains the code for operating the new collimator (as of 2020)
through a SPSS7. Though, in fact, it is run via EPICS, thus NICOS is
isolated from talking to the SPS directly.
"""

import time

from nicos.core import Attach, Override, status
from nicos.core.device import Moveable, Readable
from nicos.core.params import oneof
from nicos.devices.epics import EpicsDigitalMoveable
from nicos.devices.generic import Pulse


class SegmentPulse(Pulse):
    """
    This class also exposes the read() method of the underlying
    attached device for Pulse
    """
    def doRead(self, maxage=0):
        return self._attached_moveable.read(maxage)

    def doIsAtTarget(self, pos, target):
        return True


class SegmentMoveable(EpicsDigitalMoveable):
    """
    Just overload isAtTarget() which makes no sense if you
    wish to pulse. Suppresses a confusing and unnecessary
    warning
    """
    def doIsAtTarget(self, pos, target):
        return True


class Segment(Moveable):
    """
    This class controls a SANS collimator segment through a
    host of attached slave devices
    """

    attached_devices = {
        'hand': Attach('Switch into remote mode',
                       Moveable),
        'ble': Attach('Switch to BLE position',
                      Moveable),
        'nl': Attach('Switch to NL position',
                     Moveable),
        'zus': Attach('Switch to ZUS position',
                      Moveable),
        'mot_error': Attach('Test motor errror',
                            Readable),
        'seq_error': Attach('Test sequence error',
                            Readable),
        'bolt_error': Attach('Test bolt error',
                             Readable),
        'mot_fast': Attach('Motor fast',
                           Readable),
        'mot_slow': Attach('Motor slow',
                           Readable)
    }
    valuetype = oneof('ble', 'nl', 'zus')

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    _target = None
    _start_time = None

    def doInit(self, mode):
        self._target = self.read(0)
        self._attached_hand.start(1)

    def doRead(self, maxage=0):
        if self._attached_ble.read(maxage) == 1:
            return 'ble'
        if self._attached_nl.read(maxage) == 1:
            return 'nl'
        if self._attached_zus.read(maxage) == 1:
            return 'zus'
        return 'transit'

    def _test_error(self):
        if self._attached_mot_error.read() == 1:
            return True, 'motor error'
        if self._attached_seq_error.read() == 1:
            return True, 'sequence error'
        if self._attached_bolt_error.read() == 1:
            return True, 'bolt error'
        return False, ''

    def doIsAllowed(self, pos):
        test, reason = self._test_error()
        if test:
            return False, reason
        return True, ''

    def doStart(self, target):
        # Will only need to be done once (or someone messes with the rack)
        if self._attached_hand.read(0) == 0:
            self._attached_hand.start(1)
        self._target = target
        if target == self.doRead(0):
            return
        self._start_time = time.time()
        if target == 'ble':
            self._attached_ble.start(1)
        elif target == 'nl':
            self._attached_nl.start(1)
        elif target == 'zus':
            self._attached_zus.start(1)

    def doStatus(self, maxage=0):
        test, reason = self._test_error()
        if test:
            return status.ERROR, \
                   'Collimator SPS broken with %s, reset manually' % reason
        pos = self.doRead(maxage)
        if pos == self._target:
            return status.OK, ' '
        else:
            if time.time() > self._start_time + 360:
                return status.ERROR, 'Timeout moving segment'
            if self._attached_mot_fast.read(maxage) == 1:
                return status.BUSY, 'Moving fast'
            if self._attached_mot_slow.read(maxage) == 1:
                return status.BUSY, 'Moving slow'
            return status.BUSY, 'Locking/Unlocking'


class Polariser(Moveable):
    """
    The polariser is in when segment 1 is on zus, out else
    """

    attached_devices = {
        'cols1': Attach('Collimator segment 1',
                        Moveable),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }
    valuetype = oneof('in', 'out')

    def doRead(self, maxage=0):
        pos = self._attached_cols1.read(maxage)
        if pos == 'zus':
            return 'in'
        return 'out'

    def doStart(self, target):
        if target == 'in':
            self._attached_cols1.start('zus')
        else:
            self._attached_cols1.start('nl')

    def doStatus(self, maxage=0):
        return self._attached_cols1.status(maxage)


class Collimator(Moveable):
    """
    This class coordinates the collimator segments in order to realize
    different collimator settings.
    """

    attached_devices = {
        'segments': Attach('The individual collimator segments',
                           Moveable, multiple=7),
    }

    _steps = [18, 15, 11, 8, 6, 4.5, 3, 2]

    def doIsAllowed(self, pos):
        if pos in self._steps:
            pol = self._attached_segments[0].read(0)
            if pol == 'zus' and pos == 18:
                return False, '18m not allowed with polariser "in"'
            return True, ''
        return False, '%s NOT allowed, choose one of %s' \
            % (pos, ','.join(map(str, self._steps)))

    def doRead(self, maxage=0):
        for idx, seg in enumerate(self._attached_segments):
            pos = seg.read(maxage)
            if pos == 'ble':
                if all(seg.read() == 'ble' for seg in
                        self._attached_segments[idx:]):
                    return self._steps[idx]
                return 'unknown position'
            if pos == 'transit':
                return 'transit position'
        return self._steps[-1]

    def doStart(self, target):
        # what if colsX is was moved independently?
        for idx, step in enumerate(self._steps):
            if idx == 0 and self._attached_segments[0].read(0) == 'zus':
                # leave polariser alone
                continue
            if idx == 7:
                break
            if target < step:
                self._attached_segments[idx].start('nl')
            else:
                self._attached_segments[idx].start('ble')
