#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Detector for triggering dynamic light scattering (DLS) during counting."""

import time

from nicos import session
from nicos.core import Measurable, Param
from nicos.devices.tango import PyTangoDevice


class DLSSync(PyTangoDevice, Measurable):
    """A measurable device that triggers a DLS measurement while the main
    detector is counting.

    For this purpose, a string is sent via serial interface (a Tango StringIO)
    to the DLS software, which by itself starts a series of measurements
    """

    parameters = {
        'duration': Param('Duration of one DLS measurement', type=float,
                          unit='s', default=300, settable=True),
    }

    _meastime = 0

    def doSetPreset(self, **preset):
        self._meastime = preset.get('t')

    def doStart(self):
        try:
            sampletemp = 0
            if 'Ts' in session.devices:
                tdev = session.getDevice('Ts')
                if tdev.alias:
                    sampletemp = tdev.read() or 0
            sampleno = session.getDevice('Sample').samplenumber
            counters = session.data.getCounters()
            dlsstring = '%s,%d,%d,%d,%f,%d,%d' % (
                session.experiment.proposal,
                counters.get('pointcounter', 0),
                sampleno or 0,
                time.time(),
                sampletemp,
                self._meastime,
                self.duration,
            )
            self._dev.WriteLine(dlsstring)
        except Exception:
            # make this non-fatal
            self.log.warning('could not send DLS sync string', exc=1)

    def valueInfo(self):
        # no usable values returned
        return ()

    def doRead(self, maxage=0):
        return []

    def doStop(self):
        # stopping is not possible
        pass

    def doFinish(self):
        pass
