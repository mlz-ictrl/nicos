#  -*- Coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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

import math

from nicos.core import multiStatus, status
from nicos.core.device import Attach, Moveable, Param, listof
from nicos.devices.generic.mono import to_k

from nicos_sinq.devices.logical_motor import InterfaceLogicalMotorHandler
from nicos_sinq.devices.mono import SinqMonochromator


class EigerA2Controller(InterfaceLogicalMotorHandler):
    """
    The EIGER monochromators has a slit for the outgoing
    beam which is realised through two moving shielding blocks.
    Thus, whenever moving A2, these slit blocks have to be moved
    as well. The other logical motor attached is the slit width.
    """
    parameters = {
        'sizes': Param('Left and right block sizes',
                       type=listof(float), mandatory=False,
                       default=[-101.5, -3.5])
    }
    attached_devices = {
        'reala2': Attach('Motor for really moving A2', Moveable),
        'right': Attach('Motor for moving the right slit block', Moveable),
        'left': Attach('Motor for moving the left slit block', Moveable),
    }

    def doPreinit(self, mode):
        self._status_devs = ['reala2', 'right', 'left']
        InterfaceLogicalMotorHandler.doPreinit(self, mode)

    def doRead(self, maxage=0):
        result = {}
        result['a2'] = self._attached_reala2.doRead(maxage)
        a2Target = self._attached_reala2.target
        vall = self._attached_left.doRead(maxage)
        valr = self._attached_right.doRead(maxage)
        d2ro = self.sizes[1] - a2Target
        d2lo = self.sizes[0] + a2Target
        a2w = (d2lo - vall) + (d2ro - valr)
        result['a2w'] = abs(a2w)
        return result

    def _get_move_list(self, targets):
        positions = []

        a2 = targets['a2']
        positions.append((self._attached_reala2, a2))

        a2w = targets['a2w']
        right = self.sizes[1] - a2 + a2w/2.
        left = self.sizes[0] + a2 + a2w/2.
        positions.append((self._attached_right, right))
        positions.append((self._attached_left, left))
        return positions


class EigerMonochromator(SinqMonochromator):
    """
    In addition to the normal focussing motors, EIGER also
    drives a monochromator translation.
    """
    attached_devices = {
        'mt': Attach('Monochromator translation', Moveable,
                     optional=True),
    }

    parameters = {
        'translation_pars': Param('Parameters mta, mtb for controlling the '
                                  'monochromator translation',
                                  type=listof(float), default=[0, 3.5]),
    }

    def _movefoci(self, focmode, th, hfocuspars, vfocuspars):
        focusv = self._attached_focusv
        if focusv:
            curve = vfocuspars[0] + vfocuspars[1]/math.sin(math.radians(
                abs(th)))
            focusv.move(curve)
            self.log.info('Moving %s to %8.4f', focusv.name, curve)
        focush = self._attached_focush
        if focush:
            hcurve = hfocuspars[0] + hfocuspars[1]*math.sin(math.radians(
                abs(th)))
            focush.move(hcurve)
            self.log.info('Moving %s to %8.4f', focush.name, hcurve)
        mt = self._attached_mt
        if mt:
            mtpos = self.translation_pars[0] + self.translation_pars[1] * pow(
                curve, .75)
            limits = mt.abslimits
            if mtpos <= limits[0]:
                mtpos = limits[0] + .1
            if mtpos >= limits[1]:
                mtpos = limits[1] - .1
            mt.start(mtpos)
            self.log.info('Moving %s to %8.4f', mt.name, mtpos)

    def doStart(self, target):
        th, tt = self._calc_angles(to_k(target, self.unit))
        self._attached_twotheta.start(tt)
        self.log.info('Moving %s to %8.4f', self._attached_twotheta.name, tt)
        self._attached_theta.start(th)
        self.log.info('Moving %s to %8.4f', self._attached_theta.name, th)
        self._movefoci(self.focmode, th, self.hfocuspars, self.vfocuspars)
        self._sim_setValue(target)

    def _getWaiters(self):
        return [(name, self._adevs[name]) for name in
                ['theta', 'twotheta', 'focush', 'focusv', 'mt']]

    def doStatus(self, maxage=0):
        # order is important here.
        const, text = multiStatus(self._getWaiters(),
                                  maxage)
        if const == status.OK:  # all idle; check also angle relation
            tt, th = self._get_angles(maxage)
            if abs(tt - 2.0 * th) > self._axisprecision:
                return status.NOTREACHED, 'two theta and 2*theta axis ' \
                                          'mismatch: %s <-> %s = 2 * %s' \
                       % (tt, 2.0 * th, th)
        return const, text
