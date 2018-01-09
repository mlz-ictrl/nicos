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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************
"""Special device for Sans1 Tisane triggering or mieze on Reseda"""

from nicos.core import Param, Override, Moveable, dictof, oneof, status

from nicos.devices.tango import PyTangoDevice


class Trigger(PyTangoDevice, Moveable):
    """sends a preconfigured string upon move to the configured StringIO"""
    parameters = {
        'strings': Param('mapping of nicos-value to pre-configured string',
                         type=dictof(str, str), settable=True, unit=''),
        'safesetting': Param('selection of a \'safe\' setting',
                             type=str, settable=True, unit=''),
    }
    parameter_overrides = {
        'unit' : Override(default='', mandatory=False),
    }

    def doInit(self, mode):
        self.valuetype = oneof(*self.strings.keys())
        if self.target not in self.strings:
            self._setROParam('target', self.safesetting)

    def doStart(self, value):
        self._dev.WriteLine(self.strings[value])
        self._dev.Flush()

    def doStatus(self, maxage=0):
        return status.OK, 'indeterminate'

    def read(self, maxage=0):
        # fix bad overwrite from StringIO
        return Moveable.read(self, maxage)

    def doRead(self, maxage=0):
        # no way to read back!
        return self.target
