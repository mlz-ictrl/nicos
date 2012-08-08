#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS triple-axis instrument devices."""

__version__ = "$Revision$"

from math import pi, cos, sin, asin, radians, degrees, sqrt
from time import time

from nicos.core import Moveable, HasLimits, HasPrecision, Param, Override, \
     listof, oneof, ComputationError, LimitError, multiStatus


THZ2MEV = 4.136


def wavelength(dvalue, order, theta):
    return 2.0 * dvalue / order * sin(radians(theta))

def thetaangle(dvalue, order, lam):
    return degrees(asin(lam / (2.0 * dvalue/order)))


class Monochromator(HasLimits, HasPrecision, Moveable):
    """General monochromator theta/two-theta device.

    It supports setting the `unit` parameter to different values and will
    calculate the theta/two-theta angles correctly for each supported value:

    * "A-1" -- wavevector in inverse Angstrom
    * "A" -- wavelength in Angstrom
    * "meV" -- energy in meV
    * "THz" -- energy in THz

    Also supported is a focussing monochromator setup.  For this, set the
    `focush` and `focusv` attached devices to the axes that control the
    focussing, and set `hfocuspars` and `vfocuspars` to a list of coefficients
    (starting with the constant coefficient) for a polynomial that calculates
    the `focush` and `focusv` values from a given wavelength.
    """

    attached_devices = {
        'theta':    (HasPrecision, 'Monochromator rocking angle'),
        'twotheta': (HasPrecision, 'Monochromator scattering angle'),
        'focush':   (Moveable, 'Horizontal focusing axis'),
        'focusv':   (Moveable, 'Vertical focusing axis'),
    }

    hardware_access = False

    parameters = {
        'dvalue':   Param('d-value of the reflection used', unit='A',
                          mandatory=True, settable=True, category='instrument'),
        'mosaic':   Param('mosaicity of the crystal', unit='deg', default=0.5,
                          settable=True, category='instrument'),
        'order':    Param('order of reflection to use', type=int, default=1,
                          settable=True, category='instrument'),
        'reltheta': Param('true if theta position is relative to two-theta',
                          type=bool, default=False, category='instrument'),
        # XXX explanation?
        'sidechange': Param('', type=int, default=False),
        'focmode':  Param('focussing mode', default='manual', settable=True,
                          type=oneof('manual', 'flat', 'horizontal',
                                     'vertical', 'double'),
                          category='instrument'),
        'hfocuspars': Param('horizontal focus polynomial coefficients',
                            type=listof(float), default=[0.], settable=True,
                            category='instrument'),
        'vfocuspars': Param('vertical focus polynomial coefficients',
                            type=listof(float), default=[0.], settable=True,
                            category='instrument'),
        'warninterval': Param('interval between warnings about theta/two-theta '
                              'mismatch', unit='s', default=5),
        'scatteringsense': Param('default scattering sense when not used '
                                 'in triple-axis mode', type=oneof(1, -1)),
    }

    parameter_overrides = {
        'unit':  Override(default='A-1', type=oneof('A-1', 'A', 'meV', 'THz')),
        'precision': Override(volatile=True, settable=False),
        'fmtstr': Override(default='%.3f'),
    }

    def doInit(self, mode):
        # warnings about manual focus
        self._focwarnings = 3

        # warnings about theta/twotheta
        self._lastwarn = time() - self.warninterval # make sure for next warning

        # can be re-set by TAS object
        self._scatsense = self.scatteringsense

        # need to consider rounding effects since a difference of 0.0104 is
        # rounded to 0.010 so the combined axisprecision need to be larger than
        # the calculated value the following correction seems to work just fine
        self._axisprecision = self._adevs['twotheta'].precision + \
                              2 * self._adevs['theta'].precision
        self._axisprecision *= 1.25

        self._movelist = []
        for drive in ['theta', 'twotheta', 'focush', 'focusv']:
            if self._adevs[drive]:
                self._movelist.append(self._adevs[drive])

    def doStatus(self, maxage=0):
        return multiStatus(((name, self._adevs[name]) for name in
                            ['theta', 'twotheta', 'focush', 'focusv']), maxage)

    def doStop(self):
        for device in self._movelist:
            device.stop()

    def doWait(self):
        for device in self._movelist:
            device.wait()

    def doReset(self):
        for device in self._movelist:
            device.reset()
        self._focwarnings = 3

    def doStart(self, pos):
        lam = self._tolambda(pos)  # get position in basic unit
        try:
            angle = thetaangle(self.dvalue, self.order, lam)
        except ValueError:
            raise LimitError(self, 'wavelength not reachable with d=%.3f A '
                             'and n=%s' % (self.dvalue, self.order))
        tt = 2.0 * angle * self._scatsense  # twotheta with correct sign
        th = angle * self._scatsense      # absolute theta with correct sign
        if self.reltheta:
            # if theta is relative to twotheta, then theta = - twotheta / 2
            th = -th
        # analyser scattering side
        th += 90 * self.sidechange * (1 - self._scatsense)

        self._adevs['twotheta'].start(tt)
        self._adevs['theta'].start(th)
        self._movefoci(self.focmode, self.hfocuspars, self.vfocuspars)

    def _movefoci(self, focmode, hfocuspars, vfocuspars):
        lam = self._tolambda(self.target)  # get goalposition in basic unit
        focusv, focush = self._adevs['focusv'], self._adevs['focush']
        if focmode == 'flat':
            if focusv:
                focusv.move(0)
            if focush:
                focush.move(0)
        elif focmode == 'horizontal':
            if focusv:
                focusv.move(0)
            if focush:
                focush.move(self._calfocus(lam, hfocuspars))
        elif focmode == 'vertical':
            if focusv:
                focusv.move(self._calfocus(lam, vfocuspars))
            if focush:
                focush.move(0)
        elif focmode == 'double':
            if focusv:
                focusv.move(self._calfocus(lam, vfocuspars))
            if focush:
                focush.move(self._calfocus(lam, hfocuspars))
        else:
            if self._focwarnings and (focusv or focush):
                self.log.warning('focus is in manual mode')
                self._focwarnings -= 1

    def _calfocus(self, lam, focuspars):
        temp = lam * float(self.order)
        focus = 0
        for i, coeff in enumerate(focuspars):
            focus += coeff * (temp**i)
        return focus

    def doIsAllowed(self, pos):
        try:
            theta = thetaangle(self.dvalue, self.order, self._tolambda(pos))
        except ValueError:
            return False, 'wavelength not reachable with d=%.3f A and n=%s' % \
                   (self.dvalue, self.order)
        ttvalue = 2.0 * self._scatsense * theta
        ttdev = self._adevs['twotheta']
        ok, why = ttdev.isAllowed(ttvalue)
        if not ok:
            return ok, '[%s] moving to %s, ' % (
                ttdev, ttdev.format(ttvalue)) + why
        return True, ''

    def doRead(self, maxage=0):
        tt = self._scatsense * self._adevs['twotheta'].read(maxage)
        th = self._adevs['theta'].read(maxage)
        # analyser scattering side
        th -= 90 * self.sidechange * (1 - self._scatsense)
        th *= self._scatsense  # make it positive
        if self.reltheta:
            # if theta is relative to twotheta then theta = - twotheta / 2
            th = -th
        if abs(tt - 2.0*th) > self._axisprecision:
            if time() - self._lastwarn > self.warninterval:
                self.log.warning('two theta and 2*theta axis mismatch: %s <-> '
                                  '%s = 2 * %s' % (tt, 2.0*th, th))
                self.log.info('precisions: tt:%s, th:%s, combined: %s' % (
                    self._adevs['twotheta'].precision,
                    self._adevs['theta'].precision, self._axisprecision))
                self._lastwarn = time()

        # even on mismatch, the scattering angle is deciding
        return self._fromlambda(wavelength(self.dvalue, self.order, tt/2.0))

    # methods used by the TAS class to ensure the correct unit is used: it
    # calculates all ki/kf in A-1

    def _allowedInvAng(self, pos):
        return self.isAllowed(self._fromlambda(2*pi/pos))

    def _startInvAng(self, pos):
        return self.start(self._fromlambda(2*pi/pos))

    def _readInvAng(self, maxage=0):
        return 2*pi/self._tolambda(self.read(maxage))

    def doReadPrecision(self):
        if not hasattr(self, '_scatsense'):
            # object not yet intialized
            return 0
        # the precision depends on the angular precision of theta and twotheta
        lam = self._tolambda(self.read())
        dtheta = self._adevs['theta'].precision + \
                 self._adevs['twotheta'].precision
        dlambda = abs(2.0 * self.dvalue *
                      cos(self._adevs['twotheta'].read() * pi/360) *
                      dtheta / 180*pi)
        if self.unit == 'A-1':
            return 2*pi/lam**2 * dlambda
        elif self.unit == 'meV':
            return 2*81.804 / lam**3 * dlambda
        elif self.unit == 'THz':
            return 2*81.804 / THZ2MEV / lam**3 * dlambda
        return dlambda

    def doWriteFocmode(self, value):
        if value != 'manual':
            self.log.info('moving foci to new values')
        self._movefoci(value, self.hfocuspars, self.vfocuspars)

    def doWriteHfocuspars(self, value):
        self.log.info('moving foci to new values')
        self._movefoci(self.focmode, value, self.vfocuspars)

    def doWriteVfocuspars(self, value):
        self.log.info('moving foci to new values')
        self._movefoci(self.focmode, self.hfocuspars, value)

    def doWriteUnit(self, value):
        if self._cache:
            self._cache.invalidate(self, 'value')

    def _fromlambda(self, value):
        try:
            if self.unit == 'A-1':
                return 2.0 * pi / value
            elif self.unit == 'A':
                return value
            elif self.unit == 'meV':
                return 81.804 / value**2
            elif self.unit == 'THz':
                return 81.804 / THZ2MEV / value**2
        except (ArithmeticError, ValueError), err:
            raise ComputationError(self, 'cannot convert %s A to %s: %s' %
                                   (value, self.unit, err))

    def _tolambda(self, value):
        try:
            if self.unit == 'A-1':
                return 2.0 * pi / value
            elif self.unit == 'A':
                return value
            elif self.unit == 'meV':
                return sqrt(81.804 / value)
            elif self.unit == 'THz':
                return sqrt(81.804 / THZ2MEV / value)
        except (ArithmeticError, ValueError), err:
            raise ComputationError(self, 'cannot convert %s A to %s: %s' %
                                   (value, self.unit, err))
