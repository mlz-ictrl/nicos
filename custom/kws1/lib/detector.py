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

"""Detector switcher for KWS."""

from nicos.core import Param, Override, oneof, dictof, dictwith, MASTER, \
    ConfigurationError, DeviceMixinBase
from nicos.devices.generic.switcher import MultiSwitcher
from nicos.pycompat import iteritems


class oneof_detector(oneof):
    def __call__(self, val=None):
        try:
            return oneof.__call__(self, val)
        except ValueError:
            raise ValueError('preset %r does not exist for the current '
                             'selector setting' % val)


class DetectorPosSwitcherMixin(DeviceMixinBase):

    parameters = {
        'offsets':  Param('Offsets to correct TOF chopper-detector length '
                          'for the errors in the det_z axis value',
                          type=dictof(float, float),
                          mandatory=True),
        'mapkey':   Param('Last selector position for mapping',
                          type=str, settable=True, userparam=False),
    }


class DetectorPosSwitcher(DetectorPosSwitcherMixin, MultiSwitcher):
    """Switcher for the detector position.

    This controls the X, Y and Z components of the detector position.  Presets
    depend on the target wavelength given by the selector.
    """

    parameters = {
        'presets':  Param('Presets that determine the mappings',
                          type=dictof(str, dictof(str, dictwith(
                              x=float, y=float, z=float))),
                          mandatory=True),
    }

    parameter_overrides = {
        'mapping':  Override(mandatory=False, settable=True, userparam=False),
    }

    def doInit(self, mode):
        # check that an offset is defined for each z distance
        for _selpos, selpresets in iteritems(self.presets):
            for _pname, preset in iteritems(selpresets):
                if preset['z'] not in self.offsets:
                    raise ConfigurationError(
                        self, 'no detector offset found in configuration '
                        'for detector distance of %.2f m' % preset['z'])
        MultiSwitcher.doInit(self, mode)
        # apply mapping of last selector pos in case it changed
        if mode == MASTER:
            self._updateMapping(self.mapkey)

    def _updateMapping(self, selpos):
        self.log.debug('updating the detector mapping for selector '
                       'setting %s', selpos)
        try:
            pos = self.presets.get(selpos, {})
            new_mapping = dict((k, [v['z'], v['x'], v['y']])
                               for (k, v) in pos.items())
            self.mapping = new_mapping
            self.mapkey = selpos
            self.valuetype = oneof_detector(*new_mapping)
            if self._cache:
                self._cache.invalidate(self, 'value')
                self._cache.invalidate(self, 'status')
        except Exception:
            self.log.warning('could not update detector mapping', exc=1)
