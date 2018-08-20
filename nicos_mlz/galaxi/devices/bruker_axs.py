# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""GALAXI Bruker AXS control"""

from nicos.core import Waitable, status
from nicos.devices.tango import NamedDigitalInput, PartialDigitalInput


class TubeConditioner(NamedDigitalInput, Waitable):
    """Tube conditioning device of the GALAXI MetalJet X-ray source.

    Provides an additional command in order to calibrate the source by starting
    the tube conditioning."""

    def calibrate(self, time_span=None, wait=True):
        """Calibrates the X-ray source by starting the MetalJet tube
        conditioning and wait for its completion.

        If ``time_span`` is ``None`` calibration will start in any case.
        Otherwise the TANGO server will check if it is necessary within the
        next ``time_span`` hours.

        :param None or float time_span: the time_span to be checked
        :param bool wait: whether to wait for completion
        """
        conditioning = False
        if not time_span:
            self._dev.Condition()
        else:
            self._dev.MaybeCondition(time_span)
        if self.status(0)[0] == status.BUSY:
            self.log.info('tube conditioning started')
            conditioning = True
        if not conditioning:
            self.log.info('tube conditioning not necessary')
        elif wait:
            self.log.info('waiting for its completion ...')
            self.wait()
            self.log.info('tube conditioning completed')


class WaterCooler(PartialDigitalInput):
    """Device that shows possible water cooler errors of the x-ray source."""

    def doStatus(self, maxage=0):
        value = self.doRead(maxage)
        # status is ok if doRead() returned a string mapped on a non-zero value
        if self.mapping.get(value, value):
            return PartialDigitalInput.doStatus(self, maxage)
        # determine alarm reason(s)
        value = self._dev.value
        reason_dict = {0: 'pressure', 1: 'temperature', 2: 'flow rate',
                       4: 'conductance', 5: 'water level'}
        reason = ', '.join(reason_dict[bit] for bit in reason_dict
                           if not (value >> bit) & 1)
        if not reason:
            return status.UNKNOWN, 'error indicating bit set by mistake?'
        return status.WARN, 'reason(s): %s' % reason
