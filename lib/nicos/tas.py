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


from nicos.cell import Cell
from nicos.utils import vec3
from nicos.errors import ConfigurationError, ComputationError
from nicos.device import Moveable, HasLimits, Param, Override, AutoDevice
from nicos.experiment import Sample
from nicos.instrument import Instrument


SCANMODES = ['CKI', 'CKF', 'CPHI', 'CPSI', 'DIFF']

ENERGYTRANSFERUNITS = ['meV', 'THz']
THZ2MEV = 4.136


class TASSample(Sample, Cell):
    pass


class TAS(Instrument, Moveable):

    attached_devices = {
        'cell': Cell,
        'mono': Moveable,
        'ana': Moveable,
        'phi': Moveable,
        'psi': Moveable,
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
        'scatteringsense': Param('Scattering sense', type=vec3,
                                 default=[1, -1, 1], settable=True,
                                 category='instrument'),
        'energytransferunit': Param('Energy transfer unit', type=str,
                                    default='THz', settable=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='[%7.4f, %7.4f, %7.4f, %7.4f, %7.4f]'),
        'unit':   Override(default='rlu rlu rlu THz A-1', mandatory=False,
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
        self.printdebug('moving phi to %s' % angles[2])
        phi.move(angles[2])
        self.printdebug('moving psi to %s' % angles[3])
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

    def doWriteScatteringsense(self, val):
        for v in val:
            if v not in [-1, 1]:
                raise ConfigurationError('invalid scattering sense %s' % v)

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
