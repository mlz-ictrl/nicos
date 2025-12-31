# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
    Param, Value, dictof, listof, nicosdev, oneof, tupleof
from nicos.core.errors import InvalidValueError, UsageError
from nicos.devices.generic.mono import Monochromator, from_k
from nicos.devices.sxtal.instrument import SXTalBase as NicosSXTalBase, \
    SXTalIndex

from nicos_sinq.sxtal.singlexlib import calcNBUBFromCellAndReflections, \
    calcTheta, calcUBFromCellAndReflections, eulerian_to_kappa, \
    kappa_to_eulerian, rotatePsi, z1FromAngles, z1FromNormalBeam, \
    z1ToBisecting, z1ToNormalBeam
from nicos_sinq.sxtal.tasublib import KToEnergy, calcPlaneNormal, \
    calcTasQAngles, calcTasQH, calcTasUBFromTwoReflections, energyToK, \
    tasAngles, tasQEPosition, tasReflection


class SXTalBase(NicosSXTalBase):
    """An instrument class that can move in q space.

    When setting up a single xtal configuration, use a subclass that reflects
    the instrument geometry as your instrument device.
    """

    parameters = {
        'scan_width_multiplier': Param('Multiplier for the scan width '
                                       'calculated from scan_uvw',
                                       type=float, userparam=True,
                                       settable=True, default=3.),
        'center_counter': Param('Counter to use for centering',
                                type=str),
        'center_maxpts': Param('Width for centering', type=int,
                               userparam=True, settable=True,
                               default=60),
        'center_order': Param('Optional order of motors for centering',
                              type=listof(nicosdev), userparam=True,
                              settable=True, default=[]),
        'center_steps': Param('Step width for each angle to use for centering',
                              type=listof(float),
                              userparam=True, settable=True,
                              default=[0.2, 0.2, 0.2, 0.2]),
        'ccl_file': Param('Flag for writing CCL data files',
                          type=bool, default=False,
                          settable=True,
                          userparam=True),
        'orienting_reflections': Param('Reflections from which the UB'
                                       'was calculated',
                                       type=tupleof(int, int), settable=True,
                                       default=(0, 0)),
    }

    def _calcPos(self, hkl, wavelength=None):
        """Calculate the Z1 vector for a given HKL position."""
        ub = session.experiment.sample.getUB()
        return ub.dot(np.array(list(hkl), dtype='float64'))

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
        return abs(poslist[0][1]) <= 3

    def doIsAllowed(self, hkl):
        try:
            poslist = self._extractPos(self._calcPos(hkl))
        except Exception as err:
            return False, str(err)
        zero = np.zeros((len(poslist),))
        if np.allclose([p[1] for p in poslist], zero):
            return False, 'Failed to calculate angles for ' + str(hkl)
        if self._isToClose(poslist):
            return False, 'Reflection %s to close to incoming beam %s' % hkl
        # check limits for the individual axes
        ok, why = self._checkPosList(poslist)
        if not ok:
            return ok, why
        return True, ''

    def doRead(self, maxage=0):
        pos = self._readPos(maxage)
        pos = self._convertPos(pos)
        ub = session.experiment.sample.getUB()
        ubinv = np.linalg.inv(ub)
        hkl = ubinv.dot(pos)
        return list(hkl)

    def getScanWidthFor(self, hkl):
        """Get scanwidth as ``sqrt(u + v *tan Theta + w * tan² Theta)``."""
        cpos = self._calcPos(hkl)
        _, th = calcTheta(self.wavelength, cpos)
        tan_th = np.tan(th)
        w2 = self.scan_uvw[0] + \
            self.scan_uvw[1] * tan_th + \
            self.scan_uvw[2] * (tan_th ** 2)
        return abs(w2)

    def get_motors(self):
        """Get the attached goniometer motors"""
        raise NotImplementedError

    def calc_ub(self, cell, r1, r2):
        """Calculate a UB matrix from the cell and two
        reflections"""
        raise NotImplementedError

    def doStop(self):
        # The "Measure" command in nicos_sinq/sxtal/commands/__init__.py does
        # set the parameter ccl_file to True before starting a measurement and
        # to False after the measurement is done. However, in case the device is
        # stopped (e.g. by an emergency stop), this parameter needs to be reset
        # manually.
        if hasattr(NicosSXTalBase, 'doStop'):
            NicosSXTalBase.doStop(self)
        self.ccl_file = False


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
                            settable=True),
        't2angle': Param('Two theta angle when to switch to t2t mode',
                         type=float, settable=True, userparam=True,
                         default=60.),
        'use_psi': Param('If to use the psi angle in calculations', type=bool,
                         settable=True, userparam=True, default=False),
        'psi_target': Param('Target for the PSI angle', type=float,
                            internal=True, settable=True),
    }

    def doInit(self, mode):
        SXTalBase.doInit(self, mode)
        self.add_autodevice('psi', SXTalPSI, namespace='global',
                            unit='degree', mtstr='%.3f',
                            visibility=self.autodevice_visibility, sxtal=self)
        if self.use_psi:
            self.fmtstr = '[%6.4f, %6.4f, %6.4f, %6.4f]'
            self.valuetype = tupleof(float, float, float, float)
        self.psi_target = 0

    def _calcPos(self, hkl, wavelength=None):
        """Calculate the Z1 vector for a given HKL position."""
        if len(hkl) < 3:
            raise UsageError('Need at least three reciprocal space'
                             ' coordinates')
        if len(hkl) > 3:
            self.psi_target = hkl[3]
            hkl = hkl[0:3]
        ub = session.experiment.sample.getUB()
        return ub.dot(np.array(list(hkl), dtype='float64'))

    def _extractPos(self, pos):
        om, chi, phi = z1ToBisecting(self.wavelength,
                                     pos)
        tth = 2. * om
        if self.use_psi:
            om, chi, phi = rotatePsi(om, chi, phi,
                                     np.deg2rad(self.psi_target))
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
        if not ok and self._attached_ttheta.isAllowed(np.rad2deg(tth))\
                and not self.use_psi:
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
                    self.psi_target = psi
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

    def doRead(self, maxage=0):
        hkl = SXTalBase.doRead(self, maxage)
        if self.use_psi:
            hkl.append(self.psi_target)
        return hkl

    def doWriteUse_Psi(self, val):
        if val:
            self.fmtstr = '[%6.4f, %6.4f, %6.4f, %6.4f]'
            self.valuetype = tupleof(float, float, float, float)
        else:
            self.fmtstr = '[%6.4f, %6.4f, %6.4f]'
            self.valuetype = tupleof(float, float, float)

    def valueInfo(self):
        if self.use_psi:
            return Value('h', unit='rlu', fmtstr='%.4f'), \
                Value('k', unit='rlu', fmtstr='%.4f'), \
                Value('l', unit='rlu', fmtstr='%.4f'), \
                Value('psi', unit='degree', fmtstr='%.4f')
        return SXTalBase.valueInfo(self)


class LiftingSXTal(SXTalBase):

    attached_devices = {
        'gamma':  Attach('gamma device', Moveable),
        'omega':  Attach('omega device', Moveable),
        'nu':     Attach('nu device (counter lifting axis)', Moveable),
    }

    def doInit(self, mode):
        # for pseudo two theta scans to work
        self._attached_ttheta = self._attached_gamma
        SXTalBase.doInit(self, mode)

    def _extractPos(self, pos):
        gamma, omega, nu = z1ToNormalBeam(self.wavelength, pos)
        om = np.rad2deg(omega)
        if om < -180:
            om += 360
        return [
            ('gamma', np.rad2deg(gamma)),
            ('omega', om),
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
            self._attached_gamma,
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


class KappaSXTal(SXTalBase):
    """ Kappa geometry goniometer"""

    attached_devices = {
        'stt': Attach('Two Theta', Moveable),
        'omega': Attach('Kappa omega device', Moveable),
        'kappa': Attach('kappa motor', Moveable),
        'kphi': Attach('Kappa phi rotation', Moveable),
    }

    parameters = {
        'searchpars': Param('Limits and steps for peak searching',
                            dictof(str, tupleof(float, float, float)),
                            settable=True),
        'kappa_angle': Param('Kappa angle of the goniometer',
                             type=float, mandatory=True),
        'right_hand': Param('Boolean if the goniometer is right handed or not',
                            type=bool, mandatory=True),
    }

    def _extractPos(self, pos):
        eom, echi, ephi = z1ToBisecting(self.wavelength,
                                        pos)
        # Chi must be below 2*alpha for the kappa calculation to work.
        # Thus we rotate in PSI until this is the case.
        stt = np.rad2deg(eom) * 2.
        psi = 10
        psichi = echi
        psiom = eom
        psiphi = ephi
        while psichi > 2. * np.deg2rad(self.kappa_angle) and psi < 360:
            psiom, psichi, psiphi = rotatePsi(eom, echi, ephi, np.deg2rad(psi))
            # self.log.info('chi, psi: %f, %f', np.rad2deg(psichi), psi)
            psi += 10
        # self.log.info('Found solution at psi: %f', psi)
        # self.log.info('Kappa eulerian, om, chi, phi: %f, %f, %f',
        #              np.rad2deg(psiom), np.rad2deg(psichi),
        #              np.rad2deg(psiphi))
        status, komega, kappa, kphi = eulerian_to_kappa(np.rad2deg(psiom),
                                                        np.rad2deg(psichi),
                                                        np.rad2deg(psiphi),
                                                        self.kappa_angle,
                                                        self.right_hand)
        # This code not be needed if we have a motor with limits
        # in the 0 - 360 range
        if kphi < -180.:
            kphi += 360.
        if kphi > 180.:
            kphi -= 360.
        # self.log.info('Kappa om, kappa, kphi: %f, %f, %f', komega,
        #              kappa, kphi)
        if not status:
            self.log.error('Cannot reach reflection')
        return [('stt', stt), ('omega', komega),
                ('kappa', kappa), ('kphi', kphi)]

    def _convertPos(self, pos, wavelength=None):
        status, om, chi, phi = kappa_to_eulerian(pos[1], pos[2], pos[3],
                                                 self.kappa_angle,
                                                 self.right_hand)
        # self.log.info('Eulerian om, chi, phi when calculating back:'
        #              ' %f, %f, %f',
        #              om, chi, phi)
        if status:
            return z1FromAngles(self.wavelength,
                                np.deg2rad(pos[0]),
                                np.deg2rad(om),
                                np.deg2rad(chi),
                                np.deg2rad(phi))
        else:
            self.log.error('Failed to convert from kappa to Eulerian angles')
            return [1., 0, 0]

    def _readPos(self, maxage=0):
        apos = (self._attached_stt.read(maxage),
                self._attached_omega.read(maxage),
                self._attached_kappa.read(maxage),
                self._attached_kphi.read(maxage))
        return apos

    def _createPos(self, stt, komega, kappa, kphi):
        apos = (stt, komega, kappa, kphi)
        return apos

    def get_motors(self):
        return [
            self._attached_stt,
            self._attached_omega,
            self._attached_kappa,
            self._attached_kphi
        ]

    def _refl_to_dict(self, r):
        status, om, chi, phi = kappa_to_eulerian(r[1][1], r[1][2], r[1][3],
                                                 self.kappa_angle,
                                                 self._right_hand)
        if not status:
            self.log.error('Failed to convert from kappa to Eulerian angles')
        rd = {}
        rd['h'] = r[0][0]
        rd['k'] = r[0][1]
        rd['l'] = r[0][2]
        rd['stt'] = r[1][0]
        rd['om'] = om
        rd['chi'] = chi
        rd['phi'] = phi
        return rd

    def calc_ub(self, cell, r1, r2):
        r1d = self._refl_to_dict(r1)
        r2d = self._refl_to_dict(r2)
        return calcUBFromCellAndReflections(cell, r1d, r2d)


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
    the parameter inelastic which causes energy to be drive when True. When
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
                                  category='instrument', default=1),
        'plane_normal': Param('Plane normal',
                              type=tupleof(float, float, float),
                              settable=True, default=(0, 0, 1),
                              category='instrument'),
        'out_of_plane': Param('Flag if we may move out of plane or not',
                              type=bool, settable=True,
                              category='instrument', default=True),
    }

    parameter_overrides = {
        'unit': Override(default='rlu rlu rlu meV', mandatory=False,
                         settable=True),
    }

    def doInit(self, mode):
        SXTalBase.doInit(self, mode)
        if self.inelastic:
            self.add_autodevice('en', SXTalIndex, namespace='global',
                                unit='meV', fmtstr='%.3f', index=3,
                                visibility=self.autodevice_visibility,
                                sxtal=self)
            self.valuetype = tupleof(float, float, float, float)

    def _calcPos(self, hkl, wavelength=None):
        return hkl

    def _extractPos(self, pos):
        ki = self._attached_mono.read(0)
        kf = self._attached_ana.read(0)
        if self.inelastic:
            if self.emode == 'FKI':
                kf = ki - pos[3]
            else:
                ki = kf + pos[3]
        ki = energyToK(ki)
        kf = energyToK(kf)
        qepos = tasQEPosition(ki, kf, pos[0], pos[1], pos[2], 0)
        ub = session.experiment.sample.getUB()
        try:
            angpos = calcTasQAngles(ub, np.array(self.plane_normal),
                                    self.scattering_sense, 0, qepos)
        except RuntimeError as xx:
            raise InvalidValueError(xx) from None

        poslist = [('a3', angpos.a3),
                   ('a4', angpos.sample_two_theta)]

        if self.out_of_plane:
            poslist.append(('sgu', angpos.sgu))
            poslist.append(('sgl', angpos.sgl))
        else:
            poslist.append(('sgu', 0))
            poslist.append(('sgl', 0))

        if self.inelastic:
            poslist.append(('mono', from_k(ki, self._attached_mono.unit)))
            poslist.append(('ana', from_k(kf, self._attached_ana.unit)))

        return poslist

    def _readPos(self, maxage=0):
        ki = energyToK(self._attached_mono.read(maxage))
        kf = energyToK(self._attached_ana.read(maxage))
        a3 = self._attached_a3.read(maxage)
        sample_two_theta = self._attached_a4.read(maxage)
        if self.out_of_plane:
            sgu = self._attached_sgu.read(maxage)
            sgl = self._attached_sgl.read(maxage)
        else:
            sgu = 0
            sgl = 0
        return ki, kf, a3, sample_two_theta, sgu, sgl

    def _createPos(self, ei, ef, a3, a4, sgu, sgl):
        return energyToK(ei), energyToK(ef), a3, a4, sgu, sgl

    def _convertPos(self, pos, wavelength=None):
        ki = pos[0]
        kf = pos[1]
        a = tasAngles(0, pos[2], pos[3], pos[5], pos[4], 0)
        ub = session.experiment.sample.getUB()
        q = calcTasQH(ub, a, ki, kf)
        en = KToEnergy(ki) - KToEnergy(kf)
        return q[0], q[1], q[2], en

    def doRead(self, maxage=0):
        pos = self._readPos(maxage)
        return list(self._convertPos(pos))

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
        return abs(poslist[1][1]) <= 3

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

    def valueInfo(self):
        if self.inelastic:
            return Value('h', unit='rlu', fmtstr='%.4f'), \
                Value('k', unit='rlu', fmtstr='%.4f'), \
                Value('l', unit='rlu', fmtstr='%.4f'), \
                Value('en', unit='mev', fmtstr='%.4f')
        return SXTalBase.valueInfo(self)


class SXTalPSI(AutoDevice, Moveable):
    """
    "Partial" device for the PSI angle of an Eulerian cradle instrument
    """

    attached_devices = {
        'sxtal': Attach('The spectrometer to control', EulerSXTal),
    }

    valuetype = float

    hardware_access = False

    def doRead(self, maxage=0):
        return self._attached_sxtal.psi_target

    def doIsAllowed(self, target):
        if not self._attached_sxtal.use_psi:
            return False, 'Can only use PSI when use_psi is enabled on %s' \
                % self._attached_sxtal.name

    def doStart(self, target):
        current = list(self._attached_sxtal.read(0.5))
        current[3] = target
        self._attached_sxtal.start(current)
