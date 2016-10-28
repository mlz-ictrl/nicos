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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Motor device via the CARESS device service."""

from nicos import session
from nicos.core import HasOffset, Override, POLLER, Param
from nicos.core.errors import NicosError
from nicos.devices.abstract import Motor as AbstractMotor
from nicos.devices.vendor.caress.base import Driveable
from nicos.devices.vendor.caress.core import CARESS, INIT_REINIT, OFF_LINE

EKF_44520_ABS = 114  # EKF 44520 motor control, abs. encoder, VME
EKF_44520_INCR = 115  # EKF 44520 motor control, incr. encoder, VME


class Motor(HasOffset, Driveable, AbstractMotor):
    """Device accessing the CARESS axes with and without encoder."""

    hardware_access = True

    parameters = {
        'coderoffset': Param('Encoder offset',
                             type=float, default=0., unit='main',
                             settable=True, category='offsets', chatty=True,
                             ),
        'gear': Param('Ratio between motor and encoder',
                      type=float, default=1.0, settable=False,
                      ),
    }

    parameter_overrides = {
        'precision': Override(default=0.01)
    }

    def doInit(self, mode):
        Driveable.doInit(self, mode)
        self._set_speed(self.config)

    def doStart(self, target):
        Driveable.doStart(self, target + (self.coderoffset + self.offset))

    def doRead(self, maxage=0):
        raw = Driveable.doRead(self, maxage)
        if raw is None and session.sessiontype == POLLER:
            return None
        return raw - (self.coderoffset + self.offset)

    def doSetPosition(self, pos):
        pass

    def _set_speed(self, config):
        tmp = config.split()
        # The  7th entry is the number of motor steps and the  6th entry the
        # number of encoder steps.  The ratio between both gives the speed of
        # the axis. It must be multiplied by the gear.
        if len(tmp) > 1:
            if int(tmp[1]) == EKF_44520_ABS and len(tmp) > 6:
                speed = self.gear * float(tmp[6]) / float(tmp[5])
                self._params['speed'] = speed
                if self._cache:
                    self._cache.put(self, 'speed', speed)

    def doWriteSpeed(self, speed):
        tmp = self.config.split()
        # In case of using an EKF module the speed could be set
        # The speed will be calculated in respect to the number of coder values
        # per unit tmp[5] value and set into tmp[6] value. The new
        # configuration line will be send to the CARESS device driver to reinit
        # this module
        if len(tmp) > 1:
            if int(tmp[1]) == EKF_44520_ABS and len(tmp) > 6:
                sp = int(float(tmp[5]) * speed / self.gear)
                tmp[6] = '%d' % sp
                # the acceleration value should be roughly 1/10th of the speed
                tmp[7] = '%d' % (sp / 10)
                _config = ' '.join(tmp)
                res = self._caressObject.init_module(INIT_REINIT, self.cid,
                                                     _config)
                if res[0] not in (0, CARESS.OK) or res[1] == OFF_LINE:
                    raise NicosError(self, 'Could not set speed to module!'
                                     '(%r) %d' % ((res,), self._device_kind()))
        self._params['speed'] = speed
