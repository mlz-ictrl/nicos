# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Lukas Vogl <lukas.vogl@frm2.tum.de>
#
# *****************************************************************************

"""Support classes for the CCR compressors"""

from nicos.core import SIMULATION, Param, tangodev
from nicos.utils import HardwareStub
from nicos.devices.entangle import NamedDigitalOutput


class F70ColdheadController(NamedDigitalOutput):

    parameters = {
        'ophours_device': Param('coldhead compressor operation hours device',
                        type=tangodev, mandatory=True, preinit=True, userparam=False),
        'p_return_device': Param('coldhead compressor return pressure device',
                        type=tangodev, mandatory=True, preinit=True, userparam=False),
        't_compr_device': Param('coldhead compressor temperature device',
                        type=tangodev, mandatory=True, preinit=True, userparam=False),
        't_water_in_device': Param('coldhead compressor water outlet temperature device',
                        type=tangodev, mandatory=True, preinit=True, userparam=False),
        't_water_out_device': Param('coldhead compressor water inlet temperature device',
                        type=tangodev, mandatory=True, preinit=True, userparam=False),
        'ophours': Param('coldhead compressor operation hours',
                        type=float,userparam=True, volatile=True),
        'p_return': Param('coldhead compressor return pressure',
                        type=float,userparam=True, volatile=True),
        't_compr': Param('coldhead compressor temperature',
                        type=float,userparam=True, volatile=True),
        't_water_in': Param('coldhead compressor water outlet temperature',
                        type=float,userparam=True, volatile=True),
        't_water_out': Param('coldhead compressor water inlet temperature',
                        type=float,userparam=True, volatile=True),
    }

    _ophours = _p_return = _t_compr = _t_water_in = _t_water_out = None

    def doInit(self,mode):
        NamedDigitalOutput.doInit(self,mode)
        # Don't create PyTango device in simulation mode
        if mode != SIMULATION:
            self._ophours     = self._createPyTangoDevice(self.ophours_device)
            self._p_return    = self._createPyTangoDevice(self.p_return_device)
            self._t_compr     = self._createPyTangoDevice(self.t_compr_device)
            self._t_water_in  = self._createPyTangoDevice(self.t_water_in_device)
            self._t_water_out = self._createPyTangoDevice(self.t_water_out_device)
        else:
            self._ophours     = HardwareStub(self)
            self._p_return    = HardwareStub(self)
            self._t_compr     = HardwareStub(self)
            self._t_water_in  = HardwareStub(self)
            self._t_water_out = HardwareStub(self)


    def doReadOphours(self):
        return self._ophours.value

    def doReadP_Return(self):
        return self._p_return.value

    def doReadT_Compr(self):
        return self._t_compr.value

    def doReadT_Water_In(self):
        return self._t_water_in.value

    def doReadT_Water_Out(self):
        return self._t_water_out.value

    def doPoll(self, n, maxage):
        # the ccurrent sehw nicos version is old
        self._pollParam('ophours',self.maxage)
        self._pollParam('p_return',self.maxage)
        self._pollParam('t_compr',self.maxage)
        self._pollParam('t_water_in',self.maxage)
        self._pollParam('t_water_out',self.maxage)
