#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
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

"""NICOS triple-axis instrument devices."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from math import pi, cos, sin, asin, sqrt
from time import time

from nicos.cell import Cell
from nicos.utils import tupleof, listof, oneof, multiStatus
from nicos.errors import ConfigurationError, ComputationError
from nicos.device import Moveable, HasLimits, HasPrecision, Param, Override, \
     AutoDevice
from nicos.experiment import Sample
from nicos.instrument import Instrument


SCANMODES = ['CKI', 'CKF', 'CPHI', 'CPSI', 'DIFF']

ENERGYTRANSFERUNITS = ['meV', 'THz']
THZ2MEV = 4.136


class TASSample(Sample, Cell):
    pass


def wavelength(dvalue, order, theta):
    return 2.0 * dvalue / order * sin(theta/180.0*pi)

def thetaangle(dvalue, order, lam):
    return asin(lam / (2.0 * dvalue/order))/pi*180.0


class Monochromator(HasLimits, HasPrecision, Moveable):
    """
    General monochromator theta/two-theta device.
    """

    attached_devices = {
        'theta':    HasPrecision,
        'twotheta': HasPrecision,
        'focush':   Moveable,
        'focusv':   Moveable,
    }

    hardware_access = False

    parameters = {
        'dvalue':   Param('d-value of the reflection used', unit='A',
                          mandatory=True),
        'order':    Param('order of reflection to use', type=int, default=1,
                          settable=True),
        'reltheta': Param('true if theta position is relative to two-theta',
                          type=bool, default=False),
        # XXX explanation?
        'sidechange': Param('true if side changes?', type=bool, default=False),
        'focmode':  Param('focussing mode', default='manual', settable=True,
                          type=oneof(str, 'manual', 'flat', 'horizontal',
                                     'vertical', 'double')),
        'hfocuspars': Param('horizontal focus polynomial coefficients',
                            type=listof(float), default=[0.]),
        'vfocuspars': Param('vertical focus polynomial coefficients',
                            type=listof(float), default=[0.]),
        'warninterval': Param('interval between warnings about theta/two-theta '
                              'mismatch', unit='s', default=5),
    }

    parameter_overrides = {
        'unit':  Override(default='A-1',
                          type=oneof(str, 'A-1', 'A', 'meV', 'THz')),
        'precision': Override(volatile=True, settable=False),
    }

    def doInit(self):
        # warnings about manual focus
        self._focwarnings = 3

        # warnings about theta/twotheta
        self._lastwarn = time() - self.warninterval # make sure for next warning

        # needs to be set by TAS object, if it isn't this will give an exception
        # when it's used in a calculation
        self._scatsense = None

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

    def doStatus(self):
        return multiStatus((name, self._adevs['name']) for name in
                           ['theta', 'twotheta', 'focush', 'focusv'])

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

    def doStart(self, position):
        lam = self._tolambda(position)  # get position in basic unit
        angle = thetaangle(self.dvalue, self.order, lam)
        tt = 2.0 * angle * self._scatsense  # twotheta with correct sign
        th = angle * self._scatsense      # absolute theta with correct sign
        if self.reltheta:
            # if theta is relative to twotheta, then theta = - twotheta / 2
            th = -th
        # analyser scattering side
        th += 90 * self.sidechange * (1 - self._scatsense)

        self._adevs['twotheta'].start(tt)
        self._adevs['theta'].start(th)
        self._movefoci()

    def _movefoci(self):
        lam = self._tolambda(self.target) # get goalposition in basic unit
        focusv, focush = self._adevs['focusv'], self._adevs['focush']
        if self.focmode == 'flat':
            if focusv:
                focusv.move(0)
            if focush:
                focush.move(0)
        elif self.focmode == 'horizontal':
            if focusv:
                focusv.move(0)
            if focush:
                focush.move(self._calfocus(lam, self.hfocuspars))
        elif self.focmode == 'vertical':
           if focusv:
               focusv.move(self._calfocus(lam, self.vfocuspars))
           if focush:
               focush.move(0)
        elif self.focmode == 'double':
           if focusv:
               focusv.move(self._calfocus(lam, self.vfocuspars))
           if focush:
               focush.move(self._calfocus(lam, self.hfocuspars))
        else:
            if self._focwarnings:
                self.printwarning('focus is in manual mode')
                self._focwarnings -= 1

    def _calfocus(self, lam, focuspars):
        temp = lam * float(self.order)
        focus = 0
        for i, coeff in enumerate(focuspars):
            focus += coeff * (temp**i)
        return focus

    def doIsAllowed(self, position):
        theta = thetaangle(self.dvalue, self.order, self._tolambda(position))
        ttvalue = 2.0 * self._scatsense * theta
        ttdev = self._adevs['twotheta']
        ok, why = ttdev.isAllowed(ttvalue)
        if not ok:
            return ok, '[%s] moving to %s, ' % (
                ttdev, ttdev.format(ttvalue)) + why
        return True, ''

    def doRead(self):
        tt = self._scatsense * self._adevs['twotheta'].read()
        th = self._adevs['theta'].read()
        # analyser scattering side
        th -= 90 * self.sidechange * (1 - self._scatsense)
        th *= self._scatsense  # make it positive
        if self.reltheta:
            # if theta is relative to twotheta then theta = - twotheta / 2
            th = -th
        if abs(tt - 2.0*th) > self._axisprecision:
            if time() - self._lastwarn > self.warninterval:
                self.printwarning('two theta and 2*theta axis mismatch: %s <-> '
                                  '%s = 2 * %s' % (tt, 2.0*th, th))
                self.printinfo('precisions: tt:%s, th:%s, combined: %s' % (
                    self._adevs['twotheta'].precision,
                    self._adevs['theta'].precision, self._axisprecision))
                self._lastwarn = time()

        # even on mismatch, the scattering angle is deciding
        return self._fromlambda(wavelength(self.dvalue, self.order, tt/2.0))

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
           return 2*81.8/lam**3 * dlambda
        elif self.unit == 'THz':
           return 2*338.3/lam**3 * dlambda
        return dlambda

    def doWriteFocmode(self, value):
        self.printwarning('changed focmode %r active AFTER next positioning of '
                          'device' % value)

    def _fromlambda(self, value):
        try:
            if self.unit == 'A-1':
                return 2.0 * pi / value
            elif self.unit == 'A':
                return value
            elif self.unit == 'meV':
                return 81.8 / value**2
            elif self.unit == 'THz':
                return 338.3 / value**2
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
                return sqrt(81.8 / value)
            elif self.unit == 'THz':
                return sqrt(338.3 / value)
        except (ArithmeticError, ValueError), err:
            raise ComputationError(self, 'cannot convert %s A to %s: %s' %
                                   (value, self.unit, err))


class TAS(Instrument, Moveable):

    attached_devices = {
        'cell': Cell,
        'mono': Monochromator,
        'ana':  Monochromator,
        'phi':  Moveable,
        'psi':  Moveable,
    }

    parameters = {
        'scanmode':     Param('Operation mode: one of ' + ', '.join(SCANMODES),
                              type=str, default='CKI', settable=True,
                              category='instrument'),
        'scanconstant': Param('Constant of the operation mode', type=float,
                              default=0, settable=True, category='instrument'),
        'axiscoupling': Param('Whether the sample th/tt axes are coupled',
                              type=bool, default=True, settable=True),
        'psi360':       Param('Whether the range of psi is 0-360 deg '
                              '(otherwise -180-180 deg is assumed).',
                              type=bool, default=True, settable=True),
        'scatteringsense': Param('Scattering sense', default=(1, -1, 1),
                                 type=tupleof(int, int, int), settable=True,
                                 category='instrument'),
        'energytransferunit': Param('Energy transfer unit', type=str,
                                    default='THz', settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='[%6.4f, %6.4f, %6.4f, %6.4f]'),
        'unit':   Override(default='rlu rlu rlu THz', mandatory=False,
                           settable=True)
    }

    hardware_access = False

    def doInit(self):
        self.__dict__['h'] = TASIndex('h', unit='rlu', fmtstr='%.3f',
                                      index=0, lowlevel=True, tas=self)
        self.__dict__['k'] = TASIndex('k', unit='rlu', fmtstr='%.3f',
                                      index=1, lowlevel=True, tas=self)
        self.__dict__['l'] = TASIndex('l', unit='rlu', fmtstr='%.3f',
                                      index=2, lowlevel=True, tas=self)
        self.__dict__['E'] = TASIndex('E', unit=self.energytransferunit,
                                      fmtstr='%.3f', index=3, lowlevel=True,
                                      tas=self)

    def _thz(self, ny):
        if self.energytransferunit == 'meV':
            return ny / THZ2MEV
        return ny

    def doIsAllowed(self, pos):
        qh, qk, ql, ny = pos
        ny = self._thz(ny)
        try:
            angles = self._adevs['cell'].cal_angles(
                [qh, qk, ql], ny, self.scanmode, self.scanconstant,
                self.scatteringsense[1], self.axiscoupling, self.psi360)
        except ComputationError, err:
            return False, str(err)
        # check limits for the individual axes
        for devname, value in zip(['mono', 'ana', 'phi', 'psi'], angles[:4]):
            dev = self._adevs[devname]
            ok, why = dev.isAllowed(value)
            if not ok:
                return ok, 'target position %s outside limits for %s: %s' % \
                       (value, dev, why)
        return True, ''

    def doStart(self, pos):
        qh, qk, ql, ny = pos
        ny = self._thz(ny)
        angles = self._adevs['cell'].cal_angles(
            [qh, qk, ql], ny, self.scanmode, self.scanconstant,
            self.scatteringsense[1], self.axiscoupling, self.psi360)
        mono, ana, phi, psi = self._adevs['mono'], self._adevs['ana'], \
                              self._adevs['phi'], self._adevs['psi']
        self.printdebug('moving phi/stt to %s' % angles[2])
        phi.move(angles[2])
        self.printdebug('moving psi/sth to %s' % angles[3])
        psi.move(angles[3])
        self.printdebug('moving mono to %s' % angles[0])
        mono.move(angles[0])
        if self.scanmode != 'DIFF':
            self.printdebug('moving ana to %s' % angles[1])
            ana.move(angles[1])
        mono.wait()
        if self.scanmode != 'DIFF':
            ana.wait()
        phi.wait()
        psi.wait()
        #h, k, l, ny = self.doRead()
        # make sure index members read the latest value
        for index in (self.h, self.k, self.l, self.E):
            if index._cache:
                index._cache.invalidate(index, 'value')
        #self.printinfo('position hkl: (%7.4f %7.4f %7.4f) E: %7.4f %s' %
        #               (h, k, l, ny, self.energytransferunit))

    def doStatus(self):
        return multiStatus((name, self._adevs[name]) for name in
                           ['mono', 'ana', 'phi', 'psi'])

    def doWriteScatteringsense(self, val):
        for v in val:
            if v not in [-1, 1]:
                raise ConfigurationError('invalid scattering sense %s' % v)

    def doUpdateScatteringsense(self, val):
        self._adevs['mono']._scatsense = val[0]
        self._adevs['ana']._scatsense = val[2]

    def doUpdateScanmode(self, val):
        if val not in SCANMODES:
            raise ConfigurationError('invalid scanmode: %r' % val)

    def doWriteEnergytransferunit(self, val):
        if val not in ENERGYTRANSFERUNITS:
            raise ConfigurationError('invalid energy transfer unit: %r' % val)
        if self._cache:
            self._cache.invalidate(self, 'value')
        self.unit = 'rlu rlu rlu %s' % val
        self.E.unit = val

    def doRead(self):
        mono, ana, phi, psi = self._adevs['mono'], self._adevs['ana'], \
                              self._adevs['phi'], self._adevs['psi']
        # read out position
        if self.scanmode == 'DIFF':
            hkl = self._adevs['cell'].angle2hkl([mono.read(), mono.read(),
                                                 phi.read(), psi.read()],
                                                self.axiscoupling)
            ny = 0
        else:
            hkl = self._adevs['cell'].angle2hkl([mono.read(), ana.read(),
                                                 phi.read(), psi.read()],
                                                self.axiscoupling)
            ny = self._adevs['cell'].cal_ny(mono.read(), ana.read())
            if self.energytransferunit == 'meV':
                ny *= THZ2MEV
        return (hkl[0], hkl[1], hkl[2], ny)


class TASIndex(Moveable, AutoDevice):
    """
    "Partial" devices for the H, K, L, E indices of the TAS instrument.
    """

    parameters = {
        'index': Param('The index into the TAS value', type=int),
    }

    attached_devices = {
        'tas': TAS,
    }

    hardware_access = False

    def doRead(self):
        return self._adevs['tas'].read()[self.index]

    def doStart(self, pos):
        current = list(self._adevs['tas'].read())
        current[self.index] = pos
        self._adevs['tas'].start(current)


class Wavevector(Moveable):
    """
    Device for adjusting initial/final wavevectors of the TAS and also setting
    the scanmode.
    """

    parameters = {
        'scanmode': Param('Scanmode to set', type=str, mandatory=True),
    }

    attached_devices = {
        'base': Moveable,
        'tas': TAS,
    }

    hardware_access = False

    def doInit(self):
        self._value = None

    def doRead(self):
        if self._value is None:
            self._value = self._adevs['base'].read()
        return self._value

    def doStart(self, pos):
        # first drive there, to determine if it is within limits
        self._adevs['base'].start(pos)
        self._adevs['tas'].scanmode = self.scanmode
        self._adevs['tas'].scanconstant = pos
        self._value = pos
