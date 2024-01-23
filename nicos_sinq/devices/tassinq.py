# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from nicos.core.errors import ComputationError, LimitError, ProgrammingError
from nicos.core.params import Override
from nicos.devices.generic.mono import Monochromator, from_k, to_k
from nicos.devices.tas import TAS


class SinqTAS(TAS):
    """
    This just makes the sure that the scanconstant is read from
    the proper device, as requested by the scanmode
    """
    parameter_overrides = {
        'scanconstant': Override(settable=False, volatile=True),
    }

    def doReadScanconstant(self):
        if self.scanmode in ['CKI', 'DIFF']:
            return to_k(self._attached_mono.read(0),
                        self._attached_mono.unit)
        elif self.scanmode == 'CKF':
            return to_k(self._attached_ana.read(0),
                        self._attached_ana.unit)
        elif self.scanmode == 'CPSI':
            return self._attached_psi.read()
        elif self.scanmode == 'CPHI':
            return self._attached_phi.read(0)
        raise ProgrammingError()

    def _calpos(self, pos, printout=True, checkonly=True):
        """
        Custom calpos for SINQ printing all A* angles
        """
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
            raise
        if not printout:
            return angles
        ok, why = True, ''
        for devname, value in zip(['mono', 'ana', 'phi', 'psi', 'alpha'],
                                  angles):
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
        th, tth = self._attached_mono._calc_angles(angles[0])
        self.log.info('A1: %8.3f', th)
        self.log.info('A2: %8.3f', tth)
        self.log.info('A3: %8.3f deg', angles[3])
        self.log.info('A4: %8.3f deg', angles[2])
        th, tth = self._attached_ana._calc_angles(angles[1])
        self.log.info('A5: %8.3f', th)
        self.log.info('A6: %8.3f', tth)
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
