#  -*- coding: utf-8 -*-
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""KWS-3 flexible temperature controller."""

from __future__ import absolute_import

from nicos.core import Param, dictof, none_or, oneof, tangodev, tupleof
from nicos.devices.generic.paramdev import ParamDevice
from nicos.devices.tango import TemperatureController
from nicos.pycompat import iteritems

# out-dev, (in-dev, min-out, max-out, init-pid) if software-regulated
entry = tupleof(tangodev, none_or(tupleof(tangodev, float, float, float, float, float)))



class FlexRegulator(TemperatureController):
    """Temperature controller with varying setup for software and hardware
    regulation."""

    parameters = {
        'dummy':   Param('Dummy input device', type=tangodev, mandatory=True),
        'configs': Param('Possible setups', type=dictof(str, entry), mandatory=True),
        'config':  Param('Current configuration', type=str, volatile=True,
                         settable=True),
    }

    def doReadConfig(self):
        props = self._dev.GetProperties()
        indev = props[props.index('indev') + 1]
        outdev = props[props.index('outdev') + 1]
        for (cfgname, config) in iteritems(self.configs):
            if config[0] == outdev:
                if config[1] is None:
                    if indev == self.dummy:
                        return cfgname
                elif indev == config[1][0]:
                    return cfgname
        return '<unknown>'

    def doWriteConfig(self, value):
        cfg = self.configs[value]
        props = ['outdev', cfg[0]]
        if cfg[1]:
            indev, outmin, outmax, initp, initi, initd = cfg[1]
            props += ['indev', indev, 'software', 'True',
                      'outmin', str(outmin), 'outmax', str(outmax),
                      'initpid', '[%s, %s, %s]' % (initp, initi, initd)]
        else:
            props += ['indev', self.dummy, 'software', 'False']
        self._dev.SetProperties(props)


class ConfigParamDevice(ParamDevice):
    def doInit(self, mode):
        ParamDevice.doInit(self, mode)
        self.valuetype = oneof(*self._attached_device.configs)
