#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS Triple-Axis Instrument device
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""
NICOS Instrument device.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"


from nicm.cell import Cell
from nicm.utils import vec3
from nicm.errors import ConfigurationError, ComputationError
from nicm.device import BaseMoveable, Moveable, Param
from nicm.experiment import Sample
from nicm.instrument import Instrument


OPMODES = ['CKI', 'CKF', 'CPHI', 'CPSI', 'DIFF']
OPMODEUNIT = {'CKI': 'A-1', 'CKF': 'A-1',
              'CPHI': 'deg', 'CPSI': 'deg', 'DIFF': 'A-1'}

ENERGYTRANSFERUNITS = ['meV', 'THz']
THZ2MEV = 4.136


class TASSample(Sample, Cell):
    pass


class TAS(Instrument, BaseMoveable):

    attached_devices = {
        'cell': Cell,
        'mono': Moveable,
        'ana': Moveable,
        'phi': Moveable,
        'psi': Moveable,
    }

    parameters = {
        'fmtstr': Param('Format string for the device value', type=str,
                        default='%10.4f %10.4f %10.4f %10.4f %10.4f',
                        settable=True),
        'opmode': Param('Operation mode: one of ' + ', '.join(OPMODES),
                        type=str, default='CKI', settable=True, info=True),
        'scatsense': Param('Scattering sense', type=vec3, default=[1, -1, 1],
                           settable=True),
        'energytransferunit': Param('Energy transfer unit', type=str,
                                    default='THz', settable=True),
        'unit': Param('Unit', type=str, default='rlu/rlu/rlu/THz/A-1',
                      settable=True),
    }

    def doInit(self):
        self.__dict__['h'] = TASIndex(self.name+' h', unit='rlu',
                                      index=0, lowlevel=True, tas=self)
        self.__dict__['k'] = TASIndex(self.name+' k', unit='rlu',
                                      index=1, lowlevel=True, tas=self)
        self.__dict__['l'] = TASIndex(self.name+' l', unit='rlu',
                                      index=2, lowlevel=True, tas=self)
        self.__dict__['ny'] = TASIndex(self.name+' ny', unit='THz',
                                       index=3, lowlevel=True, tas=self)
        self.__dict__['sc'] = TASIndex(self.name+' sc', unit='A-1',
                                       index=4, lowlevel=True, tas=self)

    def _thz(self, ny):
        if self.energytransferunit == 'meV':
            return ny / THZ2MEV
        return ny

    def doIsAllowed(self, pos):
        qh, qk, ql, ny, sc = pos
        ny = self._thz(ny)
        try:
            angles = self._adevs['cell'].cal_angles(
                [qh, qk, ql], ny, self.opmode, sc, self.scatsense[1])
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
        qh, qk, ql, ny, sc = pos
        ny = self._thz(ny)
        angles = self._adevs['cell'].cal_angles(
            [qh, qk, ql], ny, self.opmode, sc, self.scatsense[1])
        mono, ana, phi, psi = self._adevs['mono'], self._adevs['ana'], \
                              self._adevs['phi'], self._adevs['psi']
        phi.move(angles[2])
        psi.move(angles[3])
        mono.move(angles[0])
        if self.opmode != 'DIFF':
            ana.move(angles[1])
        mono.wait()
        if self.opmode != 'DIFF':
            ana.wait()
        phi.wait()
        psi.wait()
        h, k, l, ny, sc = self.doRead()
        self.printinfo('position hkl: (%7.4f %7.4f %7.4f) ny: %7.4f %s' %
                       (h, k, l, ny, self.energytransferunit))

    def doWriteScatsense(self, val):
        for v in val:
            if v not in [-1, 1]:
                raise ConfigurationError('invalid scattering sense %s' % v)

    def doWriteOpmode(self, val):
        if val not in OPMODES:
            raise ConfigurationError('invalid opmode: %r' % val)
        self.unit = 'rlu/rlu/rlu/%s/%s' % (self.energytransferunit,
                                           OPMODEUNIT[val])
        self.sc.unit = OPMODEUNIT[val]

    def doWriteEnergytransferunit(self, val):
        if val not in ENERGYTRANSFERUNITS:
            raise ConfigurationError('invalid energy transfer unit: %r' % val)
        self.unit = 'rlu/rlu/rlu/%s/%s' % (val, OPMODEUNIT[self.opmode])
        self.ny.unit = val

    def doRead(self):
        mono, ana, phi, psi = self._adevs['mono'], self._adevs['ana'], \
                              self._adevs['phi'], self._adevs['psi']
        # read out position
        if self.opmode == 'DIFF':
            hkl = self._adevs['cell'].angle2hkl([mono.read(), mono.read(),
                                                 phi.read(), psi.read()])
            ny = 0
        else:
            hkl = self._adevs['cell'].angle2hkl([mono.read(), ana.read(),
                                                 phi.read(), psi.read()])
            ny = self._adevs['cell'].cal_ny(mono.read(), ana.read())
            if self.energytransferunit == 'meV':
                ny *= THZ2MEV
        if self.opmode in ['CKI', 'DIFF']:
            sc = mono.read()
        elif self.opmode == 'CKF':
            sc = ana.read()
        elif self.opmode == 'CPHI':
            sc = phi.read()
        elif self.opmode == 'CPSI':
            sc = psi.read()
        return (hkl[0], hkl[1], hkl[2], ny, sc)


class TASIndex(BaseMoveable):
    """
    "Partial" devices for the H, K, L, E indices of the TAS instrument.

    XXX are these really needed?
    """

    parameters = {
        'index': Param('The index into the TAS value', type=int),
    }

    attached_devices = {
        'tas': TAS,
    }

    def doRead(self):
        return self._adevs['tas'].read()[self.index]

    def doStart(self, pos):
        current = list(self._adevs['tas'].read())
        current[self.index] = pos
        self._adevs['tas'].start(current)
