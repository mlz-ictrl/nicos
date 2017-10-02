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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS triple-axis instrument devices."""

from math import pi

from nicos.core import Moveable, Param, Override, AutoDevice, Value, tupleof, \
    InvalidValueError, ComputationError, LimitError, oneof, multiStatus, Attach
from nicos.devices.tas.cell import Cell
from nicos.devices.tas.mono import Monochromator, THZ2MEV, from_k, to_k
from nicos.devices.tas import spurions
from nicos.devices.instrument import Instrument
from nicos.core import SIMULATION


SCANMODES = ['CKI', 'CKF', 'CPHI', 'CPSI', 'DIFF']

ENERGYTRANSFERUNITS = ['meV', 'THz']


class TAS(Instrument, Moveable):
    """An instrument class that can move in (q,w) space.

    When setting up a triple-axis configuration, use this as your instrument
    device (or derive an individual subclass).
    """

    attached_devices = {
        'cell':  Attach('Unit cell object to calculate angles', Cell),
        'mono':  Attach('Monochromator device', Monochromator),
        'ana':   Attach('Analysator device', Monochromator),
        'phi':   Attach('Sample scattering angle', Moveable),
        'psi':   Attach('Sample rocking angle', Moveable),
        'alpha': Attach('Device moved to "alpha" angle between ki and Q',
                        Moveable, optional=True),
    }

    parameters = {
        'scanmode':     Param('Operation mode: one of ' + ', '.join(SCANMODES),
                              type=oneof(*SCANMODES), default='CKI',
                              settable=True, category='instrument'),
        'scanconstant': Param('Constant of the operation mode', type=float,
                              default=0, settable=True, category='instrument'),
        'axiscoupling': Param('Whether the sample th/tt axes are coupled',
                              type=bool, default=True, settable=True,
                              category='instrument'),
        'psi360':       Param('Whether the range of psi is 0-360 deg '
                              '(otherwise -180-180 deg is assumed)',
                              type=bool, default=True, settable=True,
                              category='instrument'),
        'scatteringsense': Param('Scattering sense', default=(1, -1, 1),
                                 type=tupleof(oneof(1, -1),
                                              oneof(1, -1),
                                              oneof(1, -1)), settable=True,
                                 chatty=True, category='instrument'),
        'energytransferunit': Param('Energy transfer unit', type=str,
                                    default='THz', settable=True),
        'collimation':  Param('Collimation settings', type=str,
                              settable=True, category='instrument'),
        'spurioncheck': Param('Whether to check for spurions during simulation',
                              settable=True, type=bool, default=True),
    }

    parameter_overrides = {
        'fmtstr': Override(default='[%6.4f, %6.4f, %6.4f, %6.4f]'),
        'unit':   Override(default='rlu rlu rlu THz', mandatory=False,
                           settable=True)
    }

    valuetype = tupleof(float, float, float, float)

    hardware_access = False

    def doInit(self, mode):
        self.__dict__['h'] = TASIndex('h', unit='rlu', fmtstr='%.3f',
                                      index=0, lowlevel=True, tas=self)
        self.__dict__['k'] = TASIndex('k', unit='rlu', fmtstr='%.3f',
                                      index=1, lowlevel=True, tas=self)
        self.__dict__['l'] = TASIndex('l', unit='rlu', fmtstr='%.3f',
                                      index=2, lowlevel=True, tas=self)
        self.__dict__['E'] = TASIndex('E', unit=self.energytransferunit,
                                      fmtstr='%.3f', index=3, lowlevel=True,
                                      tas=self)
        self._last_calpos = None
        self._waiters = []

        if self.scatteringsense[0] != self._attached_mono.scatteringsense:
            self.log.warning('%s.scatteringsense is not the same as '
                             '%s.scatteringsense[0], please reset %s',
                             self._attached_mono, self, self)
        if self.scatteringsense[2] != self._attached_ana.scatteringsense:
            self.log.warning('%s.scatteringsense is not the same as '
                             '%s.scatteringsense[2], please reset %s',
                             self._attached_ana, self, self)

    def doShutdown(self):
        for name in ['h', 'k', 'l', 'E']:
            if name in self.__dict__:
                self.__dict__[name].shutdown()

    def _getWaiters(self):
        return [self._attached_mono, self._attached_ana,
                self._attached_phi, self._attached_psi, self._attached_alpha]

    def _thz(self, ny):
        if self.energytransferunit == 'meV':
            return ny / THZ2MEV
        return ny

    def doIsAllowed(self, pos):
        qh, qk, ql, ny = pos
        ny = self._thz(ny)
        try:
            angles = self._attached_cell.cal_angles(
                [qh, qk, ql], ny, self.scanmode, self.scanconstant,
                self.scatteringsense[1], self.axiscoupling, self.psi360)
        except ComputationError as err:
            return False, str(err)
        # check limits for the individual axes
        for devname, value in zip(['mono', 'ana', 'phi', 'psi', 'alpha'], angles):
            dev = self._adevs[devname]
            if dev is None:
                continue
            if isinstance(dev, Monochromator):
                ok, why = dev.isAllowed(from_k(value, dev.unit))
            else:
                ok, why = dev.isAllowed(value)
            if not ok:
                return ok, 'target position %s outside limits for %s: %s' % \
                    (dev.format(value, unit=True), dev, why)
        return True, ''

    def _sim_getMinMax(self):
        ret = []
        if self._sim_min is not None:
            for i, name in enumerate(['h', 'k', 'l', 'E']):
                ret.append((name, '%.4f' % self._sim_value[i],
                            '%.4f' % self._sim_min[i], '%.4f' % self._sim_max[i]))
        return ret

    def _sim_setValue(self, pos):
        self._sim_old_value = self._sim_value
        self._sim_value = pos
        self._sim_min = tuple(map(min, pos, self._sim_min or pos))
        self._sim_max = tuple(map(max, pos, self._sim_max or pos))

    def doReset(self):
        self.doWriteScatteringsense(self.scatteringsense)

    def doStart(self, pos):
        self.doWriteScatteringsense(self.scatteringsense)
        qh, qk, ql, ny = pos
        ny = self._thz(ny)
        angles = self._attached_cell.cal_angles(
            [qh, qk, ql], ny, self.scanmode, self.scanconstant,
            self.scatteringsense[1], self.axiscoupling, self.psi360)
        mono, ana, phi, psi, alpha = self._attached_mono, self._attached_ana, \
            self._attached_phi, self._attached_psi, self._attached_alpha
        self.log.debug('moving phi/stt to %s', angles[2])
        phi.start(angles[2])
        self.log.debug('moving psi/sth to %s', angles[3])
        psi.start(angles[3])
        if alpha is not None:
            self.log.debug('moving alpha to %s', angles[4])
            alpha.start(angles[4])
        self.log.debug('moving mono to %s', angles[0])
        mono.start(from_k(angles[0], mono.unit))
        if self.scanmode != 'DIFF':
            self.log.debug('moving ana to %s', angles[1])
            ana.start(from_k(angles[1], ana.unit))
        self._waiters = [mono, phi, psi]
        if alpha is not None:
            self._waiters.append(alpha)
        if self.scanmode != 'DIFF':
            self._waiters.append(ana)
        # spurion check
        if self.spurioncheck and self._mode == SIMULATION:
            self._spurionCheck(pos)
        # store the min and max values of h,k,l, and E for simulation
        self._sim_setValue(pos)

    def doFinish(self):
        # make sure index members read the latest value
        for index in (self.h, self.k, self.l, self.E):
            if index._cache:
                index._cache.invalidate(index, 'value')

    def doStatus(self, maxage=0):
        if self.scanmode == 'DIFF':
            return multiStatus(((name, self._adevs[name]) for name in
                                ['mono', 'phi', 'psi', 'alpha']), maxage)
        else:
            return multiStatus(((name, self._adevs[name]) for name in
                                ['mono', 'ana', 'phi', 'psi', 'alpha']), maxage)

    def doWriteScanmode(self, val):
        if val == 'DIFF':
            self.log.warning('Switching to two-axis mode; you are responsible '
                             'for moving the analyzer axes to the desired '
                             'position')

    def doWriteScatteringsense(self, val):
        self._attached_mono.scatteringsense = val[0]
        self._attached_ana.scatteringsense = val[2]

    def doReadUnit(self):
        return 'rlu rlu rlu %s' % self.energytransferunit

    def doWriteEnergytransferunit(self, val):
        if val not in ENERGYTRANSFERUNITS:
            raise InvalidValueError(self,
                                    'invalid energy transfer unit: %r' % val)
        if self._cache:
            self._cache.invalidate(self, 'value')
        self.unit = 'rlu rlu rlu %s' % val
        self.E.unit = val

    def valueInfo(self):
        return Value('h', unit='rlu', fmtstr='%.4f'), \
            Value('k', unit='rlu', fmtstr='%.4f'), \
            Value('l', unit='rlu', fmtstr='%.4f'), \
            Value('E', unit=self.energytransferunit, fmtstr='%.4f')

    def doRead(self, maxage=0):
        mono, ana, phi, psi = self._attached_mono, self._attached_ana, \
                              self._attached_phi, self._attached_psi
        # read out position
        monovalue = to_k(mono.read(maxage), mono.unit)
        if self.scanmode == 'DIFF':
            hkl = self._attached_cell.angle2hkl(
                [monovalue, monovalue, phi.read(maxage), psi.read(maxage)],
                self.axiscoupling)
            ny = 0
        else:
            anavalue = to_k(ana.read(maxage), ana.unit)
            hkl = self._attached_cell.angle2hkl(
                [monovalue, anavalue, phi.read(maxage), psi.read(maxage)],
                self.axiscoupling)
            ny = self._attached_cell.cal_ny(monovalue, anavalue)
            if self.energytransferunit == 'meV':
                ny *= THZ2MEV
        pos = [hkl[0], hkl[1], hkl[2], ny]
        return pos

    def _calpos(self, pos, printout=True, checkonly=True):
        qh, qk, ql, ny, sc, sm = pos
        ny = self._thz(ny)
        if sm is None:
            sm = self.scanmode
        if sc is None:
            sc = self.scanconstant
        try:
            angles = self._attached_cell.cal_angles(
                [qh, qk, ql], ny, sm, sc,
                self.scatteringsense[1], self.axiscoupling, self.psi360)
        except ComputationError as err:
            if checkonly:
                self.log.error('cannot calculate position: %s', err)
                return
            else:
                raise
        if not printout:
            return angles
        ok, why = True, ''
        for devname, value in zip(['mono', 'ana', 'phi', 'psi', 'alpha'], angles):
            dev = self._adevs[devname]
            if dev is None:
                continue
            if isinstance(dev, Monochromator):
                devok, devwhy = dev.isAllowed(from_k(value, dev.unit))
            else:
                devok, devwhy = dev.isAllowed(value)
            if not devok:
                ok = False
                why += 'target position %s outside limits for %s: %s -- ' % \
                    (dev.format(value, unit=True), dev, devwhy)
        self.log.info('ki:            %8.3f A-1', angles[0])
        if self.scanmode != 'DIFF':
            self.log.info('kf:            %8.3f A-1', angles[1])
        self.log.info('2theta sample: %8.3f deg', angles[2])
        self.log.info('theta sample:  %8.3f deg', angles[3])
        if self._attached_alpha is not None:
            self.log.info('alpha:         %8.3f deg', angles[4])
        if ok:
            self._last_calpos = pos
            if checkonly:
                self.log.info('position allowed')
        else:
            if checkonly:
                self.log.warning('position not allowed: %s', why[:-4])
            else:
                raise LimitError(self, 'position not allowed: ' + why[:-4])

    def _reverse_calpos(self, phi, psi, **kwds):
        if 'E' in kwds:
            ny = self._thz(kwds['E'])
            if self.scanmode == 'CKI':
                ki = self.scanconstant
                kf = self._attached_cell.cal_kf(ny, ki)
            elif self.scanmode == 'CKF':
                kf = self.scanconstant
                ki = self._attached_cell.cal_ki1(ny, kf)
            else:
                self.log.error('cannot calculate position with scanmode %s',
                               self.scanmode)
        elif 'ki' in kwds or 'kf' in kwds:
            ki = kwds.get('ki')
            kf = kwds.get('kf')
            if not ki or not kf:
                self.log.error('must give both ki and kf arguments')
        else:
            ki = self._attached_mono.read()
            kf = self._attached_ana.read()
        ny = self._attached_cell.cal_ny(ki, kf)
        if self.energytransferunit == 'meV':
            ny *= THZ2MEV
        hkl = self._calhkl([ki, kf, phi, psi])
        self.log.info('ki: %8.3f A-1', ki)
        self.log.info('kf: %8.3f A-1', kf)
        self.log.info('pos: [%.4f, %.4f, %.4f, %.4f] rlu rlu rlu %s',
                      *(tuple(hkl) + (ny, self.energytransferunit)))

    def _calhkl(self, angles):
        return self._attached_cell.angle2hkl(angles, self.axiscoupling)

    def _getCollimation(self):
        """Return current Soller collimator acceptance angles in minutes of arc.
        Order of the returned list must be alpha1-alpha4 then beta1-beta4.  If
        not installed, use '6000'.

        Must be overridden for instruments with collimation support.
        """
        def to_coll(v):
            if v == 'open':
                return 6000
            return int(v)
        try:
            a1, a2, a3, a4, b1, b2, b3, b4 = map(to_coll, self.collimation.split())
        except Exception:
            try:
                a1, a2, a3, a4 = map(to_coll, self.collimation.split())
            except Exception:
                self.log.warning('collimation parameter should be set to '
                                 '"a1 a2 a3 a4 b1 b2 b3 b4", assuming open')
                return [6000, 6000, 6000, 6000, 6000, 6000, 6000, 6000]
            else:
                return [a1, a2, a3, a4, 6000, 6000, 6000, 6000]
        else:
            return [a1, a2, a3, a4, b1, b2, b3, b4]

    def _getResolutionParameters(self):
        """Return a list of 30 parameters used for resolution calculation."""
        return [
            0,   # circular (0) or rectangular (1) source
            5,   # width of source / diameter (cm)
            5,   # height of source / diameter (cm)
            0,   # no guide (0) or guide (1)
            1,   # horizontal guide divergence (min/AA)
            1,   # vertical guide divergence (min/AA)

            1,   # cylindrical (0) or cuboid (1) sample
            1,   # sample width / diameter perp. to Q (cm)
            1,   # sample width / diameter along Q (cm)
            1,   # sample height (cm)

            1,   # circular (0) or rectangular (1) detector
            2.5, # width / diameter of the detector (cm)
            10,  # height / diameter of the detector (cm)

            0.2, # thickness of monochromator (cm)
            20,  # width of monochromator (cm)
            20,  # height of monochromator (cm)

            0.2, # thickness of analyzer (cm)
            15,  # width of analyzer (cm)
            15,  # height of analyzer (cm)

            200, # distance source - monochromator (cm)
            200, # distance monochromator - sample (cm)
            100, # distance sample - analyzer (cm)
            100, # distance analyzer - detector (cm)

            0,   # horizontal curvature of monochromator (1/cm)
            0,   # vertical curvature of monochromator (1/cm)
            0,   # horizontal curvature of analyzer (1/cm)
            0,   # vertical curvature of analyzer (1/cm)

            100, # distance monochromator - monitor (cm)
            4,   # width of monitor (cm)
            10,  # height of monitor (cm)
        ]

    def _spurionCheck(self, pos):
        for line in spurions.check_acc_bragg(self, *pos):
            self.log.info(line)
        for line in spurions.check_ho_spurions(
                to_k(self._attached_ana.read(), self._attached_ana.unit),
                pos[3] - 0.25, pos[3] + 0.25):
            self.log.info(line)
        kival = to_k(self._attached_mono.read(), self._attached_mono.unit)
        phival = self._attached_phi.read()
        for line in spurions.check_powderrays(kival, spurions.alu_hkl, phival):
            self.log.info(line)
        for line in spurions.check_powderrays(kival, spurions.copper_hkl, phival):
            self.log.info(line)


class TASIndex(AutoDevice, Moveable):
    """
    "Partial" devices for the H, K, L, E indices of the TAS instrument.
    """

    parameters = {
        'index': Param('The index into the TAS value', type=int),
    }

    attached_devices = {
        'tas': Attach('The spectrometer to control', TAS),
    }

    valuetype = float

    hardware_access = False

    def doRead(self, maxage=0):
        return self._attached_tas.read(maxage)[self.index]

    def doStart(self, pos):
        current = list(self._attached_tas.read(0.5))
        current[self.index] = pos
        self._attached_tas.start(current)


class TASConstant(Moveable):
    """
    Common class for TAS k, E and lambda pseudo-devices.
    """

    parameters = {
        'scanmode': Param('Scanmode to set', type=oneof(*SCANMODES),
                          mandatory=True),
    }

    parameter_overrides = {
        'unit':     Override(volatile=True),
    }

    attached_devices = {
        'base': Attach('Device to move (mono or ana)', Moveable),
        'tas':  Attach('The spectrometer for setting scanmode', TAS),
    }

    valuetype = float

    hardware_access = False

    def doStatus(self, maxage=0):
        return self._attached_base.status(maxage)

    def _getWaiters(self):
        return [self._attached_base]

    def _start(self, k):
        # first drive there, to determine if it is within limits
        tas = self._attached_tas
        base = self._attached_base
        pos = from_k(k, base.unit)
        base.start(pos)
        msg = False
        if tas.scanmode != self.scanmode:
            tas.scanmode = self.scanmode
            msg = True
        if tas.scanconstant != pos:
            tas.scanconstant = pos
            msg = True
        return msg

    def doReadUnit(self):
        # needed for "does volatile param have a doRead" checking
        raise NotImplementedError

    def doStop(self):
        self._attached_base.stop()

    def fix(self, reason=''):
        # fix the base as well, avoids surprises
        Moveable.fix(self, reason)
        return self._attached_base.fix(reason)

    def release(self):
        Moveable.release(self)
        return self._attached_base.release()


class Wavevector(TASConstant):
    """
    Device for adjusting initial/final wavevectors of the TAS and also setting
    the scanmode.
    """

    def doRead(self, maxage=0):
        base = self._attached_base
        return to_k(base.read(maxage), base.unit)

    def doStart(self, pos):
        tas = self._attached_tas
        if self._start(pos):
            tas.log.info('scan mode is now %s at %s',
                         self.scanmode, self.format(pos, unit=True))

    def doReadUnit(self):
        return 'A-1'


class Energy(TASConstant):
    """
    Device for adjusting initial/final energy of the TAS and also setting
    the scanmode.
    """

    def doRead(self, maxage=0):
        mono = self._attached_base
        return from_k(to_k(mono.read(maxage), mono.unit),
                      self._attached_tas.energytransferunit)

    def doStart(self, pos_e):
        tas = self._attached_tas
        if self._start(to_k(pos_e, tas.energytransferunit)):
            tas.log.info('scan mode is now %s at %s',
                         self.scanmode, self.format(pos_e, unit=True))

    def doReadUnit(self):
        return self._attached_tas.energytransferunit


class Wavelength(TASConstant):
    """
    Device for adjusting initial/final wavelength of the TAS and also setting
    the scanmode.
    """

    def doRead(self, maxage=0):
        mono = self._attached_base
        return 2 * pi / to_k(mono.read(maxage), mono.unit)

    def doStart(self, lam):
        tas = self._attached_tas
        if self._start(to_k(lam, 'A')):
            tas.log.info('scan mode is now %s at %s',
                         self.scanmode, self.format(lam, unit=True))

    def doReadUnit(self):
        return 'AA'
