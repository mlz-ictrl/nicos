#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

"""Base single crystal instrument (Euler geometry)."""

import numpy as np

from nicos import session
from nicos.core import Moveable, Param, Override, AutoDevice, LimitError, \
    Value, Attach, oneof, vec3, intrange, tupleof
from nicos.devices.instrument import Instrument
from nicos.devices.tas import Monochromator

from nicos.devices.sxtal.goniometer.base import PositionFactory


class SXTalBase(Instrument, Moveable):
    """An instrument class that can move in q space.

    When setting up a single xtal configuration, use a subclass that reflects
    the instrument geometry as your instrument device.
    """

    attached_devices = {
        'mono': Attach('Monochromator device', Monochromator),
    }

    parameters = {
        'wavelength': Param('Wavelength', type=float,
                            volatile=True, settable=False),
        'scanmode':   Param('Scanmode', type=oneof('omega', 't2t'),
                            userparam=True, settable=True,
                            default='omega'),
        'scansteps':  Param('Scan steps', type=intrange(10, 999),
                            userparam=True, settable=True, default=40),
        'scan_uvw':   Param('U,V,W Param', type=vec3, userparam=True,
                            settable=True, default=[1.0, 1.0, 1.0]),
    }

    parameter_overrides = {
        'fmtstr':     Override(default='[%6.4f, %6.4f, %6.4f]'),
        'unit':       Override(default='rlu', mandatory=False,
                               settable=True),
    }

    valuetype = tupleof(float, float, float)
    hardware_access = False
    _last_calpos = None

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

    def _calcPos(self, hkl):
        """Calculate instrument position object for given HKL position."""
        cell = session.experiment.sample.cell
        cpos = PositionFactory('c', c=cell.CVector(hkl))
        return self._convertPos(cpos)

    def _extractPos(self, pos):
        """Extract values for the attached devices from a position object.
        Must be implemented in subclasses.
        """
        raise NotImplementedError

    def _convertPos(self, pos):
        """Convert given position to the type usable by this geometry.
        Must be implemented in subclasses.
        """
        raise NotImplementedError

    def _readPos(self, maxage=0):
        """Create a position object with the current values of the attached
        devices.  Must be implemented in subclasses.
        """
        raise NotImplementedError

    def _createPos(self, **kwds):
        """Create a position object with the values of the given devices.
        Must be implemented in subclasses.
        """
        raise NotImplementedError

    def _calpos(self, hkl, printout=True, checkonly=True):
        """Implements the calpos() command."""
        try:
            poslist = self._extractPos(self._calcPos(hkl))
        except Exception as err:
            return False, str(err)
        ok, why = True, ''
        for devname, value in poslist:
            dev = self._adevs[devname]
            if dev is None:
                continue
            devok, devwhy = dev.isAllowed(value)
            if not devok:
                ok = False
                why += 'target position %s outside limits for %s: %s -- ' % \
                    (dev.format(value, unit=True), dev, devwhy)
            self.log.info('%-14s %8.3f %s', dev.name + ':', value, dev.unit)
        if ok:
            self._last_calpos = hkl
            if checkonly:
                self.log.info('position allowed')
        else:
            if checkonly:
                self.log.warning('position not allowed: %s', why[:-4])
            else:
                raise LimitError(self, 'position not allowed: ' + why[:-4])

    def _reverse_calpos(self, **kwds):
        """Implements the pos2hkl() command."""
        pos = self._createPos(**kwds).asC()
        hkl = session.experiment.sample.cell.hkl(pos.c)
        self.log.info('pos: [%.4f, %.4f, %.4f]', *hkl)

    def doIsAllowed(self, hkl):
        try:
            poslist = self._extractPos(self._calcPos(hkl))
        except Exception as err:
            return False, str(err)
        # check limits for the individual axes
        for (devname, devvalue) in poslist:
            dev = self._adevs[devname]
            if dev is None:
                continue
            else:
                ok, why = dev.isAllowed(devvalue)
            if not ok:
                return ok, 'target position %s outside limits for %s: %s' % \
                    (dev.format(devvalue, unit=True), dev, why)
        return True, ''

    def _sim_getMinMax(self):
        ret = []
        if self._sim_min is not None:
            for i, name in enumerate(['h', 'k', 'l']):
                ret.append((name, '%.4f' % self._sim_value[i],
                            '%.4f' % self._sim_min[i],
                            '%.4f' % self._sim_max[i]))
        return ret

    def doStart(self, hkl):
        poslist = self._extractPos(self._calcPos(hkl))
        self._waiters = []
        for (devname, devvalue) in poslist:
            dev = self._adevs[devname]
            dev.start(devvalue)
            self._waiters.append(dev)
        # store the min and max values of h,k,l, and E for simulation
        self._sim_value = hkl
        self._sim_min = tuple(map(min, hkl, self._sim_min or hkl))
        self._sim_max = tuple(map(max, hkl, self._sim_max or hkl))

    def doFinish(self):
        # make sure index members read the latest value
        for index in (self.h, self.k, self.l):
            if index._cache:
                index._cache.invalidate(index, 'value')

    def valueInfo(self):
        return Value('h', unit='rlu', fmtstr='%.4f'), \
            Value('k', unit='rlu', fmtstr='%.4f'), \
            Value('l', unit='rlu', fmtstr='%.4f')

    def doRead(self, maxage=0):
        pos = self._readPos(maxage).asC()
        hkl = session.experiment.sample.cell.hkl(pos.c)
        return list(hkl)

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
        """Get scan width for a certain HKL."""
        raise NotImplementedError


class EulerSXTal(SXTalBase):

    attached_devices = {
        'ttheta': Attach('two-theta device', Moveable),
        'omega':  Attach('omega device', Moveable),
        'chi':    Attach('chi device', Moveable),
        'phi':    Attach('phi device', Moveable),
    }

    def _extractPos(self, pos):
        return [
            ('ttheta', np.rad2deg(2 * pos.theta)),
            ('omega',  np.rad2deg(pos.omega)),
            ('chi',    np.rad2deg(pos.chi)),
            ('phi',    np.rad2deg(pos.phi)),
        ]

    def _convertPos(self, pos):
        return pos.asE()

    def _readPos(self, maxage=0):
        return PositionFactory('e',
                               theta=self._attached_ttheta.read(maxage) / 2.,
                               omega=self._attached_omega.read(maxage),
                               chi=self._attached_chi.read(maxage),
                               phi=self._attached_phi.read(maxage))

    def _createPos(self, ttheta, omega, chi, phi):  # pylint: disable=W0221
        return PositionFactory('e', theta=ttheta/2., omega=omega, chi=chi,
                               phi=phi)

    def getScanWidthFor(self, hkl):
        """Get scanwidth as ``sqrt(u + v *tan Theta + w * tan² Theta)``."""
        th = session.experiment.sample.cell.Theta(hkl, self.wavelength)
        tan_th = np.tan(th)
        w2 = self.scan_uvw[0] + \
            self.scan_uvw[1] * tan_th + \
            self.scan_uvw[2] * (tan_th ** 2)
        if w2 > 0:
            return np.sqrt(w2)
        else:
            return -np.sqrt(-w2)


class LiftingSXTal(SXTalBase):

    attached_devices = {
        'gamma':  Attach('gamma device', Moveable),
        'omega':  Attach('omega device', Moveable),
        'nu':     Attach('nu device (counter lifting axis)', Moveable),
    }

    def _extractPos(self, pos):
        return [
            ('gamma', np.rad2deg(pos.gamma)),
            ('omega', np.rad2deg(pos.omega)),
            ('nu',    np.rad2deg(pos.nu)),
        ]

    def _convertPos(self, pos):
        return pos.asL()

    def _readPos(self, maxage=0):
        return PositionFactory('l',
                               gamma=self._attached_gamma.read(maxage),
                               omega=self._attached_omega.read(maxage),
                               nu=self._attached_nu.read(maxage))

    def _createPos(self, gamma, omega, nu):  # pylint: disable=W0221
        return PositionFactory('l', gamma=gamma, omega=omega, nu=nu)

    def getScanWidthFor(self, hkl):
        """Get scanwidth.

        TODO: make this dependent on angles.
        """
        return 5.0


class SXTalIndex(AutoDevice, Moveable):
    """
    "Partial" devices for the H, K, L indices of the SXTAL instrument.
    """

    parameters = {
        'index': Param('The index into the SXTAL value', type=int),
    }

    attached_devices = {
        'sxtal': Attach('The spectrometer to control', SXTalBase),
    }

    valuetype = float

    hardware_access = False

    def doRead(self, maxage=0):
        return self._attached_sxtal.read(maxage)[self.index]

    def doStart(self, pos):
        current = list(self._attached_tas.read(0.5))
        current[self.index] = pos
        self._attached_tas.start(current)
