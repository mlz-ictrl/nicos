#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

"""Base single crystal instrument (Euler geometry)."""

import numpy as np

from nicos import session
from nicos.core import Attach, AutoDevice, LimitError, Moveable, Override, \
    Param, Value, dictof, intrange, listof, oneof, tupleof, vec3
from nicos.core.errors import InvalidValueError
from nicos.devices.generic.mono import Monochromator, from_k, to_k
from nicos.devices.instrument import Instrument

from nicos_sinq.sxtal.singlexlib import calcNBUBFromCellAndReflections, \
    calcTheta, calcUBFromCellAndReflections, rotatePsi, z1FromAngles, \
    z1FromNormalBeam, z1ToBisecting, z1ToNormalBeam
from nicos_sinq.sxtal.tasublib import calcPlaneNormal, calcTasQAngles, \
    calcTasQH, calcTasUBFromTwoReflections, energyToK, tasAngles, \
    tasQEPosition, tasReflection


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
        'center_counter': Param('Counter to use for centering',
                                type=str),
        'center_maxpts': Param('Width for centering', type=int,
                               userparam=True, settable=True,
                               default=60),
        'center_steps': Param('Step width for each angle to use for centering',
                              type=listof(float),
                              userparam=True, settable=True,
                              default=[0.2, 0.2, 0.2, 0.2]),
        'ccl_file': Param('Flag for writing CCL data files',
                          type=bool, default=False,
                          settable=True,
                          userparam=True),
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

    def doShutdown(self):
        for name in ['h', 'k', 'l']:
            if name in self.__dict__:
                self.__dict__[name].shutdown()

    def _calcPos(self, hkl, wavelength=None):
        """Calculate the Z1 vector for a given HKL position."""
        ub = session.experiment.sample.getUB()
        return ub.dot(np.array(list(hkl), dtype='float64'))

    def _extractPos(self, pos):
        """
        Calculates the settings angles from the Z1 vector pos
        Returns a list of tuples of devicename, angle
        """
        raise NotImplementedError

    def _convertPos(self, pos, wavelength=None):
        """Converts from angles for the given geometry to the Z1
        vector.
        Must be implemented in subclasses.
        """
        raise NotImplementedError

    def _readPos(self, maxage=0):
        """Create a position object with the current values of the attached
        devices.  Must be implemented in subclasses. Returns the Z1 vector
        calculated from the positions read
        """
        raise NotImplementedError

    def _createPos(self, **kwds):
        """Create a position object with the values of the given devices.
        Must be implemented in subclasses. **kwds contains angles. This returns
        the Z1 vector calculated from the angles given.
        """
        raise NotImplementedError

    def _checkPosList(self, poslist):
        """
        Checks if the positions in poslist are allowed.
        """
        ok, why = True, ''
        whyinfo = []
        for devname, value in poslist:
            dev = self._adevs[devname]
            if dev is None:
                continue
            devok, devwhy = dev.isAllowed(value)
            if not devok:
                ok = False
                whyinfo.append('target position %s outside limits '
                               'for %s: %s -- ' %
                               (dev.format(value, unit=True), dev, devwhy))
        if not ok:
            why = '---'.join(whyinfo)
        return ok, why

    def _calpos(self, hkl, checkonly=True):
        """Implements the calpos() command."""
        try:
            poslist = self._extractPos(self._calcPos(hkl))
        except Exception as err:
            return False, str(err)
        ok, why = self._checkPosList(poslist)
        if ok:
            self._last_calpos = hkl
            if checkonly:
                self.log.info('position allowed')
        else:
            if checkonly:
                self.log.warning('position not allowed: %s', why[:-4])
            else:
                raise LimitError(self, 'position not allowed: ' + why[:-4])

    def _reverse_calpos(self, ang):
        """Implements the pos2hkl() command."""
        pos = self._createPos(*ang)
        pos = self._convertPos(pos)
        ub = session.experiment.sample.getUB()
        ubinv = np.linalg.inv(ub)
        return tuple(ubinv.dot(pos))

    def _isToClose(self, poslist):
        """
        Test if this position it to close to the incoming beam
        """
        if poslist[0] > 3.:
            return True
        return False

    def doIsAllowed(self, hkl):
        try:
            poslist = self._extractPos(self._calcPos(hkl))
        except Exception as err:
            return False, str(err)
        zero = np.zeros((len(poslist),))
        if np.allclose(poslist, zero):
            return False, 'Failed to calculate angles for ' + str(hkl)
        if self._isToClose(poslist):
            return False, 'Reflection %s to close to incoming beam'\
                           % (str(hkl))
        # check limits for the individual axes
        ok, why = self._checkPosList(poslist)
        if not ok:
            return ok, why
        return True, ''

    def _sim_getMinMax(self):
        ret = []
        if self._sim_min is not None:
            for i, name in enumerate(['h', 'k', 'l']):
                ret.append((name, '%.4f' % self._sim_value[i],
                            '%.4f' % self._sim_min[i],
                            '%.4f' % self._sim_max[i]))
        return ret

    def _sim_setValue(self, pos):
        self._sim_old_value = self._sim_value
        self._sim_value = pos
        self._sim_min = tuple(map(min, pos, self._sim_min or pos))
        self._sim_max = tuple(map(max, pos, self._sim_max or pos))

    def doStart(self, hkl):
        poslist = self._extractPos(self._calcPos(hkl))
        for (devname, devvalue) in poslist:
            dev = self._adevs[devname]
            dev.start(devvalue)
        # store the min and max values of h,k,l, and E for simulation
        self._sim_setValue(hkl)

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
        pos = self._readPos(maxage)
        pos = self._convertPos(pos)
        ub = session.experiment.sample.getUB()
        ubinv = np.linalg.inv(ub)
        hkl = ubinv.dot(pos)
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
        """Get scanwidth as ``sqrt(u + v *tan Theta + w * tan² Theta)``."""
        cpos = self._calcPos(hkl)
        _, th = calcTheta(self.wavelength, cpos)
        tan_th = np.tan(th)
        w2 = self.scan_uvw[0] + \
            self.scan_uvw[1] * tan_th + \
            self.scan_uvw[2] * (tan_th ** 2)
        if w2 > 0:
            return np.sqrt(w2)
        else:
            return -np.sqrt(-w2)

    def get_motors(self):
        """Get the attached goniometer motors"""
        raise NotImplementedError

    def calc_ub(self, cell, r1, r2):
        """Calculate a UB matrix from the cell and two
        reflections"""
        raise NotImplementedError


class EulerSXTal(SXTalBase):

    attached_devices = {
        'ttheta': Attach('two-theta device', Moveable),
        'omega':  Attach('omega device', Moveable),
        'chi':    Attach('chi device', Moveable),
        'phi':    Attach('phi device', Moveable),
    }

    parameters = {
        'searchpars': Param('Limits and steps for peak searching',
                            dictof(str, tupleof(float, float, float)),
                            settable=True)
    }

    def _extractPos(self, pos):
        om, chi, phi = z1ToBisecting(self._attached_mono.read(0),
                                     pos)
        tth = 2. * om
        poslist = [
            ('ttheta', np.rad2deg(tth)),
            ('omega', np.rad2deg(om)),
            ('chi', np.rad2deg(chi)),
            ('phi', np.rad2deg(phi)),
        ]
        ok, _ = self._checkPosList(poslist)
        # If the calculated position violates limits, try to rotate
        # through the psi cone in order to find a working solutions.
        # This does not make sense though if we hit a limit in ttheta
        if not ok and self._attached_ttheta.isAllowed(np.rad2deg(tth)):
            for psi in range(0, 360, 10):
                ompsi, chipsi, phipsi = rotatePsi(om, chi, phi,
                                                  np.deg2rad(psi))
                psilist = [
                  ('ttheta', np.rad2deg(tth)),
                  ('omega', np.rad2deg(ompsi)),
                  ('chi', np.rad2deg(chipsi)),
                  ('phi', np.rad2deg(phipsi)),
                ]
                psiok, _ = self._checkPosList(psilist)
                if psiok:
                    poslist = psilist
                    break
        return poslist

    def _convertPos(self, pos, wavelength=None):
        return z1FromAngles(self.wavelength,
                            np.deg2rad(pos[0]),
                            np.deg2rad(pos[1]),
                            np.deg2rad(pos[2]),
                            np.deg2rad(pos[3]))

    def _readPos(self, maxage=0):
        apos = (self._attached_ttheta.read(maxage),
                self._attached_omega.read(maxage),
                self._attached_chi.read(maxage),
                self._attached_phi.read(maxage))
        return apos

    def _createPos(self, ttheta, omega, chi, phi):
        apos = (ttheta, omega, chi, phi)
        return apos

    def get_motors(self):
        return [
            self._attached_ttheta,
            self._attached_omega,
            self._attached_chi,
            self._attached_phi
        ]

    def _refl_to_dict(self, r):
        rd = {}
        rd['h'] = r[0][0]
        rd['k'] = r[0][1]
        rd['l'] = r[0][2]
        rd['stt'] = r[1][0]
        rd['om'] = r[1][1]
        rd['chi'] = r[1][2]
        rd['phi'] = r[1][3]
        return rd

    def calc_ub(self, cell, r1, r2):
        r1d = self._refl_to_dict(r1)
        r2d = self._refl_to_dict(r2)
        return calcUBFromCellAndReflections(cell, r1d, r2d)


class LiftingSXTal(SXTalBase):

    attached_devices = {
        'gamma':  Attach('gamma device', Moveable),
        'omega':  Attach('omega device', Moveable),
        'nu':     Attach('nu device (counter lifting axis)', Moveable),
    }

    def _extractPos(self, pos):
        gamma, omega, nu = z1ToNormalBeam(self.wavelength, pos)
        return [
            ('gamma', np.rad2deg(gamma)),
            ('omega', np.rad2deg(omega)),
            ('nu',    np.rad2deg(nu)),
        ]

    def _convertPos(self, pos, wavelength=None):
        return z1FromNormalBeam(self.wavelength,
                                np.deg2rad(pos[0]),
                                np.deg2rad(pos[1]),
                                np.deg2rad(pos[2]))

    def _readPos(self, maxage=0):
        apos = (self._attached_gamma.read(maxage),
                self._attached_omega.read(maxage),
                self._attached_nu.read(maxage))
        return apos

    def _createPos(self, gamma, omega, nu):
        apos = (gamma, omega, nu)
        return apos

    def get_motors(self):
        return [
            self._attached_ttheta,
            self._attached_omega,
            self._attached_nu,
        ]

    def _refl_to_dict(self, r):
        rd = {}
        rd['h'] = r[0][0]
        rd['k'] = r[0][1]
        rd['l'] = r[0][2]
        rd['gamma'] = r[1][0]
        rd['om'] = r[1][1]
        rd['nu'] = r[1][2]
        return rd

    def calc_ub(self, cell, r1, r2):
        r1d = self._refl_to_dict(r1)
        r2d = self._refl_to_dict(r2)
        return calcNBUBFromCellAndReflections(cell, r1d, r2d)


ENERGYMODES = ['FKI', 'FKE']


class TASSXTal(SXTalBase):
    """
    This is basically a Triple Axis Spectrometer as used at SINQ. It uses
    Mark Lumsden's UB matrix calculus. See J. Appl. Cryst. (2005). 38, 405-411
    https://doi.org/10.1107/S0021889805004875 for reference. This algorithm
    allows to reach reflections out of plane by using the sample table tilt
    angles. This also helps when the sample is not well aligned on the
    spectrometer.

    At SINQ, we use this in elastic and inelastic modes. This is controlled by
    the parameter inelastic which causes enegry to be drive when True. When
    false, energy is not driven and the attached analyzer and monochromator
    must be the same device.
    """

    attached_devices = {
        'ana': Attach('Analyzer device', Monochromator),
        'a3': Attach('Sample rotation angle', Moveable),
        'a4': Attach('Sample scattering angle', Moveable),
        'sgl': Attach('Sample lower tilt angle', Moveable),
        'sgu': Attach('Sample upper tilt angle', Moveable),
    }

    parameters = {
        'inelastic': Param('True for inelastic operation', type=bool,
                           mandatory=True, settable=False),
        'emode': Param('Energy driving mode', oneof(*ENERGYMODES),
                       settable=True, category='instrument',
                       default='FKI'),
        'scattering_sense': Param('Scattering sense at the sample',
                                  type=oneof(-1, 1), settable=True,
                                  default=1),
        'plane_normal': Param('Plane normal',
                              type=tupleof(float, float, float),
                              settable=True, default=(0, 0, 1)),
        'out_of_plane': Param('Flag if we may move out of plane or not',
                              type=bool, settable=True, default=True),
    }

    parameter_overrides = {
        'unit': Override(default='rlu rlu rlu meV', mandatory=False,
                         settable=True),
    }

    def doInit(self, mode):
        SXTalBase.doInit(self, mode)
        if self.inelastic:
            self.__dict__['en'] = SXTalIndex('en', unit='meV',
                                             fmtstr='%.3f', index=3,
                                             lowlevel=True, sxtal=self)
            self.valuetype = tupleof(float, float, float, float)

    def doShutdown(self):
        for name in ['h', 'k', 'l', 'en']:
            if name in self.__dict__:
                self.__dict__[name].shutdown()

    def _calcPos(self, hkle, wavelength=None):
        return hkle

    def _extractPos(self, hkle):
        ki = self._attached_mono.read(0)
        kf = self._attached_ana.read(0)
        if self.inelastic:
            if self.emode == 'FKI':
                kf = ki - hkle[3]
            else:
                ki = kf + hkle[3]
        ki = to_k(ki, self._attached_mono.unit)
        kf = to_k(kf, self._attached_ana.unit)
        qepos = tasQEPosition(ki, kf, hkle[0], hkle[1],
                              hkle[2], 0)
        ub = session.experiment.sample.getUB()
        try:
            angpos = calcTasQAngles(ub, np.array(self.plane_normal),
                                    self.scattering_sense, 0, qepos)
        except RuntimeError as xx:
            raise InvalidValueError(xx) from None

        poslist = [('a3', angpos.a3),
                   ('a4', angpos.sample_two_theta)]

        if self.inelastic:
            poslist.append(('mono', from_k(ki, self._attached_mono.unit)))
            poslist.append(('ana', from_k(kf, self._attached_ana.unit)))
        if self.out_of_plane:
            poslist.append(('sgu', angpos.sgu))
            poslist.append(('sgl', angpos.sgl))

        return poslist

    def _readPos(self, maxage=0):
        ki = to_k(self._attached_mono.read(maxage),
                  self._attached_mono.unit)
        kf = to_k(self._attached_ana.read(maxage),
                  self._attached_ana.unit)
        a3 = self._attached_a3.read(maxage)
        sample_two_theta = self._attached_a4.read(maxage)
        sgu = self._attached_sgu.read(maxage)
        sgl = self._attached_sgl.read(maxage)
        return ki, kf, a3, sample_two_theta, sgu, sgl

    def _createPos(self, ei, ef, a3, a4, sgu, sgl):
        return to_k(ei, 'meV'), to_k(ef, 'meV'), a3, a4, sgu, sgl

    def _convertPos(self, pos, wavelength=None):
        ki = pos[0]
        kf = pos[1]
        a = tasAngles(0, pos[2], pos[3], pos[5], pos[4], 0)
        ub = session.experiment.sample.getUB()
        q = calcTasQH(ub, a, ki, kf)
        en = from_k(ki, 'meV') - from_k(kf, 'meV')
        return q[0], q[1], q[2], en

    def doRead(self, maxage=0):
        pos = self._readPos(maxage)
        return self._convertPos(pos)

    def get_motors(self):
        return [
            self._attached_a3,
            self._attached_a4,
            self._attached_sgu,
            self._attached_sgl,
        ]

    def _isToClose(self, poslist):
        """
        Test if this position it to close to the incoming beam
        """
        if poslist[3] > 3.:
            return True
        return False

    def _rfl_to_reflection(self, r):
        """convert a reflection from reflection list format to internal
        tasublib format """
        # ei, ef is assumed to be in aux
        ki = energyToK(r[2][0])
        kf = energyToK(r[2][1])
        qe = tasQEPosition(ki, kf, r[0][0], r[0][1], r[0][2], .0)
        angles = tasAngles(0, r[1][0], r[1][1], r[1][2], r[1][3], 0)
        return tasReflection(qe=qe, angles=angles)

    def calc_ub(self, cell, r1, r2):
        tref1 = self._rfl_to_reflection(r1)
        tref2 = self._rfl_to_reflection(r2)
        self.plane_normal = calcPlaneNormal(tref1, tref2)
        return calcTasUBFromTwoReflections(cell, tref1, tref2)


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
        current = list(self._attached_sxtal.read(0.5))
        current[self.index] = pos
        self._attached_sxtal.start(current)
