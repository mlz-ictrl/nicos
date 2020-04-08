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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS integration for GE detector."""

from __future__ import absolute_import, division, print_function

import time

import PyTango

from nicos import session
from nicos.core import Attach, Moveable, NicosTimeoutError, Override, Param, \
    dictof, status, tupleof, usermethod
from nicos.devices.epics import EpicsAnalogMoveable, EpicsReadable
from nicos.devices.generic.sequence import BaseSequencer, SeqMethod, SeqSleep
from nicos.devices.generic.switcher import Switcher
from nicos.devices.tango import PowerSupply
from nicos.pycompat import iteritems


class HVSwitcher(Switcher):
    """Override precision to work with lists.

    Also sets all relevant PV values on the eight-packs when starting the
    detector.
    """

    hardware_access = True

    parameters = {
        'pv_values': Param('PV values to set when starting the detector',
                           type=dictof(str, list), mandatory=True),
    }

    def _mapReadValue(self, pos):
        prec = self.precision
        for name, value in iteritems(self.mapping):
            if prec:
                if all(abs(p - v) <= prec for (p, v) in zip(pos, value)):
                    return name
            elif pos == value:
                return name
        return self.fallback

    def doTime(self, old, new):
        if old != new:
            session.clock.tick(90)
        return 0

    def doStart(self, target):
        # on start, also set all configured parameters
        if target == 'on' and self.read() != 'on':
            self.transferSettings()
        Switcher.doStart(self, target)

    @usermethod
    def transferSettings(self):
        import epics
        for epicsid, pvs in iteritems(self.pv_values):
            for pvname, pvvalue in pvs:
                fullpvname = '%s:%s_W' % (epicsid, pvname)
                self.log.debug('setting %s = %s' % (fullpvname, pvvalue))
                epics.caput(fullpvname, pvvalue)
        session.delay(2)


class MultiHV(BaseSequencer):
    """On/off switch for the GE detector high voltage.

    This is not a MultiSwitcher because it has to ramp the voltage up/down
    slowly in predefined steps.

    Acceptable ramp: move 200 V, settle for 1s.  At the end, settle for 30s.
    """

    attached_devices = {
        'ephvs':   Attach('Individual 8-pack HV', Moveable, multiple=True),
    }

    parameters = {
        'voltagestep': Param('Maximum voltage step ramping up', default=200),
        'stepsettle':  Param('Settle time between steps', default=2, unit='s'),
        'finalsettle': Param('Final settle time', default=30, unit='s'),
        # note: this should be <= the precision of the switcher above
        'offlimit':    Param('Limit under which HV is considered OFF',
                             default=24, unit='V'),
        'offtimeout':  Param('Timeout waiting for rampdown', default=900),
    }

    parameter_overrides = {
        'unit':    Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        self.valuetype = tupleof(*(int,) * len(self._attached_ephvs))

    def _generateSequence(self, target):
        seq = []
        current = [int(dev.read(0)) for dev in self._attached_ephvs]

        if all(v == 0 for v in target):
            # shut down without ramp via capacitors
            subseq = []
            for (i, dev) in enumerate(self._attached_ephvs):
                if current[i] <= 10:
                    continue
                subseq.append(SeqMethod(dev, 'start', 0))
            if subseq:
                seq.append(subseq)
                seq.append(SeqMethod(self, '_wait_for_shutdown'))

        else:
            while True:
                subseq = []
                for (i, dev) in enumerate(self._attached_ephvs):
                    if target[i] - 5 <= current[i] <= target[i] + 10:
                        continue
                    if target[i] > current[i]:
                        setval = min(current[i] + self.voltagestep, target[i])
                    elif target[i] < current[i]:
                        setval = max(current[i] - self.voltagestep, target[i])
                    subseq.append(SeqMethod(dev, 'start', setval))
                    current[i] = setval
                if not subseq:
                    break
                seq.extend(subseq)
                seq.append(SeqSleep(self.stepsettle))
            # final settle
            if seq:
                seq.append(SeqSleep(self.finalsettle))
        return seq

    def _wait_for_shutdown(self):
        timeout = time.time() + self.offtimeout
        while time.time() < timeout:
            time.sleep(1)
            for dev in self._attached_ephvs:
                if dev.read(0) > self.offlimit:
                    break
            else:
                return
        raise NicosTimeoutError(self, 'timeout waiting for HV to ramp down')

    def doRead(self, maxage=None):
        return [d.read(0) for d in self._attached_ephvs]


class GEPowerSupply(PowerSupply):
    """Special power supply that will switch on the device if it is OFF.

    This is necessary because when tripped (by sense or by temperature interlock),
    the Toellner supply outputs are switched off.

    Conversely, when setting voltage to zero, the device is switched OFF.
    """

    def doStart(self, value):
        if value != 0 and self._dev.State() == PyTango.DevState.OFF:
            self._dev.On()
            PowerSupply.doStart(self, value)
        elif value == 0:
            self._dev.Off()


class HVEpicsAnalogMoveable(EpicsAnalogMoveable):

    def doStatus(self, maxage=None):
        # HV writepv intermittently goes into unknown state, ignore it
        code, text = EpicsAnalogMoveable.doStatus(self, maxage)
        if code == status.UNKNOWN:
            code, text = status.OK, ''
        return code, text


class HVEpicsArrayReadable(EpicsReadable):
    def doRead(self, maxage=0):
        return self._get_pv('readpv')[:8].tolist()
