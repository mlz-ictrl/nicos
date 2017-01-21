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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Cryopad related polarization devices."""

from nicos.core import Param, Override, Attach, Moveable, multiStatus, \
    status, tupleof, listof, oneof
from nicos.devices.sxtal.instrument import SXTalBase
from nicos.devices.generic.switcher import Switcher

from . import calc


class BaseCryopad(Moveable):
    """Controls the whole state of the cryopad.

    How to determine the wavelength and sample angles must be implemented
    in subclasses, via the _getInstr* methods.
    """

    attached_devices = {
        'nut_in':   Attach('Incoming nutator axis', Moveable),
        'prec_in':  Attach('Incoming precession current', Moveable),
        'nut_out':  Attach('Outgoing nutator axis', Moveable),
        'prec_out': Attach('Outgoing precession current', Moveable),
    }

    parameters = {
        # 01/2017: [108.27, 0, 0, 80.73, 0, 0]
        'coefficients':       Param('Coefficients for calculating currents',
                                    type=listof(float), settable=True,
                                    default=[108.46, 0, 0, 80.77, 0, 0]),
        'meissnercorrection': Param('Correct for curved Meissner shield?',
                                    type=bool, default=True),
    }

    parameter_overrides = {
        'fmtstr':  Override(default='%.1f %.1f / %.1f %.1f'),
    }

    valuetype = tupleof(float, float, float, float)

    def _getWaiters(self):
        return [self._attached_nut_in, self._attached_nut_out,
                self._attached_prec_in, self._attached_prec_out]

    def _getInstrPosition(self, maxage=None):
        """Return (lambda_in, lambda_out, gamma, sense) of the instrument.

        Wavelength must be in Angstrom, the angles must be in degrees.
        """
        raise NotImplementedError

    def _getInstrTarget(self):
        """Return targets (lambda_in, lambda_out, gamma, sense) of the
        instrument.
        """
        raise NotImplementedError

    def doRead(self, maxage=None):
        lam_in, lam_out, gamma, sense = self._getInstrPosition(maxage)
        prec_in = self._attached_prec_in.read(maxage)
        prec_out = self._attached_prec_out.read(maxage)
        theta_in = self._attached_nut_in.read(maxage)
        theta_out = self._attached_nut_out.read(maxage)

        if self.meissnercorrection:
            theta_out -= calc.curved_meissner_correction(theta_out)

        chi_in, chi_out = calc.currents_to_angles(
            self.coefficients, prec_in, prec_out, lam_in, lam_out, gamma)
        self.log.debug('chi_in=%s, chi_out=%s', chi_in, chi_out)
        xyz_in = calc.pol_in_from_angles(sense, theta_in, chi_in, lam_in, lam_out, gamma)
        xyz_out = calc.pol_out_from_angles(sense, theta_out, chi_out, lam_in, lam_out, gamma)
        self.log.debug('xyz_in=%s, xyz_out=%s', xyz_in, xyz_out)

        polar_in = calc.polar_angles_from_xyz(*xyz_in)
        polar_out = calc.polar_angles_from_xyz(*xyz_out)
        return polar_in + polar_out   # a 4-tuple

    def doStart(self, target):
        lam_in, lam_out, gamma, sense = self._getInstrTarget()
        polar_th_in, polar_phi_in, polar_th_out, polar_phi_out = target

        theta_in, chi_in = calc.cryopad_in(sense, lam_in, lam_out, gamma,
                                           polar_th_in, polar_phi_in)
        theta_in, chi_in = calc.optimize_angles(theta_in, chi_in)

        theta_out, chi_out = calc.cryopad_out(sense, lam_in, lam_out, gamma,
                                              polar_th_out, polar_phi_out)
        theta_out, chi_out = calc.optimize_angles(theta_out, chi_out)

        if self.meissnercorrection:
            theta_out += calc.curved_meissner_correction(theta_out)

        prec_in, prec_out = calc.angles_to_currents(
            self.coefficients, chi_in, chi_out, lam_in, lam_out, gamma)

        self._attached_nut_in.start(theta_in)
        self._attached_nut_out.start(theta_out)
        self._attached_prec_in.start(prec_in)
        self._attached_prec_out.start(prec_out)


class SXTalCryopad(BaseCryopad):

    attached_devices = {
        'sxtal':  Attach('Single-crystal instrument', SXTalBase),
        'ttheta': Attach('Two-theta motor', Moveable),
    }

    def _getInstrPosition(self, maxage=None):
        lam = self._attached_sxtal.wavelength
        # XXX: check signs of angles and sense
        return lam, lam, self._attached_ttheta.read(maxage), 1

    def _getInstrTarget(self):
        lam = self._attached_sxtal.wavelength
        # XXX: check signs of angles and sense
        return lam, lam, self._attached_ttheta.target, 1


class CryopadPol(Moveable):
    """Controls the incoming or outgoing polarization direction."""

    attached_devices = {
        'cryopad': Attach('Underlying Cryopad device', BaseCryopad)
    }

    parameters = {
        'side':    Param('Which side of the instrument is this device?',
                         type=oneof('in', 'out'), mandatory=True),
    }

    parameter_overrides = {
        'unit':    Override(mandatory=False, default=''),
    }

    valuetype = oneof('+x', '-x', '+y', '-y', '+z', '-z')

    def doRead(self, maxage=0):
        # NOTE: for now, we just return the latest target because it became
        # necessary to introduce corrections to nutator angles that cannot yet
        # be included reliably in the calculations, and would change the readout
        # here to "unknown".
        return self.target
        # cppos = self._attached_cryopad.read(maxage)
        # theta, chi = cppos[0:2] if self.side == 'in' else cppos[2:4]
        # for (pos, (goaltheta, goalchi)) in calc.DIRECTIONS.items():
        #     # fix chi = -179.5, goalchi = 180 situation
        #     diffchi = abs(chi - goalchi)
        #     chiok = diffchi < 0.5 or 359.5 < diffchi < 360.5
        #     # XXX: make precision configurable
        #     if abs(theta - goaltheta) < 0.5 and chiok:
        #         return pos
        # return 'unknown'

    def doStatus(self, maxage=0):
        st, text = multiStatus(self._adevs)
        if st == status.BUSY:
            return st, text
        if self.read(maxage) == 'unknown':
            return status.NOTREACHED, 'unknown polarization setting'
        return status.OK, 'idle'

    def doStart(self, pos):
        theta_chi = calc.DIRECTIONS[pos]
        cppos = self._attached_cryopad.target or (0, 0, 0, 0)
        if self.side == 'in':
            target = tuple(theta_chi) + cppos[2:4]
        else:
            target = cppos[0:2] + tuple(theta_chi)
        self._attached_cryopad.start(target)


class CryopadFlip(Switcher):
    """Controls the nutator current used as a flipper."""

    def doInit(self, mode):
        Switcher.doInit(self, mode)
        self._onoff = list(self.mapping)
        self.valuetype = oneof('same', 'switch', *self._onoff)

    def doStatus(self, maxage=0):
        st, text = Switcher.doStatus(self, maxage)
        if st == status.UNKNOWN:
            st, text = status.NOTREACHED, 'invalid flipper current'
        return st, text

    def doIsAllowed(self, target):
        if target in ('same', 'switch'):
            return True, ''
        return Switcher.doIsAllowed(self, target)

    def doStart(self, target):
        if target == 'same':
            real_tgt = self.read(0)
            if real_tgt == 'unknown':
                real_tgt = self._onoff[0]
            self._setROParam('target', real_tgt)
            return
        if target == 'switch':
            if self.read(0) == self._onoff[0]:
                self._setROParam('target', self._onoff[1])
                Switcher.doStart(self, self._onoff[1])
            else:
                self._setROParam('target', self._onoff[0])
                Switcher.doStart(self, self._onoff[0])
        else:
            Switcher.doStart(self, target)
