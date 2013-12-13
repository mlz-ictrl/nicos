#  -*- coding: utf-8 -*-
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
#   Jens Krueger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Class for the NOK (Neutronen optischer Körper) of the REFSANS instrument
"""

import math

from nicos.core import Moveable, Param, Override, Value, \
     oneof, tupleof, multiStatus, multiWait, multiReset
from nicos.devices.generic import Axis

class NOK(Moveable):

    valuetype = tupleof(float, float)

    hardware_access = False

    attached_devices = {
        'left': (Axis, 'left axis'),
        'right': (Axis, 'right axis'),
    }

    parameters = {
        'opmode': Param('Mode of operation for the NOK',
                        type=oneof('2axis', 'incline',),
                        settable=True, default='2axis',
                       ),
        'length': Param('Length of the neutron guide of the NOK',
                        type=float, settable=False, mandatory=True,
                       ),
        'ldist': Param('Left distance from neutron guide to axis',
                       type=float, settable=False, mandatory=True,
                      ),
        'rdist': Param('Right distance from neutron guide to axis',
                       type=float, settable=False, mandatory=True,
                      ),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.2f, %.2f'),
        'unit': Override(mandatory=False),
    }

    def doInit(self, mode):
        self._axes = [self._adevs['left'], self._adevs['right'],]
        self._axnames = ['left', 'right',]

        for name in self._axnames:
            self.__dict__[name] = self._adevs[name]

        self._distance = self.length - (self.ldist + self.rdist)

    def doIsAllowed(self, target):
        return self._doIsAllowedPositions(target)

    def _getPositions(self, target):
        tl, tr = target
        if self.opmode == 'incline':
            dx = self.length * math.tan(math.pi * tr / 180)
            self.log.debug(self, 'inclination is %.5f' % dx)
            tr = tl + dx
        tdx = tr - tl
        cl = tl + tdx * self.ldist / self.length
        cr = tr - tdx * self.rdist / self.length
        return (cl, cr)

    def _doIsAllowedPositions(self, positions):
        targets = self._getPositions(positions)
        for ax, axname, pos in zip(self._axes, self._axnames, targets):
            self.log.debug(ax, 'check for allowed position: %.3f' % pos)
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, '[%s axis] %s' % (axname, why)
        return True, ''

    def doStart(self, target):
        cl, cr = self._getPositions(target)
        self.log.debug(self, 'move axis to (%.2f, %.2f)' % (cl, cr))
        al, ar = self._axes
        al.move(cl)
        ar.move(cr)

    def doRead(self, maxage=0):
        cl, cr = [d.read(maxage) for d in self._axes]
        self.log.debug(self, 'read axis from (%.2f, %.2f)' % (cl, cr))
        dx = cr - cl
        self.log.debug(self, 'read axis from (%.2f)' % (dx))
        dxr = dx * self.rdist / self._distance
        dxl = dx * self.ldist / self._distance
        self.log.debug(self, 'read axis from (%.2f, %.2f)' % (dxl, dxr))
        cl -= dxl
        if self.opmode == 'incline':
            cr = 180 * math.atan2(dx, self._distance) / math.pi
        else:
            cr += dxr
        return [cl, cr]

    def doStatus(self, maxage=0):
        return multiStatus([('left', self._adevs['left']),
                            ('right', self._adevs['right'])], maxage)

    def doReset(self):
        multiReset(self._axes)
        multiWait(self._axes)

    def valueInfo(self):
        if self.opmode == 'incline':
            return Value('%s.start' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.incline' % self, unit='°', fmtstr='%.2f')
        else:
            return Value('%s.left' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.right' % self, unit=self.unit, fmtstr='%.2f')

    def doWriteOpmode(self, value):
        if value == 'incline':
            self.fmtstr = '%.2f, %.2f'
        else:
            self.fmtstr = '%.2f, %.2f'
        if self._cache:
            self._cache.invalidate(self, 'value')

