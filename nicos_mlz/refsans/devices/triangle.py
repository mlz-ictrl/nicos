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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Devices for the Trioptic autocollimator.

The 'Help' command on the serial line interface leads to the following output
which has to be considered as doc for the communication:

TRIOPTICS GmbH -- OptiAngle 5
-----------------------------
Please note. All commands are case sensitive.
Measurement Commands:
-----------------------------
Zero    [1|2]           Zero
Z       [1|2]           short format
Measure [1|2]           Measure
M       [1|2]           short format
Poll    [1|2]           Measure
P       [1|2]           short format
Tolerance               Tolerance
T                       short format
Capture                 Tolerance
Select Measure Programs:
-----------------------------
AutoCollimationAbsolute Select Measure Program AutoCollimation Absolute
ACA                     short format
AutoCollimation         Select Measure Program AutoCollimation
AC                      short format
Telescope               Select Measure Program Telescope
TE                      short format
WedgeAngle              Select Measure Program Wedge Angle
WA                      short format
WedgeRelative           Select Measure Program Wedge Relative
WR                      short format
Misc Commands:
-----------------------------
Unit    [ SEC | MINUTE | DEGREE | URAD | RAD | MM | PIXEL |
         INCH | MIL    |STRICH  ]
Help                    show this help message
"""

from nicos.core import Override, Param, Readable, floatrange, intrange, status
from nicos.core.errors import CommunicationError
from nicos.core.mixins import HasOffset
from nicos.devices.tango import StringIO


class TriangleBase(Readable, StringIO):

    def _read_controller(self, index):
        index = int(index)
        self.log.debug('_read_controller %s %d' % (type(index), index))
        res = self.communicate('P 1')
        self.log.debug('_read_controller res for %s' % res)
        res = res.split(';')
        self.log.debug('_read_controller res %s' % res)
        res = [float(e) for e in res]
        return res[index]


class TriangleMaster(TriangleBase):

    def doRead(self, maxage=0):
        try:
            res = self._read_controller(3)
            self.log.debug('pos: %f', res)
        except IndexError:
            res = 0
        return res

    def doStatus(self, maxage=0):
        try:
            sig = self._read_controller(3)
            if sig <= .01:
                return status.WARN, 'no signal'
            return status.OK, ''
        except CommunicationError:
            return status.ERROR, 'timeout check PC! SW running and COM-Port'


class TriangleAngle(HasOffset, TriangleMaster):

    parameters = {
        'index': Param('index of return',
                       type=intrange(0, 1), settable=False,
                       volatile=False, userparam=False),
    }

    parameter_overrides = {
        'offset': Override(type=floatrange(-2, 2)),
    }

    def doRead(self, maxage=0):
        try:
            self.log.debug('index: %d' % self.index)
            res = self._read_controller(self.index)
            res -= - self.offset
            self.log.debug('pos: %f' % res)
        except IndexError:
            res = 0
        return res
