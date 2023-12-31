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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""Slit devices in AMOR"""
from numpy import arctan, degrees, radians, tan

from nicos import session
from nicos.core import Attach, Device, HasAutoDevices, HasPrecision, \
    Moveable, Override, Param, Readable, dictwith, oneof, status
from nicos.core.utils import multiStatus
from nicos.devices.generic.slit import Slit, SlitAxis as DefaultSlitAxis

from nicos_sinq.amor.devices.logical_motor import AmorLogicalMotor, \
    InterfaceLogicalMotorHandler


class SlitOpening(HasPrecision, DefaultSlitAxis):
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


def read_divergence(distance, slit):
    left, right, bottom, top = slit
    s = arctan(top / distance)
    d = arctan(bottom / distance)
    h = 2 * arctan((left+right) / distance)
    return{
        'div': degrees(s+d),
        'did': degrees((s-d)/2),
        'dih': degrees(h)
    }


def read_beam_shaping(slit, diaphragm_index):
    left, right, bottom, top = slit
    return {
        f'd{diaphragm_index}v': top+bottom,
        f'd{diaphragm_index}d': (top-bottom)/2,
        f'd{diaphragm_index}h': left+right
    }


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
        self.valuetype = dictwith(div=float, did=float, dih=float, d2v=float,
                                  d2d=float, d2h=float, d3v=float, d3d=float,
                                  d3h=float, )

    def doRead(self, maxage=0):
        result = {}
        if self._is_active('diaphragm1'):
            result.update(read_divergence(
                self._read_dev('xs'),
                self._read_dev('slit1')
            ))
        if self._is_active('diaphragm2'):
            result.update(read_beam_shaping(self._read_dev('slit2'), 2))
        if self._is_active('diaphragm3'):
            result.update(read_beam_shaping(self._read_dev('slit3'), 3))
        return result

    def _get_move_list(self, targets):
        positions = []
        if self._is_active('diaphragm1'):
            distance = self._read_dev('xs')
            div = targets.get('div') or session.getDevice('div').read()
            did = targets.get('did') or session.getDevice('did').read()
            dih = targets.get('dih') or session.getDevice('dih').read()

            top = distance * tan(radians(0.5 * div + did))
            bottom = distance * tan(radians(0.5 * div - did))
            horizontal = distance * tan(.5 * radians(dih))
            positions.extend([(self._get_dev('slit1'),
                               (horizontal, horizontal, bottom, top))
                              ])
        if self._is_active('diaphragm2'):
            d2v = targets.get('d2v') or self._read_dev('d2v')
            d2d = targets.get('d2d') or self._read_dev('d2d')
            d2h = targets.get('d2h') or self._read_dev('d2h')
            top = 0.5 * d2v + d2d
            bottom = 0.5 * d2v - d2d
            horizontal = .5 * d2h

            distance = self._read_dev('xd2')
            kappa = self._read_dev('kappa')
            if self._is_active('deflector'):
                ltz = self._read_dev('ltz')
                xl = self._read_dev('xl')
                mu_offset = self._read_dev('mu_offset')
                z = ltz - (distance - xl) * tan(radians(self._read_dev(
                    'mu') + mu_offset))
            else:
                z = distance * tan(radians(kappa))
            positions.extend([(self._get_dev('slit2z'), z),
                              (self._get_dev('slit2'),
                               (top, bottom, horizontal, horizontal))
                              ])

        if self._is_active('diaphragm3'):
            d3v = targets.get('d3v')
            d3d = targets.get('d3d')
            d3h = targets.get('d3h')
            top = 0.5 * d3v + d3d
            bottom = 0.5 * d3v - d3d
            horizontal = .5 * d3h

            soz_ideal = self._read_dev('soz_ideal')
            xd3 = self._read_dev('xd3')
            nu = self._read_dev('nu')
            xs = self._read_dev('xs')
            kappa = self._read_dev('kappa')
            z = soz_ideal + (xd3 - xs) * tan(radians(nu + kappa))

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
        'abslimits': Override(mandatory=False),
        'userlimits': Override(mandatory=False)
    }

    attached_devices = {
        'controller': Attach('Controller for the logical motors',
                             AmorSlitHandler)
    }


class SlitAxis(DefaultSlitAxis):
    """
    The diaphragm consists of 4 blades, much like a standard slit. The use
    case is different though: one is no interested in the width and height
    but in the divergence.
    In addition to the slit, this slit axis attaches a controller that
    converts the position of the 4 blades to different quantities related to
    the beam divergence.
    """
    attached_devices = {
        'controller': Attach('Controller, used to connect slit and distance '
                             'to the axis', Device),
    }


class DivergenceAperture(HasAutoDevices, Device):
    """
    Slit1 is fix mounted behind the instrument shutter and can not be moved as
    a whole. Its center is by definition the origin of the instrument
    coordinate system.
    The corresponding virtual devices are divergences and angles.
    """

    class VerticalDisplacement(SlitAxis):
        """
        Defines the vertical displacement (angular) of the beam incident on the
        sample
        """

        def _convertRead(self, positions):
            distance = self._attached_controller._attached_distance.read()
            s = arctan(positions[3] / distance)
            d = arctan(positions[2] / distance)
            return .5 * degrees(s - d)

        def _convertStart(self, target, current):
            distance = self._attached_controller._attached_distance.read()
            vertical = self._attached_controller.vertical.read()
            top = distance * tan(radians(0.5 * vertical + target))
            bottom = distance * tan(radians(0.5 * vertical - target))
            return [current[0], current[1], bottom, top]

    class VerticalDivergence(SlitAxis):
        """
        Defines the vertical divergence of the beam incident on the sample
        """

        def _convertRead(self, positions):
            distance = self._attached_controller._attached_distance.read()
            s = arctan(positions[3] / distance)
            d = arctan(positions[2] / distance)
            return degrees(s + d)

        def _convertStart(self, target, current):
            distance = self._attached_controller._attached_distance.read()
            divergence = self._attached_controller.displacement.read()
            top = distance * tan(radians(0.5 * target + divergence))
            bottom = distance * tan(radians(0.5 * target - divergence))
            return [current[0], current[1], bottom, top]

    class HorizontalDivergence(SlitAxis):
        """
        Defines the horiziontal divergence of the beam incident on the sample
        """

        def _convertRead(self, positions):
            distance = self._attached_controller._attached_distance.read()
            return degrees(2 * arctan(positions[0] / distance))

        def _convertStart(self, target, current):
            distance = self._attached_controller._attached_distance.read()
            tgt = list(current)
            tgt[:2] = [distance * tan(.5 * radians(target))] * 2
            return tgt

    attached_devices = {
        'slit': Attach('Corresponding slit', Slit),
        'distance': Attach('Sample x position', Moveable),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default='degree'),
    }

    def doInit(self, mode):

        for name, cls in [
            ('displacement', DivergenceAperture.VerticalDisplacement),
            ('vertical', DivergenceAperture.VerticalDivergence),
            ('horizontal', DivergenceAperture.HorizontalDivergence),
        ]:
            self.add_autodevice(name, cls,
                                slit=self._attached_slit,
                                controller=self,
                                visibility=self.autodevice_visibility,
                                unit='deg')
