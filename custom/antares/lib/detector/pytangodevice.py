# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************


from nicos.core import Param
from nicos.core import NicosError
from nicos.core import SIMULATION

import PyTango


class PyTangoDevice(object):

    parameters = {
        'tangodevice': Param('Tango device name', type=str,
                             mandatory=True, preinit=True)
    }

    def doPreinit(self, mode):
        self._dev = None

        # Don't create PyTango device in simulation mode
        if mode != SIMULATION:
            self._dev = self._createPyTangoDevice(self.tangodevice)

    def _createPyTangoDevice(self, address):
        device = self._tangoFuncGuard(PyTango.DeviceProxy, address)
        return device

    def _tangoGetAttrGuard(self, attr):
        self.log.debug('Get PyTango attribute: %s' % attr)
        result = self._tangoFuncGuard(self._dev.__getattr__, attr)
        self.log.debug('\t=> %s' % str(result))

        return result

    def _tangoSetAttrGuard(self, attr, value):
        self.log.debug('Set PyTango attribute: %s => %s' % (attr, str(value)))
        self._tangoFuncGuard(self._dev.__setattr__, attr, value)

    def _tangoFuncGuard(self, func, *args):
        # logging of function name makes currently no sense as
        # all wrapped PyTango functions are called 'f'.
        # self.log.debug('PyTango call: %s%r' % (func.__name__, args))
        try:
            return func(*args)
        except PyTango.DevFailed as e:
            self.log.debug('PyTango error: %s' % str(e[0].desc))
            # TODO: Map TANGO DevFailed exceptions?
            # It's not that easy as the tango exception
            # system is a bit intransparent and inconsistent.
            raise NicosError(e[0].desc)
