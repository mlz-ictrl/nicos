#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Michael Hart <michael.hart@stfc.ac.uk>
#
# *****************************************************************************

from nicos.core import Readable, Param, Override, Attach, dictof, anytype


class MantidDevice(Readable):
    parameters = {
        'args': Param('Additional arguments to MoveInstrumentComponent.',
                      type=dictof(str, anytype)),
        'algorithm': Param('Mantid algorithm name.',
                           type=str, settable=False, userparam=False,
                           mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False)
    }

    valuetype = dictof(str, anytype)


class MantidTranslationDevice(MantidDevice):
    attached_devices = {
        'x': Attach('Device that determines x-translation of component.',
                    Readable, optional=True),
        'y': Attach('Device that determines y-translation of component.',
                    Readable, optional=True),
        'z': Attach('Device that determines z-translation of component.',
                    Readable, optional=True),
    }

    parameter_overrides = {
        'algorithm': Override(default='MoveInstrumentComponent',
                              mandatory=False)
    }

    def doRead(self, maxage=0):
        device_args = {}

        if self._attached_x:
            device_args['X'] = self._attached_x.read(maxage)

        if self._attached_y:
            device_args['Y'] = self._attached_y.read(maxage)

        if self._attached_z:
            device_args['Z'] = self._attached_z.read(maxage)

        device_args.update(self.args)

        return device_args


class MantidRotationDevice(MantidDevice):
    attached_devices = {
        'angle': Attach('Device that describes rotation angle of component.',
                        Readable, optional=False),

    }

    parameters = {
        'x': Param('X component of rotation vector', type=float, default=0.0),
        'y': Param('Y component of rotation vector', type=float, default=0.0),
        'z': Param('Z component of rotation vector', type=float, default=0.0),
    }

    parameter_overrides = {
        'algorithm': Override(default='RotateInstrumentComponent',
                              mandatory=False)
    }

    def doRead(self, maxage=0):
        device_args = {}

        device_args['X'] = self.x
        device_args['Y'] = self.y
        device_args['Z'] = self.z

        if self._attached_angle:
            device_args['Angle'] = self._attached_angle.read(maxage)

        device_args.update(self.args)

        return device_args
