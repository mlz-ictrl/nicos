#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Custom TAS instrument class for PANDA."""

from nicos import session
from nicos.core import SIMULATION
from nicos.core.utils import multiWait
from nicos.devices.tas.mono import from_k
from nicos.devices.tas.spectro import TAS
from nicos.devices.generic.sequence import SequencerMixin, SeqDev


class PANDA(SequencerMixin, TAS):
    """TAS subclass for PANDA that does not move all axes at once,
    but positions the analyzer last.
    """

    def doReset(self):
        self.doWriteScatteringsense(self.scatteringsense)
        SequencerMixin.doReset(self)

    def doStart(self, pos):
        self.doWriteScatteringsense(self.scatteringsense)
        qh, qk, ql, ny = pos
        ny = self._thz(ny)
        angles = self._attached_cell.cal_angles(
            [qh, qk, ql], ny, self.scanmode, self.scanconstant,
            self.scatteringsense[1], self.axiscoupling, self.psi360)
        mono, ana, phi, psi, alpha = self._attached_mono, self._attached_ana, \
            self._attached_phi, self._attached_psi, self._attached_alpha

        movefirst = []
        self.log.debug('moving mono to %s', angles[0])
        movefirst.append(SeqDev(mono, from_k(angles[0], mono.unit)))
        self.log.debug('moving phi/stt to %s', angles[2])
        movefirst.append(SeqDev(phi, angles[2]))
        self.log.debug('moving psi/sth to %s', angles[3])
        movefirst.append(SeqDev(psi, angles[3]))
        if alpha is not None:
            self.log.debug('moving alpha to %s', angles[4])
            movefirst.append(SeqDev(alpha, angles[4]))
        seq = []
        # move mono/sample all at once
        seq.append(movefirst)
        # afterwards correct ana
        if self.scanmode != 'DIFF':
            self.log.debug('moving ana to %s', angles[1])
            seq.append(SeqDev(ana, from_k(angles[1], ana.unit)))
        # spurion check
        if self.spurioncheck and self._mode == SIMULATION:
            self._spurionCheck(pos)
        # store the min and max values of h,k,l, and E for simulation
        self._sim_setValue(pos)
        # start
        self._startSequence(seq)

    def _runFailed(self, i, action, exc_info):
        # stop all other motors on failure to start
        self.stop()
        raise exc_info[1]

    def _waitFailed(self, i, action, exc_info):
        # wait for all other motors on failure
        try:
            multiWait(self._getWaiters())
        except Exception:  # we want to reraise the original exception
            pass
        raise exc_info[1]

    def doFinish(self):
        SequencerMixin.doFinish(self)
        # make sure index members read the latest value
        for index in (self.h, self.k, self.l, self.E):
            if index._cache:
                index._cache.invalidate(index, 'value')

    def doStatus(self, maxage=0):
        # prefer sequence status to subdevice status
        if self._seq_is_running():
            return self._seq_status
        return SequencerMixin.doStatus(self, maxage)

    # -- resolution calculation methods

    def _getCollimation(self):
        ret = [6000]
        for devname in ['ca2', 'ca3', 'ca4']:
            try:
                dev = session.getDevice(devname)
                coll = dev.read()
            except Exception:
                self.log.warning('could not read collimation %s', devname,
                                 exc=1)
                coll = 'none'
            if coll == 'none':
                ret.append(6000)
            elif coll == '15m':
                ret.append(15)
            elif coll == '40m':
                ret.append(40)
            elif coll == '60m':
                ret.append(60)
            else:
                self.log.warning('unknown collimation setting %r for %s',
                                 coll, devname)
        for devname in ['cb1', 'cb2', 'cb3', 'cb4']:
            try:
                dev = session.getDevice(devname)
                coll = dev.read()
            except Exception:
                self.log.warning('could not read collimation %s', devname,
                                 exc=1)
                ret.append(6000)
            else:
                ret.append(coll)

        return ret

    def _getResolutionParameters(self):
        # read lengths
        lengths = {}
        for devname in ['lsm', 'lms', 'lsa', 'lad']:
            try:
                dev = session.getDevice(devname)
                l = dev.read()
            except Exception:
                self.log.warning('could not read %s', devname, exc=1)
                l = 100
            lengths[devname] = l

        return [
            1,     # circular (0) or rectangular (1) source
            13.5,  # width of source / diameter (cm)
            9.0,   # height of source / diameter (cm)
            0,     # no guide (0) or guide (1)
            1,     # horizontal guide divergence (min/AA)
            1,     # vertical guide divergence (min/AA)

            1,     # cylindrical (0) or cuboid (1) sample
            1.0,   # sample width / diameter perp. to Q (cm)
            1.0,   # sample width / diameter along Q (cm)
            1.0,   # sample height (cm)

            1,     # circular (0) or rectangular (1) detector
            2.5,   # width / diameter of the detector (cm)
            10.0,  # height / diameter of the detector (cm)

            0.2,   # thickness of monochromator (cm)
            23.1,  # width of monochromator (cm)
            19.8,  # height of monochromator (cm)

            0.2,   # thickness of analyzer (cm)
            17.0,  # width of analyzer (cm)
            15.0,  # height of analyzer (cm)

            lengths['lsm'],  # distance source - monochromator (cm)
            lengths['lms'],  # distance monochromator - sample (cm)
            lengths['lsa'],  # distance sample - analyzer (cm)
            lengths['lad'],  # distance analyzer - detector (cm)

            # automatically calculated from focmode and ki if they are zero
            0,     # horizontal curvature of monochromator (1/cm)
            0,     # vertical curvature of monochromator (1/cm)
            0,     # horizontal curvature of analyzer (1/cm)
            0,     # vertical curvature of analyzer (1/cm)

            100,   # distance monochromator - monitor (cm) XXX
            4.0,   # width of monitor (cm)
            10.0,  # height of monitor (cm)
        ]
