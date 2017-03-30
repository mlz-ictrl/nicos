# -*- coding: utf-8 -*-
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
#   Fabian Beule <f.beule@fz-juelich.de>
#
# *****************************************************************************

"""Devices for Janitza power quality monitors"""

from nicos.core import Readable, Param, Attach, Override, listof, status
from nicos.devices.tango import AnalogInput


# Helper classes:

class BaseInput(AnalogInput):
    """Base class for the different Janitza online values"""

    parameters = {
        'variables': Param('Variables that are internally read', listof(str)),
    }

    def _GetListProperty(self, name):
        s = self._getProperty(name)
        if s == '[]':
            return []
        else:
            return s[1:-1].split(', ')

    def doReadVariables(self):
        return self._GetListProperty('variables')


class SpecialInput(BaseInput):
    """Base class for devices with a scalar 'limit' property"""

    parameters = {
        'limit': Param('Alarm limit', float, settable=True),
    }

    def doReadLimit(self):
        return float(self._getProperty('limit'))

    def doWriteLimit(self, value):
        self._dev.SetProperties(['limit', str(value)])
        return self.doReadLimit()


# Tango devices:

class VectorInput(BaseInput):
    """Vector input with high and low alarm limits"""

    parameters = {
        'limitmin':  Param('Low alarm limit', listof(float), settable=True),
        'limitmax': Param('High alarm limit', listof(float), settable=True),
    }

    def doReadLimitmin(self):
        return map(float, self._GetListProperty('limitmin'))

    def doWriteLimitmin(self, value):
        self._dev.SetProperties(['limitmin', str(value)])
        return self.doReadLimitmin()

    def doReadLimitmax(self):
        return map(float, self._GetListProperty('limitmax'))

    def doWriteLimitmax(self, value):
        self._dev.SetProperties(['limitmax', str(value)])
        return self.doReadLimitmax()


class Neutral(SpecialInput):
    parameter_overrides = {
        'limit': Override(description='Max difference of neutral and summed current')
    }


class RCM(SpecialInput):
    parameter_overrides = {
        'limit': Override(description='Max quotient of residual current and power')
    }


class Leakage(SpecialInput):
    parameter_overrides = {
        'limit': Override(description='Max difference of PE and differential current')
    }


class OnlineMonitor(Readable):
    """Combines all relevant online values for an instrument"""

    attached_devices = {
        'voltages': Attach('Voltages U_L1, U_L2, U_L3',
                           Readable, multiple=True, optional=True),
        'currents': Attach('Currents I_L1, I_L2, I_L3, I_L4, I_L5',
                           Readable, multiple=True, optional=True),
        'neutral':  Attach('Neutral Currents I_N, I_sum',
                           Readable, multiple=True, optional=True),
        'rcm':      Attach('Residual Currents I_L5, I_L6, S_sum',
                           Readable, multiple=True, optional=True),
        'leakage':  Attach('Ground leakage I_L5, I_L6',
                           Readable, multiple=True, optional=True),
        'thd':      Attach('Total harmonic distortion THD_I_L1, THD_I_L2, '
                           'THD_I_L3', Readable, multiple=True, optional=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
    }

    valuetype = str

    def doRead(self, maxage=None):
        return self.status(maxage)[1]

    def doStatus(self, maxage=None):
        state = status.OK
        text = []
        for devlist in self._adevs.itervalues():
            if not isinstance(devlist, (list, tuple)):
                devlist = [devlist]
            for dev in devlist:
                if isinstance(dev, Readable):
                    devstate, devtext = dev.status(maxage)
                    if devstate != status.OK:
                        devname = dev.name
                        if devname.startswith(self.name + '_'):
                            devname = devname[len(self.name) + 1:]
                        text.append('%s: %s' % (devname, devtext))
                        state = max(state, devstate)
        if len(text) > 0:
            text = ', '.join(text)
        else:
            text = 'OK'
        return state, text
