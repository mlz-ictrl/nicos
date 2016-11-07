#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS integration for GE detector."""

import time

from nicos.core import Moveable, Attach, Param, Override, tupleof, dictof
from nicos.devices.generic.sequence import BaseSequencer, SeqMethod, SeqSleep
from nicos.devices.generic.switcher import Switcher
from nicos.pycompat import iteritems


class HVSwitcher(Switcher):
    """Override precision to work with lists.

    Also sets all relevant PV values on the eight-packs when starting the
    detector.
    """

    parameters = {
        'pv_values': Param('PV values to set when starting the detector',
                           type=dictof(str, list), mandatory=True),
    }

    hardware_access = True

    def _mapReadValue(self, pos):
        prec = self.precision
        for name, value in iteritems(self.mapping):
            if prec:
                if all(abs(p - v) <= prec for (p, v) in zip(pos, value)):
                    return name
            elif pos == value:
                return name
        return self.fallback

    def doStart(self, target):
        # on start, also set all configured parameters
        if target == 'on' and self.read() != 'on':
            import epics
            for epicsid, pvs in iteritems(self.pv_values):
                for pvname, pvvalue in pvs:
                    fullpvname = '%s:%s_W' % (epicsid, pvname)
                    self.log.debug('setting %s = %s' % (fullpvname, pvvalue))
                    epics.caput(fullpvname, pvvalue)
            time.sleep(2)
        Switcher.doStart(self, target)


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
        'voltagestep': Param('Maximum step in voltage', default=200),
        'stepsettle':  Param('Settle time between steps', default=2, unit='s'),
        'finalsettle': Param('Final settle time', default=30, unit='s'),
    }

    parameter_overrides = {
        'unit':    Override(mandatory=False, default=''),
    }

    def doInit(self, mode):
        self.valuetype = tupleof(*(int,) * len(self._attached_ephvs))

    def _generateSequence(self, target):  # pylint: disable=arguments-differ
        seq = []
        current = [int(dev.read(0)) for dev in self._attached_ephvs]

        while True:
            subseq = []
            for (i, dev) in enumerate(self._attached_ephvs):
                if abs(target[i] - current[i]) <= 2:
                    continue
                if target[i] > current[i]:
                    setval = min(current[i] + self.voltagestep, target[i])
                elif target[i] < current[i]:
                    setval = max(current[i] - self.voltagestep, target[i])
                # XXX: only one step with all starts
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

    def doRead(self, maxage=None):
        return [d.read(0) for d in self._attached_ephvs]
