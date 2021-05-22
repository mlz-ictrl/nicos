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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""Slit devices in AMOR"""
from numpy import arctan, radians, tan

from nicos.core import Attach, HasPrecision, Override, Param, Readable, \
    dictwith, oneof, status
from nicos.core.utils import multiStatus
from nicos.devices.generic.slit import Slit, SlitAxis

from nicos_sinq.amor.devices.logical_motor import AmorLogicalMotor, \
    InterfaceLogicalMotorHandler


class SlitOpening(HasPrecision, SlitAxis):
    """Device to control the slit opening/height.

    Motor dXt changes moves the slit's top slab in turn changing the
    slit opening. Motor dXb changes the position of the whole slit
    moving it up or down (X is the slit number).

    This device reads the current opening using the motor dXt and
    changes the opening using combination of the motors dXt and dXb
    such that the center remains aligned.
    """

    parameter_overrides = {
        'unit': Override(mandatory=False, default='mm'),
        'fmtstr': Override(userparam=False),
        'maxage': Override(userparam=False),
        'pollinterval': Override(userparam=False),
        'warnlimits': Override(userparam=False),
        'precision': Override(userparam=False, default=0.01),
        'target': Override(volatile=True)
    }

    status_to_msg = {
        status.ERROR: 'Error in %s',
        status.BUSY: 'Moving: %s ...',
        status.WARN: 'Warning in %s',
        status.NOTREACHED: '%s did not reach target!',
        status.UNKNOWN: 'Unknown status in %s!',
        status.OK: 'Ready.'
    }

    def doReadTarget(self):
        # Do not allow None as target
        target = self._getFromCache('target', self.doRead)
        return target if target is not None else self.doRead(0)

    def _convertRead(self, positions):
        return positions[3]

    def _convertStart(self, target, current):
        current_opening = current[3]
        current_bottom = current[2]
        new_bottom = current_bottom + 0.5 * (current_opening - target)
        return current[0], current[1], new_bottom, target

    def doStatus(self, maxage=0):
        # Check for error and warning in the dependent devices
        st_devs = multiStatus(self._adevs, maxage)
        devs = [dname for dname, d in self._adevs.items()
                if d.status()[0] == st_devs[0]]

        if st_devs[0] in self.status_to_msg:
            msg = self.status_to_msg[st_devs[0]]
            if '%' in msg:
                msg = msg % ', '.join(devs)
            return st_devs[0], msg

        return st_devs


def read_divergence(xs, slit):
    left, _, bottom, top = slit
    s = arctan(top/xs)
    d = arctan(bottom/xs)
    return s+d, 2*arctan(left/xs), (s-d)/2


def read_beam_shaping(slit):
    left, right, bottom, top = slit
    return top+bottom, right+left, (top-bottom)/2


class AmorSlitHandler(InterfaceLogicalMotorHandler):

    attached_devices = {
        'xs':  Attach('Sample x position', Readable, missingok=True,
                      optional=True),
        'mu': Attach('Sample omega', Readable, missingok=True,
                     optional=True),
        'nu': Attach('Sample omega', Readable, missingok=True,
                     optional=True),
        'ltz': Attach('Sample x position', Readable, missingok=True,
                      optional=True),
        'xd2': Attach('Sample x position', Readable, missingok=True,
                      optional=True),
        'xl': Attach('Deflector x position', Readable, missingok=True,
                     optional=True),
        'mu_offset': Attach('Sample x position', Readable, missingok=True,
                           optional=True),
        'kappa': Attach('Inclination of the beam after the Selene guide',
                        Readable, missingok=True, optional=True),
        'soz_ideal': Attach('Ideal sample omega', Readable, missingok=True,
                      optional=True),
        'xd3': Attach('', Readable, missingok=True, optional=True),
        'slit1': Attach('slit 1', Slit, missingok=True, optional=True),
        'slit2': Attach('slit 2', Slit, missingok=True, optional=True),
        'slit2z': Attach('Z motor for slit 2', Readable, missingok=True,
                         optional=True),
        'slit3': Attach('slit 3', Slit, missingok=True, optional=True),
        'slit3z': Attach('Z motor for slit 3', Readable, missingok=True,
                         optional=True),
        }

    def doPreinit(self, mode):
        self._status_devs = ['slit1', 'slit2', 'slit2z', 'slit3', 'slit3z']
        InterfaceLogicalMotorHandler.doPreinit(self, mode)
        self.valuetype = dictwith(div=float, did=float, dih=float)

    def doRead(self, maxage=0):
        result = {}
        if self._is_active('diaphragm1'):
            v, h, d = read_divergence(self._read_dev('xs'),
                                      self._read_dev('slit1'))
            result.update({'div': v, 'dih': h, 'did': d})
        if self._is_active('diaphragm2'):
            v, h, d = read_beam_shaping(self._read_dev('slit2'))
            result.update({'d2v': v, 'd2h': h, 'd2d': d})
        if self._is_active('diaphragm3'):
            v, h, d = read_beam_shaping(self._read_dev('slit3'))
            result.update({'d3v': v, 'd3h': h, 'd3d': d})
        return result

    def _get_move_list(self, targets):
        positions = []
        if self._is_active('diaphragm1'):
            xs = self._read_dev('xs')
            div = targets.get('div') or self._read_dev('div')
            did = targets.get('did') or self._read_dev('did')
            dih = targets.get('dih') or self._read_dev('dih')
            top = xs * tan(radians(div / 2 + did))
            bottom = xs * tan(radians(div / 2 - did))
            horizontal = xs * tan(radians(dih / 2))
            positions.extend([(self._get_dev('slit1'),
                               (top, bottom, horizontal, horizontal))
                              ])

        if self._is_active('diaphragm2'):
            v = targets.get('d2v')
            d = targets.get('d2d')
            h = targets.get('d2h')
            ltz = self._read_dev('ltz')
            xd2 = self._read_dev('xd2')
            xl = self._read_dev('xl')
            mu_offset = self._read_dev('mu_offset')
            kappa = self._read_dev('kappa')
            if self._is_active('deflector'):
                z = ltz - (xd2 - xl) * tan(radians(self._read_dev('mu') +
                                                   mu_offset))
            else:
                z = xd2 * tan(radians(kappa))
            top = 0.5 * (v + d)
            bottom = 0.5 * (v - d)
            horizontal = 0.5 * h
            positions.extend([(self._get_dev('slit2z'), z),
                              (self._get_dev('slit2'),
                               (top, bottom, horizontal, horizontal))
                              ])

        if self._is_active('diaphragm3'):
            soz_ideal = self._read_dev('soz_ideal')
            xd3 = self._read_dev('xd3')
            nu = self._read_dev('nu')
            xs = self._read_dev('xs')
            kappa = self._read_dev('kappa')
            v = targets.get('d3v')
            d = targets.get('d3d')
            h = targets.get('d3h')
            z = soz_ideal + (xd3 - xs) * tan(radians(nu + kappa))
            top = 0.5 * (v + d)
            bottom = 0.5 * (v - d)
            horizontal = 0.5 * h
            positions.extend([(self._get_dev('slit2z'), z),
                              (self._get_dev('slit2'),
                               (top, bottom, horizontal, horizontal))
                              ])

        return positions


motortypes = ['div', 'dih', 'did', 'd2v', 'd2h', 'd2d', 'd3v', 'd3h', 'd3d']


class AmorSlitLogicalMotor(AmorLogicalMotor):
    """ Class to represent the logical slit motors in AMOR.
    """
    parameters = {
        'motortype': Param('Type of motor %s' % ','.join(motortypes),
                           type=oneof(*motortypes), mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='degree'),
        'target': Override(volatile=True),
        'abslimits': Override(mandatory=False, default=(-3.0, 3.0)),
        'userlimits': Override(mandatory=False, default=(-3.0, 3.0))
    }

    attached_devices = {
        'controller': Attach('Controller for the logical motors',
                             AmorSlitHandler)
    }

    def doRead(self, maxage=0):
        return self._attached_controller.doRead(maxage)
