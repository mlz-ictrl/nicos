#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""NICOS slit device."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

from nicos import status
from nicos.utils import oneof
from nicos.device import Moveable, Param, Override
from nicos.errors import UsageError, LimitError
from nicos.abstract import Axis


class Slit(Moveable):
    """A rectangular slit consisting of four blades."""

    attached_devices = {
        'right': Moveable,
        'left': Moveable,
        'bottom': Moveable,
        'top': Moveable,
    }

    parameters = {
        'opmode': Param('Mode of operation for the slit',
                        type=oneof(str, '4blades', 'centered', 'offcentered'),
                        settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.2f %.2f %.2f %.2f'),
        'unit': Override(mandatory=False),
    }

    def doInit(self):
        self._axes = [self._adevs['right'], self._adevs['left'],
                      self._adevs['bottom'], self._adevs['top']]
        self._axnames = ['right', 'left', 'bottom', 'top']

    def _getPositions(self, target):
        if self.opmode == '4blades':
            if len(target) != 4:
                raise UsageError(self, 'arguments required for 4-blades mode: '
                                 '[xmin, xmax, ymin, ymax]')
            positions = list(target)
        elif self.opmode == 'centered':
            if len(target) != 2:
                raise UsageError(self, 'arguments required for centered mode: '
                                 '[width, height]')
            positions = [-target[0]/2., target[0]/2.,
                         -target[1]/2., target[1]/2.]
        else:
            if len(target) != 4:
                raise UsageError(self, 'arguments required for offcentered mode: '
                                 '[xcenter, ycenter, width, height]')
            positions = [target[0] - target[2]/2., target[0] + target[2]/2.,
                         target[1] - target[3]/2., target[1] + target[3]/2.]
        return positions

    def doIsAllowed(self, target):
        positions = self._getPositions(target)
        for ax, axname, pos in zip(self._axes, self._axnames, positions):
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, '%s blade: %s' % (axname, why)
        if positions[1] < positions[0]:
            return False, 'horizontal slit opening is negative'
        if positions[3] < positions[2]:
            return False, 'vertical slit opening is negative'
        return True, ''

    def doStart(self, target):
        # determine which axes to move first, so that the blades can
        # not touch when one moves first
        tr, tl, tb, tt  = self._getPositions(target)
        cr, cl, cb, ct = map(lambda d: d.doRead(), self._axes)
        ar, al, ab, at = self._axes
        if tr < cr and tl < cl:
            # both move to smaller values, need to start right blade first
            ar.move(tr)
            sleep(0.25)
            al.move(tl)
        elif tr > cr and tl > cl:
            # both move to larger values, need to start left blade first
            al.move(tl)
            sleep(0.25)
            ar.move(tr)
        else:
            # don't care
            al.move(tl)
            ar.move(tr)
        if tb < cb and tt < ct:
            ab.move(tb)
            sleep(0.25)
            at.move(tt)
        elif tb > cb and tt > ct:
            at.move(tt)
            sleep(0.25)
            ab.move(tb)
        else:
            at.move(tt)
            ab.move(tb)

    def doReset(self):
        for ax in self._axes:
            ax.reset()

    def doWait(self):
        for ax in self._axes:
            ax.wait()

    def doStop(self):
        for ax in self._axes:
            ax.stop()

    def doRead(self):
        positions = map(lambda d: d.read(), self._axes)
        r, l, b, t = positions
        if self.opmode == 'centered':
            # XXX motor must have precision for this!
            #if abs((l+r)/2) > self._adevs['left'].precision or \
            #   abs((t+b)/2) > self._adevs['top'].precision:
            #    self.printwarning('slit seems to be offcentered, but is set to '
            #                      '"centered" mode')
            return (l-r, t-b)
        elif self.opmode == 'offcentered':
            return ((l+r)/2, (t+b)/2, l-r, t-b)
        else:
            return tuple(positions)

    def doStatus(self):
        svalues = map(lambda d: d.status(), self._axes)
        return max(s[0] for s in svalues), 'axis status: ' + \
               ', '.join('%s=%s' % (s[1], n)
                         for (s, n) in zip(svalues, self._axnames))

    def doReadUnit(self):
        return self._adevs['left'].unit
    
    def doWriteOpmode(self, value):
        if value in ('4blades', 'offcentered'):
            self.fmtstr = '%.2f %.2f %.2f %.2f'
        else:
            self.fmtstr = '%.2f %.2f'
