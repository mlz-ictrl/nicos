#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   pedersen
#
# *****************************************************************************

"""
Base single crystal instrument (euler geometry)
"""

from collections import namedtuple
import numpy as np
from nicos import session
from nicos.devices.instrument import Instrument
from nicos.devices.tas import Monochromator
from nicos.core import Moveable, Param, Override, AutoDevice, Value, \
    multiStatus, Attach, oneof, vec3, intrange

from nicos.devices.sxtal.goniometer.base import PositionFactory

EPos = namedtuple('EPos', ['ttheta', 'omega', 'chi', 'phi'])


class numpyarray(object):
    def __init__(self, dtype=None, shape=None):
        self.dtype = dtype
        self.shape = shape

    def __call__(self, val=None):
        rv = np.asanyarray(val, dtype=self.dtype)
        if self.shape:
            try:
                rv = rv.reshape(self.shape)
            except AttributeError:
                raise ValueError('Incompatible array shape')
        return rv

    def compare(self,val1, val2):
        return np.array_equiv(val1, val2)


class SXTal(Instrument, Moveable):
    """An instrument class that can move in (q,w) space.

    When setting up a single xtal configuration, use this as your instrument
    device (or derive an individual subclass).
    """

    attached_devices = {
        'mono': Attach('Monochromator device', Monochromator),
        'ttheta': Attach('two-theta device', Moveable),
        'omega': Attach('omega device', Moveable),
        'chi': Attach('chi device', Moveable),
        'phi': Attach('phi device', Moveable),
    }

    parameters = { 'wavelength': Param('Wavelength', type=float,
                                       volatile=True,
                                       settable=False,
                                       ),
                  'scanmode': Param('Scanmode', type=oneof('omega', 't2t'),
                                    userparam=True,
                                    settable=True,
                                    default='omega'),
                  'scansteps': Param('Scan steps', type=intrange(10, 999),
                                    userparam=True,
                                    settable=True,
                                    default=40),
                  'scan_uvw': Param('U,V,W Param', type=vec3,
                                    userparam=True,
                                    settable=True,
                                    default=[1.0, 1.0, 1.0]),
    }

    parameter_overrides = {
        'fmtstr': Override(default='[%6.4f, %6.4f, %6.4f]'),
        'unit':   Override(default='rlu rlu rlu', mandatory=False,
                           settable=True,
                           )
    }

    valuetype = numpyarray(np.float64, (3,))

    hardware_access = False

    def doInit(self, mode):
        self.__dict__['h'] = SXTalIndex('h', unit='rlu', fmtstr='%.3f',
                                        index=0, lowlevel=True, sxtal=self)
        self.__dict__['k'] = SXTalIndex('k', unit='rlu', fmtstr='%.3f',
                                        index=1, lowlevel=True, sxtal=self)
        self.__dict__['l'] = SXTalIndex('l', unit='rlu', fmtstr='%.3f',
                                        index=2, lowlevel=True, sxtal=self)
        self._last_calpos = None
        self._waiters = []


    def doShutdown(self):
        for name in ['h', 'k', 'l']:
            if name in self.__dict__:
                self.__dict__[name].shutdown()

    def hkl2epos(self, pos):
        cell = session.experiment.sample.cell
        cvector = cell.CVector(pos)
        epos = PositionFactory('c', c=cvector).asE()
        return EPos(np.rad2deg(2 * epos.theta), np.rad2deg(epos.omega),
                    np.rad2deg(epos.chi), np.rad2deg(epos.phi))

    def format(self, value, unit=False):
        value = (value[0], value[1], value[2])
        return Moveable.format(self, value, unit)

    def doIsAllowed(self, pos):
        try:
            epos = self.hkl2epos(pos)
        except Exception as err:
            return False, str(err)
        # check limits for the individual axes
        for devname in ['ttheta', 'omega' , 'chi', 'phi']:
            dev = self._adevs[devname]
            if dev is None:
                continue
            else:
                val = epos._asdict()[devname]
                ok, why = dev.isAllowed(val)
            if not ok:
                return ok, 'target position %s outside limits for %s: %s' % \
                            (dev.format(val, unit=True), dev, why)
        return True, ''

    def _sim_getMinMax(self):
        ret = []
        if self._sim_min is not None:
            for i, name in enumerate(['h', 'k', 'l']):
                ret.append((name, '%.4f' % self._sim_value[i],
                            '%.4f' % self._sim_min[i], '%.4f' % self._sim_max[i]))
        return ret

    def doStart(self, pos):
        epos = self.hkl2epos(pos)
        self._attached_ttheta.start(epos.ttheta)
        self._attached_omega.start(epos.omega)
        self._attached_chi.start(epos.chi)
        self._attached_phi.start(epos.phi)
        self._waiters = [self._attached_ttheta, self._attached_omega,
                         self._attached_chi, self._attached_phi]
        # store the min and max values of h,k,l, and E for simulation
        self._sim_value = pos
        self._sim_min = tuple(map(min, pos, self._sim_min or pos))
        self._sim_max = tuple(map(max, pos, self._sim_max or pos))

    def doFinish(self):
        # make sure index members read the latest value
        for index in (self.h, self.k, self.l):
            if index._cache:
                index._cache.invalidate(index, 'value')

    def doStatus(self, maxage=0):
        return multiStatus(((name, self._adevs[name]) for name in
                            ['mono', 'ttheta', 'omega', 'chi', 'phi']), maxage)

    def valueInfo(self):
        return Value('h', unit='rlu', fmtstr='%.4f'), \
            Value('k', unit='rlu', fmtstr='%.4f'), \
            Value('l', unit='rlu', fmtstr='%.4f')

    def doRead(self, maxage=0):
        # read out position
        pos = PositionFactory('e', theta=self._attached_ttheta.read(maxage) / 2.,
                              omega=self._attached_omega.read(maxage),
                              chi=self._attached_chi.read(maxage),
                              phi=self._attached_phi.read(maxage)).asC()
        hkl = session.experiment.sample.cell.hkl(pos.c)
        return [hkl[0], hkl[1], hkl[2]]

    def doReadWavelength(self, maxage=0):
        # ensure using correct unit
        oldunit = None
        if self._attached_mono.unit != 'A':
            oldunit = self._attached_mono.unit
            self._attached_mono.unit = 'A'
        result = self._attached_mono.read(0)
        if oldunit:
            self._attached_mono.unit = oldunit
        return result

    def getScanWidthFor(self, hkl):
        '''Get scanwidth as
          sqrt(u + v *tan Theta + w * tan² Theta)
        '''
        th = session.experiment.sample.cell.Theta(hkl, self.wavelength)
        tan_th = np.tan(th)
        w2 = self.scan_uvw[0] + self.scan_uvw[1] * tan_th + self.scan_uvw[2] * (tan_th ** 2)
        if w2 > 0:
            return np.sqrt(w2)
        else:
            return -np.sqrt(-w2)


class SXTalIndex(AutoDevice, Moveable):
    """
    "Partial" devices for the H, K, L indices of the SXTAL instrument.
    """

    parameters = {
        'index': Param('The index into the SXTAL value', type=int),
    }

    attached_devices = {
        'sxtal': Attach('The spectrometer to control', SXTal),
    }

    valuetype = float

    hardware_access = False

    def doRead(self, maxage=0):
        return self._attached_sxtal.read(maxage)[self.index]

    def doStart(self, pos):
        current = list(self._attached_tas.read(0.5))
        current[self.index] = pos
        self._attached_tas.start(current)
