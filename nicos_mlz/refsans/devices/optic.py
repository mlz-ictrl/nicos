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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""REFSANS neutron guide system class."""

from __future__ import absolute_import, division, print_function

from nicos.core import Moveable, Override, Param, floatrange, oneof
from nicos.core.params import Attach
from nicos.pycompat import number_types, string_types


class Optic(Moveable):
    """REFSANS neutron guide system."""

    hardware_access = False

    parameters = {
        'mode': Param('mode of the beam',
                      type=oneof('debug',
                                 'fc:nok5a',
                                 'fc:nok5b',
                                 'fc:nok6',
                                 'fc:nok7',
                                 'fc:nok8',
                                 'fc:nok9',
                                 'gisans',
                                 'gisans789',
                                 'neutronguide',
                                 'point',
                                 '12mrad789',
                                 'vc:nok5a',
                                 'vc:nok5a_fc:nok5b',
                                 'vc:nok5a_fc:nok6',
                                 'vc:nok5a_fc:nok7',
                                 'vc:nok5a_fc:nok8',
                                 'vc:nok5a_fc:nok9',
                                 '48mrad',
                                 '54mrad',
                                 ),
                      settable=True, userparam=True, category='experiment'),
        # 'polarisation': Param('Polarisation',
        #                       type=oneof('up', 'down', 'standby', 'off'),
        #                       settable=True,
        #                       userparam=True,
        #                       default='off'),
        'setting': Param('Maps positon to attached devices positions for '
                         'bending beam',
                         type=dict, mandatory=True),
        'masks': Param('Maps mask to attached devices positions',
                       type=dict, mandatory=True),
    }

    parameter_overrides = {
        'unit': Override(default='mrad', mandatory=False, volatile=True),
    }

    attached_devices = {
        'b1': Attach('b1', Moveable),
        'b2': Attach('b2', Moveable),
        'b3': Attach('b3', Moveable),
        'bs1': Attach('bs1', Moveable),
        'nok2': Attach('nok2', Moveable),
        'nok3': Attach('nok3', Moveable),
        'nok4': Attach('nok4', Moveable),
        'nok5a': Attach('nok5a', Moveable),
        'nok5b': Attach('nok5b', Moveable),
        'nok6': Attach('nok6', Moveable),
        'nok7': Attach('nok7', Moveable),
        'nok8': Attach('nok8', Moveable),
        'nok9': Attach('nok9', Moveable),
        'sc2': Attach('sc2', Moveable),
        'zb0': Attach('zb0', Moveable),
        'zb1': Attach('zb1', Moveable),
        'zb2': Attach('zb2', Moveable),
        'zb3': Attach('zb3', Moveable),
    }

    def doRead(self, maxage=0):
        self.log.debug('doRead')
        return self.target

    def doIsAllowed(self, target):
        self.log.debug('doIsAllowed')
        if isinstance(target, string_types):
            try:
                oneof('horizontal',
                      '12mrad_b3_12.000',
                      '12mrad_b2_12.254_eng',
                      '12mrad_b2_12.88_big',
                      '12mrad_b3_13.268',
                      '12mrad_b3_789',
                      '48mrad')(target)
                return True, ''
            except ValueError as e:
                return False, str(e)
        elif isinstance(target, number_types):
            try:
                floatrange(0, 48)(target)
                return True, ''
            except ValueError as e:
                return False, str(e)
        return False, 'Wrong value type'

    def doStart(self, target):
        # Calculate positions and move devices
        self.log.debug('Start to: %s', target)
        for ele in self.setting[target].keys():
            line = 'move ' + ele
            if hasattr(self, '_attached_' + ele):
                f = getattr(self, '_attached_' + ele)
                if self.setting[target][ele] == 'debug':
                    line += ' debug'
                else:
                    f.move(self.setting[target][ele])
                    line += ' %s' % self.setting[target][ele]
                self.log.debug(line)
            else:
                line += ' not attached'
                self.log.warning(line)

    def doWriteMode(self, target):
        # Calculate positions and move devices
        self.log.debug('WriteMode to: %s', target)
        for ele in self.masks[target].keys():
            line = 'mode ' + ele
            if hasattr(self, '_attached_' + ele):
                f = getattr(self, '_attached_' + ele)
                if self.masks[target][ele] == 'debug':
                    line += ' debug'
                else:
                    f.mode = self.masks[target][ele]
                    line += ' %s' % self.masks[target][ele]
                self.log.debug(line)
            else:
                line += ' not attached'
                self.log.warning(line)

    def doReadUnit(self):
        return '' if isinstance(self.target, string_types) else 'mrad'
