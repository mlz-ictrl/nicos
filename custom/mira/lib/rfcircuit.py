#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Agilent wave generator classes."""

from time import sleep

from nicos.core import status, oneof, HasLimits, Moveable, Readable, Param, \
    Override, MASTER, Attach
from nicos.devices.taco import AnalogOutput
from nicos.utils import createThread


class GeneratorDevice(AnalogOutput):
    """RF generator frequency and amplitude device."""

    parameters = {
        'shape':  Param('Wave shape', type=oneof('sinusoid', 'square'),
                        settable=True, category='general'),
        'offset': Param('Offset of zero point', type=float, settable=True,
                        category='offsets'),
    }

    def doReadShape(self):
        return self._taco_guard(self._dev.deviceQueryResource, 'shape')

    def doReadOffset(self):
        return float(self._taco_guard(self._dev.deviceQueryResource, 'offset'))

    def doWriteShape(self, val):
        self._taco_update_resource('shape', val)

    def doWriteOffset(self, val):
        self._taco_update_resource('offset', str(val))


class RFCurrent(HasLimits, Moveable):
    """RF current device for controlling the RF amplitude due to changes in
    amplification in the RF amplifier with temperature.
    """

    attached_devices = {
        'amplitude': Attach('The frequency generator amplitude', Moveable),
        'readout':   Attach('The current readout', Readable),
    }

    parameters = {
        'rfcontrol':  Param('Whether to control the RF amplitude for a stable '
                            'current in the coils', type=bool, default=False,
                            settable=True),
        'kp':         Param('Proportionality constant between difference and '
                            'correction', type=float, default=0.005,
                            settable=True),
        'checktime':  Param('Time between control checks', type=float,
                            default=10., settable=True, unit='s'),
        'maxdelta':   Param('Maximum delta between read value and target value',
                            type=float, unit='%', default=5, settable=True),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False),
    }

    def doInit(self, mode):
        self._runthread = True

    def doShutdown(self):
        self._runthread = False

    def _setMode(self, mode):
        Moveable._setMode(self, mode)
        if mode == MASTER:
            self._rfthread = createThread('RF thread', self._rfcontrol)

    def doReadUnit(self):
        return self._attached_readout.unit

    def doStart(self, target):
        pass

    def doRead(self, maxage=0):
        return self._attached_readout.read(maxage)

    def doStatus(self, maxage=0):
        return status.OK, ''

    def _rfcontrol(self):
        self.log.debug('RF control thread started')
        amp, cur = self._attached_amplitude, self._attached_readout
        while self._runthread:
            curamp = amp.read()
            while self.rfcontrol:
                sleep(self.checktime)
                curp2p = cur.read()
                p2p = self.target
                if abs(curp2p - p2p)/p2p > self.maxdelta/100.:
                    self.log.debug('P2P %.4f, should be %.4f' % (curp2p, p2p))
                    diff = curp2p - p2p
                    # negate diff: move in opposite direction of difference!
                    prevamp = curamp
                    nextamp = curamp = prevamp - diff * self.kp
                    ok, why = amp.isAllowed(nextamp)
                    if not ok:
                        self.log.warning('not setting new RF amplitude '
                                         '%s: %s' % (amp.format(nextamp),
                                                     why))
                        continue
                    self.log.debug('setting amplitude to %s (was %s)' %
                                   (amp.format(nextamp),
                                    amp.format(prevamp)))
                    amp.move(nextamp)
            while not self.rfcontrol:
                sleep(self.checktime)
