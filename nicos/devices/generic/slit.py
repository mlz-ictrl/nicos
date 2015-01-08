#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS slit device."""

from time import sleep

from nicos.core import oneof, Moveable, HasPrecision, Param, Value, Override, \
    AutoDevice, InvalidValueError, tupleof, multiStatus
from nicos.devices.abstract import CanReference


class Slit(CanReference, Moveable):
    """A rectangular slit consisting of four blades.

    The slit can operate in four "opmodes", controlled by the `opmode`
    parameter:

    * '4blades' -- all four blades are controlled separately.  Values read from
      the slit are lists in the order ``[left, right, bottom, top]``; for
      ``move()`` the same list of coordinates has to be supplied.
    * 'centered' -- only width and height are controlled; the slit is centered
      at the zero value of the left-right and bottom-top coordinates.  Values
      read and written are in the form ``[width, height]``.
    * 'offcentered' -- the center and width/height are controlled.  Values read
      and written are in the form ``[centerx, centery, width, height]``.

    Normally, the ``right`` and ``left`` as well as the ``bottom`` and ``top``
    devices need to share a common coordinate system, i.e. when ``right.read()
    == left.read()`` the slit is closed.  A different convention can be selected
    when setting `coordinates` to ``"opposite"``: in this case, the blades meet
    at coordinate 0, and both move in positive direction when they open.

    All instances have attributes controlling single dimensions that can be used
    as devices, for example in scans.  These attributes are:

    * `left`, `right`, `bottom`, `top` -- controlling the blades individually,
      independent of the opmode
    * `centerx`, `centery`, `width`, `height` -- controlling "logical"
      coordinates of the slit, independent of the opmode

    Example usage::

        >>> move(slit.centerx, 5)      # move slit center
        >>> scan(slit.width, 0, 1, 6)  # scan over slit width from 0 to 5 mm
    """

    attached_devices = {
        'left':   (HasPrecision, 'Left blade'),
        'right':  (HasPrecision, 'Right blade'),
        'bottom': (HasPrecision, 'Bottom blade'),
        'top':    (HasPrecision, 'Top blade'),
    }

    parameters = {
        'opmode': Param('Mode of operation for the slit',
                        type=oneof('4blades', 'centered', 'offcentered'),
                        settable=True),
        'coordinates': Param('Coordinate convention for left/right and '
                             'top/bottom blades', default='equal',
                             type=oneof('equal', 'opposite')),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%.2f %.2f %.2f %.2f'),
        'unit': Override(mandatory=False),
    }

    valuetype = tupleof(float, float, float, float)

    hardware_access = False

    def doInit(self, mode):
        self._axes = [self._adevs['left'], self._adevs['right'],
                      self._adevs['bottom'], self._adevs['top']]
        self._axnames = ['left', 'right', 'bottom', 'top']

        for name in self._axnames:
            self.__dict__[name] = self._adevs[name]

        for name, cls in [
            ('centerx', CenterXSlitAxis), ('centery', CenterYSlitAxis),
            ('width', WidthSlitAxis), ('height', HeightSlitAxis)]:
            self.__dict__[name] = cls(self.name+'.'+name, slit=self,
                                      unit=self.unit, lowlevel=True)

    def doShutdown(self):
        for name in ['centerx', 'centery', 'width', 'height']:
            if name in self.__dict__:
                self.__dict__[name].shutdown()

    def _getPositions(self, target):
        if self.opmode == '4blades':
            if len(target) != 4:
                raise InvalidValueError(self, 'arguments required for 4-blades '
                                        'mode: [left, right, bottom, top]')
            positions = list(target)
        elif self.opmode == 'centered':
            if len(target) != 2:
                raise InvalidValueError(self, 'arguments required for centered '
                                        'mode: [width, height]')
            positions = [-target[0]/2., target[0]/2.,
                         -target[1]/2., target[1]/2.]
        else:
            if len(target) != 4:
                raise InvalidValueError(self, 'arguments required for '
                                        'offcentered mode: [xcenter, ycenter, '
                                        'width, height]')
            positions = [target[0] - target[2]/2., target[0] + target[2]/2.,
                         target[1] - target[3]/2., target[1] + target[3]/2.]
        return positions

    def doIsAllowed(self, target):
        return self._doIsAllowedPositions(self._getPositions(target))

    def _isAllowedSlitOpening(self, positions):
        ok, why = True, ''
        if positions[1] < positions[0]:
            ok, why = False, 'horizontal slit opening is negative'
        elif positions[3] < positions[2]:
            ok, why = False, 'vertical slit opening is negative'
        return ok, why

    def _doIsAllowedPositions(self, positions):
        f = self.coordinates == 'opposite' and -1 or +1
        for ax, axname, pos in zip(self._axes, self._axnames, positions):
            if axname in ('left', 'bottom'):
                pos *= f
            ok, why = ax.isAllowed(pos)
            if not ok:
                return ok, '[%s blade] %s' % (axname, why)
        return self._isAllowedSlitOpening(positions)

    def doStart(self, target):
        self._doStartPositions(self._getPositions(target))

    def _doStartPositions(self, positions):
        f = self.coordinates == 'opposite' and -1 or +1
        tl, tr, tb, tt = positions
        # determine which axes to move first, so that the blades can
        # not touch when one moves first
        cl, cr, cb, ct = [d.read(0) for d in self._axes]
        cl *= f
        cb *= f
        al, ar, ab, at = self._axes
        if tr < cr and tl < cl:
            # both move to smaller values, need to start right blade first
            al.move(tl * f)
            sleep(0.25)
            ar.move(tr)
        elif tr > cr and tl > cl:
            # both move to larger values, need to start left blade first
            ar.move(tr)
            sleep(0.25)
            al.move(tl * f)
        else:
            # don't care
            ar.move(tr)
            al.move(tl * f)
        if tb < cb and tt < ct:
            ab.move(tb * f)
            sleep(0.25)
            at.move(tt)
        elif tb > cb and tt > ct:
            at.move(tt)
            sleep(0.25)
            ab.move(tb * f)
        else:
            at.move(tt)
            ab.move(tb * f)

    def doReset(self):
        for ax in self._axes:
            ax.reset()
        for ax in self._axes:
            ax.wait()

    def doReference(self):
        for ax in self._axes:
            if isinstance(ax, CanReference):
                self.log.info('referencing %s...' % ax)
                ax.reference()
            else:
                self.log.warning('%s cannot be referenced' % ax)

    def _doReadPositions(self, maxage):
        cl, cr, cb, ct = [d.read(maxage) for d in self._axes]
        if self.coordinates == 'opposite':
            cl *= -1
            cb *= -1
        return [cl, cr, cb, ct]

    def doRead(self, maxage=0):
        positions = self._doReadPositions(maxage)
        l, r, b, t = positions
        if self.opmode == 'centered':
            if abs((l+r)/2.) > self._adevs['left'].precision or \
                   abs((t+b)/2.) > self._adevs['top'].precision:
                self.log.warning('slit seems to be offcentered, but is '
                                  'set to "centered" mode')
            return [r-l, t-b]
        elif self.opmode == 'offcentered':
            return [(l+r)/2, (t+b)/2, r-l, t-b]
        else:
            return positions

    def valueInfo(self):
        if self.opmode == 'centered':
            return Value('%s.width' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.height' % self, unit=self.unit, fmtstr='%.2f')
        elif self.opmode == 'offcentered':
            return Value('%s.centerx' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.centery' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.width' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.height' % self, unit=self.unit, fmtstr='%.2f')
        else:
            return Value('%s.left' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.right' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.bottom' % self, unit=self.unit, fmtstr='%.2f'), \
                   Value('%s.top' % self, unit=self.unit, fmtstr='%.2f')

    def doStatus(self, maxage=0):
        return multiStatus(zip(self._axnames, self._axes))

    def doReadUnit(self):
        return self._adevs['left'].unit

    def doWriteOpmode(self, value):
        if value == '4blades':
            self.fmtstr = '%.2f %.2f %.2f %.2f'
        elif value == 'offcentered':
            self.fmtstr = '(%.2f, %.2f) %.2f x %.2f'
        else:
            self.fmtstr = '%.2f x %.2f'
        if self._cache:
            self._cache.invalidate(self, 'value')

    def doUpdateOpmode(self, value):
        if value == 'centered':
            self.valuetype = tupleof(float, float)
        else:
            self.valuetype = tupleof(float, float, float, float)


class SlitAxis(Moveable, AutoDevice):
    """
    "Partial" devices for slit axes, useful for e.g. scanning
    over the device slit.centerx.
    """

    attached_devices = {
        'slit': (Slit, 'Slit whose axis is controlled'),
    }

    valuetype = float

    hardware_access = False

    def doRead(self, maxage=0):
        positions = self._adevs['slit']._doReadPositions(maxage)
        return self._convertRead(positions)

    def doStart(self, target):
        currentpos = self._adevs['slit']._doReadPositions(0.1)
        positions = self._convertStart(target, currentpos)
        self._adevs['slit']._doStartPositions(positions)

    def doIsAllowed(self, target):
        currentpos = self._adevs['slit']._doReadPositions(0.1)
        positions = self._convertStart(target, currentpos)
        return self._adevs['slit']._doIsAllowedPositions(positions)


class CenterXSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return (positions[0] + positions[1]) / 2.
    def _convertStart(self, target, current):
        width = current[1] - current[0]
        return (target-width/2., target+width/2., current[2], current[3])

class CenterYSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return (positions[2] + positions[3]) / 2.
    def _convertStart(self, target, current):
        height = current[3] - current[2]
        return (current[0], current[1], target-height/2., target+height/2.)

class WidthSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[1] - positions[0]
    def _convertStart(self, target, current):
        centerx = (current[0] + current[1]) / 2.
        return (centerx-target/2., centerx+target/2., current[2], current[3])

class HeightSlitAxis(SlitAxis):
    def _convertRead(self, positions):
        return positions[3] - positions[2]
    def _convertStart(self, target, current):
        centery = (current[2] + current[3]) / 2.
        return (current[0], current[1], centery-target/2., centery+target/2.)
