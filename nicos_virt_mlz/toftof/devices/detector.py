# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""VTOFTOF detector image based on McSTAS simulation."""

import numpy as np

from nicos.core import Attach, Override, Param, intrange, listof, oneof, \
    tupleof
from nicos.core.constants import FINAL, LIVE, MASTER
from nicos.devices.generic.slit import Slit
from nicos.devices.mcstas import MIN_RUNTIME, DetectorMixin, \
    McStasCounter as BaseCounter, McStasImage, \
    McStasSimulation as BaseSimulation

from nicos_mlz.toftof.devices import Detector as BaseDetector, Ratio, \
    SlitType, Speed, Wavelength
from nicos_mlz.toftof.lib import calculations as calc
from nicos_virt_mlz.toftof.devices.sample import Sample


class McStasSimulation(BaseSimulation):
    """McSimulation processing.

    See ../../README for the location of the McStas code
    """

    parameter_overrides = {
        'mcstasprog': Override(default='toftof'),
    }

    parameters = {
        'repeat_factor': Param('Factor to calculate the number of "repeat" '
                               'parameter, which determines the number of '
                               'neutrons (used in case of not give parameter '
                               '"repeat_curve")',
                               type=float, default=4/3,
                               ),
        'repeat_curve': Param('Repeat alignment curve to calculate the McStas '
                              '"repeat" factor. Given as list of '
                              '(repeat, runtime) tuples.',
                              type=listof(tupleof(float, float)),
                              ),
    }

    attached_devices = {
        'sample': Attach('Sample', Sample),
        'wavelength': Attach('Wave length device', Wavelength),
        'speed': Attach('Chopper rotation speed device', Speed),
        'ratio': Attach('Chopper disc ratio device', Ratio),
        'st': Attach('Chopper slit type', SlitType),
        'slit': Attach('Sample slit', Slit),
    }

    # lambda:      [AA]     observation wavelength
    # speed:       [rpm]    chopper speed (60 * frequency)
    # ratio:       [1]      every [1] puls will pass the 5 frame overlap
    #                       chopper (FO)
    # chST:        [1]      0 for wide chopper slits,
    #                       1 for small chopper slits,
    #                       2 for wide slits on chopper 1 and 6 and small slits
    #                       for chopper 2 and 7
    # focused_beam [1]      Use 0 for linear guide and 1 for focusing guides
    # Ah, Aw:      [m]      Height and width of focussing guide at the exit
    # slits_hor    [mm]     Horizontal slit width
    # slits_vert   [mm]     Vertical slit width
    # sample       [1]      0 = Vanadium, 1 = empty cell, 2 = water
    # scat_order   [1]      Limit multiple scattering up to given order
    #                       0 = all, 1 = single, 2 = double, ...
    # repeat       [1]      repetition of the neutrons from the virtual source
    # split_var    [1]      repetition of the neutrons arriving in front of the
    #                       sample


    def doInit(self, mode):
        BaseSimulation.doInit(self, mode)
        self._x = []
        self._y = []
        for (x, y) in self.repeat_curve:
            self._x.append(x)
            self._y.append(y)

    def _prepare_params(self):
        if self.repeat_curve:
            repeat_factor = np.interp(self.preselection, self._y, self._x)
        else:
            repeat_factor = self.repeat_factor * self.preselection
        if round(repeat_factor) < repeat_factor:
            repeat_factor += 1
        return [
            'lambda=%s' % self._dev_value(self._attached_wavelength),  # 6
            'speed=%s' % self._dev_value(self._attached_speed),  # 14000
            # chopper definitions
            'ratio=%s' % self._dev_value(self._attached_ratio),  # 2
            'chST=%s' % self._dev_value(self._attached_st),  # 0
            'focused_beam=%d' % 0,  # focussed beam
            # slits in mm
            'slits_hor=%s' % self._dev_value(self._attached_slit.width),
            'slits_vert=%s' % self._dev_value(self._attached_slit.height),
            # 0 = Vanadium, 1 = empty cell, 2 = water
            'sample=%d' % self._attached_sample.sampletype,
            'scat_order=%d' % 0,
            'repeat=%d' % round(repeat_factor),
            'split_var=%d' % 1000,
        ]


class Image(McStasImage):

    parameters = {
        'timechannels': Param('Number of time channels',
                              type=intrange(1, 4096), settable=True,
                              default=1024, category='general'),
        'timeinterval': Param('Time for each time channel',
                              type=float, settable=True, unit='s',
                              mandatory=False, default=252*5e-8,
                              category='general'),
        'frametime': Param('Time interval between pulses',
                           type=float, settable=True, volatile=True,
                           default=0.0128571, unit='s',
                           category='general',
                           ),
        'delay': Param('TOF frame delay',
                       type=float, settable=True,
                       default=162093*5e-8, fmtstr='%g', unit='s',
                       category='general',
                       ),
        'neutron_section': Param("Section to take 'neutrons' from PSD file",
                                 type=oneof('Data', 'Events'), mandatory=False,
                                 default='Events'),
        'monitorchannel': Param('Channel number of the monitor counter',
                                type=intrange(1, 1024), settable=False,
                                default=956,
                                ),
    }

    def _readpsd(self, quality):
        if self._attached_mcstas._signal_sent or quality == FINAL:
            try:
                blocks = 1 if self.neutron_section == 'Events' else 3
                with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                    lines = f.readlines()[-blocks * (self.size[1] + 1):]
                if lines[0].startswith(f'# {self.neutron_section}') and \
                   self.mcstasfile in lines[0]:
                    factor = 1 if blocks == 1 else self._attached_mcstas._getScaleFactor()
                    buf = factor * np.loadtxt(lines[1:self.size[1] + 1],
                                              dtype=np.float32)
                    self._buf = np.transpose(buf.astype(self.image_data_type))
                elif quality != LIVE:
                    raise OSError('Did not find start line: %s' % lines[0])
            except OSError:
                if self._attached_mcstas._getTime() > MIN_RUNTIME:
                    self.log.warning('could not read result file', exc=1)
                elif quality != LIVE:
                    self.log.exception('Could not read result file', exc=1)
        else:
            self._buf = np.transpose(
                np.zeros(self.size).astype(self.image_data_type))
        self.readresult = [sum(d[:self.monitorchannel].sum() +
                               d[self.monitorchannel + 1:].sum()
                               for d in self._buf)]

    def doReadFrametime(self):
        return self.timeinterval * self.timechannels

    def doWriteFrametime(self, value):
        # as the HW can only realize selected values for timeinterval, probe
        # until success
        wanted_timeinterval = int(
            (value / self.timechannels) / calc.ttr) * calc.ttr
        self.timeinterval = wanted_timeinterval
        # note: if a doReadTimeinterval differs in value from a previous
        #       doWriteTimeinterval,
        #       HW does actually use the returned value, not the wanted.
        #       (in this case: returned < set) so, increase the wanted value
        #       until the used one is big enough
        actual_timeinterval = self.timeinterval
        while actual_timeinterval * self.timechannels < value:
            wanted_timeinterval += calc.ttr
            self.timeinterval = wanted_timeinterval
            actual_timeinterval = self.timeinterval


class McStasCounter(BaseCounter):

    def doRead(self, maxage=0):
        if self._mode == MASTER:
            try:
                with self._attached_mcstas._getDatafile(self.mcstasfile) as f:
                    line = list(f)[-1]
                    self.curvalue = float(line.split()[2])
            except Exception:
                if self._attached_mcstas._getTime() > MIN_RUNTIME:
                    self.log.warning('could not read result file', exc=1)
                self.curvalue = 0
        return self.curvalue


class Detector(DetectorMixin, BaseDetector):
    """Detector subclass for McStas simulations that don't require a custom
    Detector class.
    """
