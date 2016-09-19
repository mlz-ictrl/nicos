#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Class for KWS chopper control."""

from nicos.core import Moveable, Attach, Param, Override, status, tupleof, \
    listof, oneof, intrange, floatrange, PositionError, MASTER, HasPrecision
from nicos.devices.tango import WindowTimeoutAO
from nicos.utils import clamp
from nicos.kws1.daq import KWSDetector
from nicos.kws1.selector import SelectorSwitcher
from nicos.kws1.detector import DetectorPosSwitcher

# neutron speed at 1A, in m/ms
SPEED = 3.956


class ChopperFrequency(WindowTimeoutAO):
    """Chopper frequency setting with timing."""

    def doTime(self, old, new):
        if old is None or new is None:
            return 0.
        if old == new:
            return 20.                   # phase adjustment
        total = 30.                      # phase adjustment
        total += abs(old - new) / 0.25   # frequency speedup
        total += 60. if new == 0 else 0  # complete stop adds ~1min
        return total


class ChopperParams(Moveable):
    """Setting chopper parameters in terms of (frequency, opening angle)."""

    valuetype = tupleof(floatrange(0, 100), floatrange(0, 90))

    hardware_access = False

    attached_devices = {
        'freq1':  Attach('The frequency of the first chopper', HasPrecision),
        'freq2':  Attach('The frequency of the second chopper', HasPrecision),
        'phase1': Attach('The phase of the first chopper', HasPrecision),
        'phase2': Attach('The phase of the second chopper', HasPrecision),
    }

    parameter_overrides = {
        'fmtstr': Override(default='(%.1f, %.1f)'),
        'unit':   Override(mandatory=False, default=''),
    }

    def doIsAllowed(self, pos):
        freq = pos[0]
        # forbidden ranges 0-5 and 25-32 Hz (0 must be allowed and means OFF)
        if 0 < freq <= 5 or 25 <= freq <= 32:
            return False, 'moving to "forbidden" frequency ranges ' \
                '0-5 Hz and 25-32 Hz is not allowed'
        return True, ''

    def doStart(self, pos):
        if pos[0] == 0:
            if self._attached_freq1.read(0) == 0:
                return
            for dev in (self._attached_phase1, self._attached_phase2,
                        self._attached_freq1, self._attached_freq2):
                dev.start(0)
            return
        (freq, opening) = pos
        self._attached_freq1.start(freq)
        self._attached_freq2.start(freq)
        # calculate phases of the two choppers (they should be around 180deg)
        p0 = 90.0 - opening  # p0: phase difference for given opening angle
        p1 = 180.0 - p0/2.0
        p2 = 180.0 + p0/2.0
        self._attached_phase1.start(p1)
        self._attached_phase2.start(p2)

    # doStatus provided by adevs is enough

    def doRead(self, maxage=0):
        freq = self._attached_freq1.read(maxage)
        p1 = self._attached_phase1.read(maxage)
        p2 = self._attached_phase2.read(maxage)
        if freq == p1 == p2 == 0:
            return (0.0, 0.0)
        opening = 90.0 - (p2 - p1)
        return (freq, opening)

    def doIsAtTarget(self, pos):
        # take precision into account
        tfreq, topen = self.target
        rfreq, ropen = pos
        return abs(tfreq - rfreq) < self._attached_freq1.precision and \
            abs(topen - ropen) < self._attached_phase1.precision


def calculate(lam, spread, reso, shade, l, dtau, n_max):
    """Calculate chopper frequency and opening angle for a single setting,
    which needs:

    * lam: incoming neutron wavelength in Angstrom
    * spread: incoming neutron wavelength spread from selector
    * reso: desired wavelength resolution
    * shade: shade of spectrum edges
    * l: chopper-detector length in m
    * dtau: additional offset of TOF in ms
    * n_max: maximum number of acquisition frames

    Returns: (frequency in Hz, opening angle in deg)
    """

    dlam = 2.0 * spread * lam
    tau_tot = l * lam * (1.0 - spread) / SPEED

    n = max(2, int(2 * spread / reso + 1))
    n_fac = (1. - 2 * shade) / (1. - shade)
    n_fac = clamp(n_fac, 1.0 / n, 1.0)
    n_illum = clamp(int(n_fac * n), 1, n_max)

    tau_delta = l * dlam / ((n - 1) * SPEED)
    tau_win = 0.5 * tau_delta * (n + n_illum)
    tau0 = tau_tot + 0.5 * (n - n_illum) * tau_delta + dtau
    tau0 -= tau_win * int(tau0 / tau_win)

    freq = 1000.0 / tau_win / 2.0
    angle = 180.0 / (0.5 * (n + n_illum))

    return freq, angle


class Chopper(Moveable):
    """Switcher for the TOF setting.

    This controls the chopper phase and opening angle, as well as the TOF slice
    settings for the detector.  Presets depend on the target wavelength as well
    as the detector position.
    """

    hardware_access = False

    attached_devices = {
        'selector':    Attach('Selector preset switcher', SelectorSwitcher),
        'det_pos':     Attach('Detector preset switcher', DetectorPosSwitcher),
        'daq':         Attach('KWSDetector device', KWSDetector),
        'params':      Attach('Chopper param device', Moveable),
    }

    parameters = {
        'resolutions': Param('Possible values for the resolution', unit='%',
                             type=listof(float), mandatory=True),
        'channels':    Param('Desired number of TOF channels',
                             # TODO: max channels?
                             type=intrange(1, 1024), default=64,
                             settable=True),
        'shade':       Param('Desired overlap of spectrum edges',
                             type=floatrange(0.0, 1.0), default=0.0,
                             settable=True, category='general'),
        'tauoffset':   Param('Additional offset for time of flight',
                             type=floatrange(0.0), default=0.0, settable=True,
                             category='general'),
        'nmax':        Param('Maximum number of acquisition frames',
                             type=intrange(1, 128), default=25, settable=True),
        'calcresult':  Param('Last calculated setting',
                             type=tupleof(float, float, int), settable=True,
                             userparam=False),
    }

    parameter_overrides = {
        'unit':        Override(default='', mandatory=False),
    }

    def doInit(self, mode):
        self.valuetype = oneof('off', 'manual',
                               *('%.1f%%' % v for v in self.resolutions))

    def _getWaiters(self):
        return [self._attached_params]

    def doUpdateChannels(self, value):
        # invalidate last calculated result when changing these parameters
        if self._mode == MASTER and 'channels' in self._params:
            self.calcresult = (0, 0, 0)

    def doUpdateShade(self, value):
        if self._mode == MASTER and 'shade' in self._params:
            self.calcresult = (0, 0, 0)

    def doUpdateTauoffset(self, value):
        if self._mode == MASTER and 'tauoffset' in self._params:
            self.calcresult = (0, 0, 0)

    def doUpdateNmax(self, value):
        if self._mode == MASTER and 'nmax' in self._params:
            self.calcresult = (0, 0, 0)

    def doStart(self, value):
        if value == 'off':
            if self._attached_daq.mode == 'tof':  # don't touch realtime
                self._attached_daq.mode = 'standard'
            self._attached_params.start((0, 0))
            return
        elif value == 'manual':
            if self._attached_daq.mode == 'standard':
                self._attached_daq.mode = 'tof'
            return
        reso = float(value.strip('%')) / 100.0

        sel_target = self._attached_selector.target
        det_target = self._attached_det_pos.target
        try:
            lam = self._attached_selector.presets[sel_target]['lam']
            spread = self._attached_selector.presets[sel_target]['spread']
            det_z = self._attached_det_pos.presets[sel_target][det_target]['z']
            det_offset = self._attached_det_pos.offsets[det_z]
        except KeyError:
            raise PositionError(self, 'cannot calculate chopper settings: '
                                'selector or detector device not at preset')

        self.log.debug('chopper calc inputs: reso=%f, lam=%f, spread=%f, '
                       'det_z=%f' % (reso, lam, spread, det_z))
        freq, opening = calculate(lam, spread, reso, self.shade,
                                  20.0 + det_z + det_offset,
                                  self.tauoffset, self.nmax)
        self.log.debug('calculated chopper settings: freq=%f, opening=%f' %
                       (freq, opening))
        interval = int(1000000.0 / (freq * self.channels))
        self.calcresult = freq, opening, interval

        self._attached_params.start((freq, opening))

        self._attached_daq.mode = 'tof'
        self._attached_daq.tofchannels = self.channels
        self._attached_daq.tofinterval = interval
        self._attached_daq.tofprogression = 1.0  # linear channel widths

    def doRead(self, maxage=0):
        if self.target == 'manual':
            return 'manual'
        params = self._attached_params.read(maxage)
        if params[0] < 1.0:
            return 'off'
        # TODO: take from isAtTarget
        if abs(params[0] - self.calcresult[0]) < self._attached_params._attached_freq1.precision and \
           abs(params[1] - self.calcresult[1]) < self._attached_params._attached_phase1.precision:
            if self._attached_daq.mode == 'tof' and \
               self._attached_daq.tofchannels == self.channels and \
               self._attached_daq.tofinterval == self.calcresult[2] and \
               self._attached_daq.tofprogression == 1.0:
                return self.target
        return 'unknown'

    def doStatus(self, maxage=0):
        move_status = self._attached_params.status(maxage)
        if move_status[0] not in (status.OK, status.WARN):
            return move_status
        r = self.read(maxage)
        if r == 'unknown':
            return (status.NOTREACHED, 'unconfigured chopper frequency/phase '
                    'or still moving')
        return status.OK, ''
