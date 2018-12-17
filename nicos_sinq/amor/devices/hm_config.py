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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from math import floor, log

from nicos import session
from nicos.core import Attach, Override
from nicos.core.errors import NicosError
from nicos.pycompat import number_types

from nicos_sinq.devices.epics.astrium_chopper import EpicsAstriumChopper
from nicos_sinq.devices.sinqhm.configurator import ConfiguratorBase, \
    HistogramConfTofArray


class AmorTofArray(HistogramConfTofArray):
    """ Special TOF Array for AMOR. The time bins can be changed using one
    of the schemes.
    Time binning schemes:

        c/q/t <argument>
        c means Delta q / q = constant = <argument>
        q means Delta q = constant, <argument> is the number of bins/channels
        qq assumes two spectra per pulse
        t means Delta t = constant, <argument> is the number of bins/channels
    """
    attached_devices = {
        'chopper': Attach('The chopper device', EpicsAstriumChopper)
    }

    parameter_overrides = {
        'dim': Override(mandatory=False)
    }

    schemes = {
        'c': float,
        'q': int,
        't': int,
        'qq': int,
    }

    # Constants
    mdh = 2.5277828e6

    def doInit(self, mode):
        if not self.data:
            self.log.warning('TOF binning data missing. Please update it!')

    def dataText(self):
        # Due to limited size of the configuration memory we write
        # diff instead of actual values
        if not self.data:
            self.log.warning('Data for the array missing.')
            return ''

        arraytxt = '\n'
        newlinecount = 0
        d0 = self.data[0]
        for d in self.data:
            arraytxt += self.formatter % (d - d0)  # Write the diff only
            newlinecount += 1
            if newlinecount % 5 == 0:
                newlinecount = 0
                arraytxt += '\n'
        return arraytxt

    def applyBinScheme(self, scheme, value=None):
        if scheme not in self.schemes:
            self.log.error('%s is not an identified scheme. Please use one '
                           'from the list below', scheme)
            self.log.error('%s', self.schemes.keys())
            return

        typ = self.schemes.get(scheme)
        if typ:
            try:
                value = typ(value)
            except TypeError:
                self.log.error('Provided value for scheme %s should be %s',
                               scheme, typ)

        # Get the chopper speed, phase
        chspeed = 0
        for ch in self._attached_chopper._attached_choppers:
            if ch.isMaster:
                chspeed = ch.speed

        if chspeed == 0:
            self.log.error('Chopper is not running. Time binning should not'
                           'be changed.')
            return

        # Get the chopper-detector distance
        distances = session.getDevice('Distances')
        if not isinstance(distances.chopper, number_types) or \
                not isinstance(distances.detector, number_types):
            raise NicosError('Chopper and detector distance unknown')
        dist = abs(distances.chopper - distances.detector)

        # Get Lambda range
        lmin, lmax = self._getLambdaRange()

        # Calculate t range
        tmin, tmax = (l * dist * self.mdh * 1e-6 for l in (lmin, lmax))

        # Calculate tau
        tau = int(30e7 / chspeed)
        # check if tau, lambda_max and CDD are compatible
        if tau < lmax * dist / 4e6:
            self.log.warning('Chopper-Detector distance is too large for '
                             'chopper frequency')

        # offset between chopper-pulse and time-zero for data acquisition
        toffset = self._attached_chopper.indexphase * 1e7 / (6 * chspeed)
        threshold = toffset + tmax

        # Give user some information
        self.log.info('Chopper Detector distance: %s', dist)
        self.log.info('Using: %s < lambda < %s', lmin, lmax)
        self.log.info('Corresponds to %s < time < %s', tmin, tmax)
        self.log.info('Calculated time offset: %s', toffset)
        self.log.info('Calculated tau: %s', tau)

        # Apply correct scheme
        if not hasattr(self, '_timebin_scheme_' + scheme):
            raise NotImplementedError('This scheme is not yet implemented.')

        # For q scheme tau should be set to 0
        if scheme == 'q':
            tau = 0

        schemefunc = getattr(self, '_timebin_scheme_' + scheme)
        tofarray = schemefunc(tmin, tmax, toffset, tau, value)

        # The last boundary term
        tofarray.append(tofarray[-1] + tofarray[1] - tofarray[0])

        self.setData([len(tofarray)], tofarray)
        self.offset = int(tau)
        self.threshold = int(threshold)
        self.log.info('Created using %s time bins', len(self.data))

    def _getLambdaRange(self):
        if 'selene' in session.loaded_setups:
            return 4.0, 13.0
        else:
            return 3.5, 12.0

    def _timebin_scheme_c(self, tmin, tmax, toffset, tau, resolution):
        self.log.info('Using resolution Dq/q = const = %s', resolution)
        bins = []
        end = floor(log(tmax / tmin) / log(1 + resolution))
        tme = tmin
        bn = 0
        while bn <= end:
            tim = int(tme + 0.5)
            bins.append(int(tim + toffset))
            tme = tme * (1 + resolution)
            bn += 1
        return bins

    def _timebin_scheme_q(self, tmin, tmax, toffset, tau, channels):
        self.log.info('Using %s channels, equidistant in q', channels)
        bins = []
        delta = (1 / tmin - 1 / tmax) / channels
        bn = 0
        while bn <= channels:
            tme = 1 / (1 / tmin - bn * delta)
            tim = tau + int(tme + 0.5)
            bins.append(int(tim + toffset))
            bn += 1
        return bins

    def _timebin_scheme_qq(self, tmin, tmax, toffset, tau, channels):
        self.log.info('*** assuming 2 spectra per pulse ***')
        # First pulse
        self.log.info('Creating first pulse..')
        first = self._timebin_scheme_q(tmin, tmax, toffset,
                                       0, channels)
        # Second pulse
        self.log.info('Creating second pulse..')
        second = self._timebin_scheme_q(tmin, tmax, toffset,
                                        tau, channels)
        return first + second

    def _timebin_scheme_t(self, tmin, tmax, toffset, tau, channels):
        self.log.info('Using %s channels, equidistant in t', channels)
        bins = []
        delta = (tmax - tmin) / channels
        bn = 0
        while bn <= channels:
            tme = tmin + bn * delta
            tim = int(tme + 0.5)
            bins.append(int(tim + toffset))
            bn += 1
        return bins


class AmorHMConfigurator(ConfiguratorBase):
    """The configurator for AMOR is a special case as it writes
    different mask depending on if the chopper is spinning or not.
    """
    attached_devices = {
        'chopper': Attach('The chopper device', EpicsAstriumChopper)
    }

    def _isChopperActive(self):
        return self._attached_chopper._master.speed > 0

    def doReadMask(self):
        return "0x00f00000" if self._isChopperActive() else "0x00000000"

    def doReadActive(self):
        return "0x00600000" if self._isChopperActive() else "0x00000000"
