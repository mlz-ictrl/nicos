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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS triple-axis instrument devices."""

from math import asin, cos, degrees, pi, radians, sin, sqrt

from nicos.core import Attach, ComputationError, HasLimits, HasPrecision, \
    LimitError, Moveable, Override, Param, ProgrammingError, listof, multiReset, \
    multiStatus, oneof, status, MASTER, SIMULATION
from nicos.pycompat import listvalues


THZ2MEV = 4.1356675
ANG2MEV = 81.804165


def wavevector(dvalue, order, theta):
    return pi * order / (dvalue * sin(radians(theta)))


def thetaangle(dvalue, order, k):
    return degrees(asin(pi * order / (k * dvalue)))


def from_k(value, unit):
    try:
        if unit == 'A-1':
            return value
        elif unit == 'A':
            return 2.0 * pi / value
        elif unit == 'meV':
            return ANG2MEV * value**2 / (2*pi)**2
        elif unit == 'THz':
            return ANG2MEV / THZ2MEV * value**2 / (2*pi)**2
        else:
            raise ProgrammingError('unknown energy unit %r' % unit)
    except (ArithmeticError, ValueError) as err:
        raise ComputationError('cannot convert %s A-1 to %s: %s' %
                               (value, unit, err))


def to_k(value, unit):
    try:
        if unit == 'A-1':
            return value
        elif unit == 'A':
            return 2.0 * pi / value
        elif unit == 'meV':
            return 2.0 * pi * sqrt(value / ANG2MEV)
        elif unit == 'THz':
            return 2.0 * pi * sqrt(value * THZ2MEV / ANG2MEV)
        else:
            raise ProgrammingError('unknown energy unit %r' % unit)
    except (ArithmeticError, ValueError) as err:
        raise ComputationError('cannot convert %s A-1 to %s: %s' %
                               (value, unit, err))


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
        'theta':    Attach('Monochromator rocking angle', HasPrecision),
        'twotheta': Attach('Monochromator scattering angle', HasPrecision),
        'focush':   Attach('Horizontal focusing axis', Moveable,
                           optional=True),
        'focusv':   Attach('Vertical focusing axis', Moveable,
                           optional=True),
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
        'sidechange': Param('', type=int, default=False, userparam=False),
        'focmode':  Param('focussing mode', default='manual', settable=True,
                          type=oneof('manual', 'flat', 'horizontal',
                                     'vertical', 'double'),
                          category='instrument'),
        'hfocuspars': Param('horizontal focus polynomial coefficients',
                            type=listof(float), default=[0.], settable=True,
                            category='instrument'),
        'hfocusflat': Param('horizontal focus value for flat mono',
                            type=float, default=0, settable=True),
        'vfocuspars': Param('vertical focus polynomial coefficients',
                            type=listof(float), default=[0.], settable=True,
                            category='instrument'),
        'vfocusflat': Param('vertical focus value for flat mono',
                            type=float, default=0, settable=True),
        'scatteringsense': Param('default scattering sense when not used '
                                 'in triple-axis mode', type=oneof(1, -1)),
    }

    parameter_overrides = {
        'unit':  Override(default='A-1', type=oneof('A-1', 'A', 'meV', 'THz'),
                          chatty=True),
        'precision': Override(volatile=True, settable=False),
        'fmtstr': Override(default='%.3f'),
    }

    def doInit(self, mode):
        # warnings about manual focus
        self._focwarnings = 3

        # can be re-set by TAS object
        self._scatsense = self.scatteringsense

        # need to consider rounding effects since a difference of 0.0104 is
        # rounded to 0.010 so the combined axisprecision need to be larger than
        # the calculated value the following correction seems to work just fine
        self._axisprecision = self._adevs['twotheta'].precision + \
            2 * self._adevs['theta'].precision
        self._axisprecision *= 1.25

    def doReset(self):
        multiReset(listvalues(self._adevs))
        self._focwarnings = 3

    def doStart(self, pos):
        k = to_k(pos, self.unit)
        try:
            angle = thetaangle(self.dvalue, self.order, k)
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
        self._sim_setValue(pos)

    def _movefoci(self, focmode, hfocuspars, vfocuspars):
        lam = from_k(to_k(self.target, self.unit), 'A')  # get goalposition in A
        focusv, focush = self._adevs['focusv'], self._adevs['focush']
        if focmode == 'flat':
            if focusv:
                focusv.move(self.vfocusflat)
            if focush:
                focush.move(self.hfocusflat)
        elif focmode == 'horizontal':
            if focusv:
                focusv.move(self.vfocusflat)
            if focush:
                focush.move(self._calfocus(lam, hfocuspars))
        elif focmode == 'vertical':
            if focusv:
                focusv.move(self._calfocus(lam, vfocuspars))
            if focush:
                focush.move(self.hfocusflat)
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
            theta = thetaangle(self.dvalue, self.order, to_k(pos, self.unit))
        except ValueError:
            return False, 'wavelength not reachable with d=%.3f A and n=%s' % \
                (self.dvalue, self.order)
        ttvalue = 2.0 * self._scatsense * theta
        ttdev = self._adevs['twotheta']
        ok, why = ttdev.isAllowed(ttvalue)
        if not ok:
            return ok, '[%s] moving to %s, ' % (
                ttdev, ttdev.format(ttvalue, unit=True)) + why
        return True, ''

    def _get_angles(self, maxage):
        tt = self._scatsense * self._adevs['twotheta'].read(maxage)
        th = self._adevs['theta'].read(maxage)
        # analyser scattering side
        th -= 90 * self.sidechange * (1 - self._scatsense)
        th *= self._scatsense  # make it positive
        if self.reltheta:
            # if theta is relative to twotheta then theta = - twotheta / 2
            th = -th
        return tt, th

    def doRead(self, maxage=0):
        # the scattering angle is deciding
        tt = self._scatsense * self._adevs['twotheta'].read(maxage)
        return from_k(wavevector(self.dvalue, self.order, tt/2.0), self.unit)

    def doStatus(self, maxage=0):
        # order is important here.
        const, text = multiStatus(((name, self._adevs[name]) for name in
            ['theta', 'twotheta', 'focush', 'focusv']), maxage)
        if const == status.OK:  # all idle; check also angle relation
            tt, th = self._get_angles(maxage)
            if abs(tt - 2.0*th) > self._axisprecision:
                return status.NOTREACHED, \
                    'two theta and 2*theta axis mismatch: %s <-> %s = 2 * %s' % \
                    (tt, 2.0*th, th)
        return const, text

    def doFinish(self):
        tt, th = self._get_angles(0)
        if abs(tt - 2.0*th) > self._axisprecision:
            self.log.warning('two theta and 2*theta axis mismatch: %s <-> '
                             '%s = 2 * %s' % (tt, 2.0*th, th))
            self.log.info('precisions: tt:%s, th:%s, combined: %s' % (
                self._adevs['twotheta'].precision,
                self._adevs['theta'].precision, self._axisprecision))

    def doReadPrecision(self):
        if not hasattr(self, '_scatsense'):
            # object not yet intialized
            return 0
        # the precision depends on the angular precision of theta and twotheta
        lam = from_k(to_k(self.read(), self.unit), 'A')
        dtheta = self._adevs['theta'].precision + \
            self._adevs['twotheta'].precision
        dlambda = abs(2.0 * self.dvalue *
                      cos(self._adevs['twotheta'].read() * pi/360) *
                      dtheta / 180*pi)
        if self.unit == 'A-1':
            return 2*pi/lam**2 * dlambda
        elif self.unit == 'meV':
            return 2*ANG2MEV / lam**3 * dlambda
        elif self.unit == 'THz':
            return 2*ANG2MEV / THZ2MEV / lam**3 * dlambda
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

    def doUpdateUnit(self, value):
        if 'unit' not in self._params:
            # this is the initial update
            return
        if self._mode not in (MASTER, SIMULATION):
            # change limits only from the master copy, or in simulation mode
            return
        new_absmin = from_k(to_k(self.abslimits[0], self.unit), value)
        new_absmax = from_k(to_k(self.abslimits[1], self.unit), value)
        if new_absmin > new_absmax:
            new_absmin, new_absmax = new_absmax, new_absmin
        self._setROParam('abslimits', (new_absmin, new_absmax))
        if self.userlimits != (0, 0):
            new_umin = from_k(to_k(self.userlimits[0], self.unit), value)
            new_umax = from_k(to_k(self.userlimits[1], self.unit), value)
            if new_umin > new_umax:
                new_umin, new_umax = new_umax, new_umin
            new_umin = max(new_umin, new_absmin)
            new_umax = min(new_umax, new_absmax)
            self.userlimits = (new_umin, new_umax)
        if 'target' in self._params and self.target and self.target != 'unknown':
            # this should be still within the limits
            self._setROParam(
                'target', from_k(to_k(self.target, self.unit), value))
        self.read(0)

    def _calcurvature(self, l1, l2, k, vertical=True):
        """Calculate optimum curvature (1/radius) for given lengths and
        monochromator rotation angle (given by wavevector in A-1).
        """
        theta = thetaangle(self.dvalue, self.order, k)
        exp = vertical and -1 or +1
        return 0.5*(1./l1 + 1./l2)*sin(radians(abs(theta)))**exp
