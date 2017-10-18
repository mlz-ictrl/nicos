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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from bisect import bisect_left
from math import pi, sqrt
from collections import OrderedDict

import numpy

from nicos.core import Readable, Moveable, Attach, Param, tupleof
from nicos.pycompat import xrange, iteritems  # pylint: disable=W0622
from nicos.devices.generic.sequence import BaseSequencer, SeqDev, SeqMethod


class CBoxResonanceFrequency(BaseSequencer):
    """Class to control the RESEDA capacity box, used to adjust the resonant
    circuits.

    You can trigger an auto adjustment by setting a desired resonance frequency.
    This device will calculate the necessary capacity
    ((1/(2*pi*frequency)) ** 2 / coil_inductivity) and determine the best setup
    for that capacity. It will also try some setups with lower and higher
    capacities, determining the adjustment quality
    (defined by (fwdp - revp) / (fwdp + revp)), and chooses the setup with the
    maximum quality as its new setup.
    It will also tune the input (highpass/tranformator/diplexer) for the given
    frequency and set the frequency to the function generator.

    The read value of this device will be the calculated resonance frequency,
    defined by the current capacitor setup.
    """

    # Bank capacities in F
    BANK_CAPACITIES = [
        [2e-08, 4.4e-08, 9.4e-08, 2e-07, 4.4e-07, 9.4e-07],  # C1
        [4.4e-10, 9.4e-10, 2e-09, 4.4e-09, 9.4e-09],  # C2
        [4.4e-11, 6.6e-11, 9.4e-11, 2e-10]  # C3
    ]

    HIGHPASS_POLYNOM = [0.000000100879350, -0.000137497565329,
                        0.059798285349245, 2.519127111192503]
    HIGHPASS_CAPACITIES = [22e-9, 10e-9, 4.7e-9, 2.2e-9, 1e-9, 470e-12, 220e-12]

    attached_devices = {
        'power_divider': Attach('Power divider to split the power to both '
                                'coils', Moveable),
        'highpass': Attach('Highpass filter to smooth the signal', Moveable),
        'diplexer': Attach('Lowpass filter to smooth the signal (enable for '
                           'low frequency, disable for high frequency)',
                           Moveable),
        'coil1_c1': Attach('Coil 1: Capacitor bank 1', Moveable),
        'coil1_c2': Attach('Coil 1: Capacitor bank 2', Moveable),
        'coil1_c3': Attach('Coil 1: Capacitor bank 3', Moveable),
        'coil1_c1c2serial': Attach('Coil 1: Use c1 and c2 in serial instead of'
                                   'parallel', Moveable),
        'coil1_transformer': Attach('Coil 1: Used to manipulate the coil '
                                    'resistance to match the power amplifier '
                                    'resistance', Moveable),
        'coil2_c1': Attach('Coil 2: Capacitor bank 1', Moveable),
        'coil2_c2': Attach('Coil 2: Capacitor bank 2', Moveable),
        'coil2_c3': Attach('Coil 2: Capacitor bank 3', Moveable),
        'coil2_c1c2serial': Attach('Coil 2: Use c1 and c2 in serial instead of '
                                   'parallel', Moveable),
        'coil2_transformer': Attach('Coil 2: Used to manipulate the coil '
                                    'resistance to match the power amplifier '
                                    'resistance', Moveable),
        'pa_fwdp': Attach('Device to measure the forward power for adjustment '
                          'quality', Readable),
        'pa_revp': Attach('Device to measure the reverse power for adjustment '
                          'quality', Readable),
        'fg': Attach('Frequency generator', Moveable),
    }

    parameters = {
        # usage parameters #
        'use_second_coil': Param('Use 2 coils instead of one', type=bool,
                                 volatile=True, settable=True),
        # adjustment parameters #
        'cable_capacity': Param('Cumulated cable capacity', type=float,
                                unit='F', default=50e-12),
        'serial_output_capacity_c2': Param('Serial capacity of capacitor bank '
                                           '2', type=float, unit='F',
                                           default=20e-12),
        'serial_output_capacity_c1_c2': Param('Cumulated serial capacity of '
                                              'capacitor bank 1 and bank 2',
                                              type=float, unit='F',
                                              default=20e-12,),
        'cbox2_input_capacity': Param('Input capacity for cbox2 (coil box)',
                                      type=float, unit='F', default=8e-12),
        'cbox2_output_capacity': Param('Output capacity for cbox2 (coil box)',
                                       type=float, unit='F', default=9e-12),
        'coil_inductivity': Param('Inductivity of coil 1', unit='H',
                                   type=float, default=28.76e-6),
        'coil_self_capacitance': Param('Self-capacitance of coil 1', unit='F',
                                        type=float, default=5e-12),
        'tuning_step': Param('Frequency range to tune for', type=float,
                             default=1e3),
        'tuning_steps': Param('Number of steps to tune around the necessary '
                              'capacity (+/-)', type=int, default=10),
        'tuning_points': Param('Number of points to average over for 1 '
                               'adjustment step', type=int, default=5),
        'diplexer_threshold_frequency': Param('Threshold frequency for '
                                              'diplexer usage. The diplexer '
                                              'is used if the frequency is '
                                              'higher then the threshold',
                                              type=float, default=1e6),
        'transformer_threshold_frequencies': Param('Threshold frequencies for '
                                              'transformer usage.',
                                              type=tupleof(float, float),
                                                   default=(0.4e6, 2e6)),
    }


    def doInit(self, mode):
        self._capacities = self._calculatePossibleCapacities()

    def doRead(self, maxage=0):
        return self._getResonanceFrequency(1)

    def doWriteUse_Second_Coil(self, value):
        self._adevs['power_divider'].maw(value)

    def doReadUse_Second_Coil(self):
        return self._adevs['power_divider'].read()

    def _generateSequence(self, target):
        return [
            SeqDev(self._adevs['fg'], target),
            SeqMethod(self, '_tuneInput', target),
            SeqMethod(self, '_tuneCapacity', target),
        ]

    def _applyCapacity(self, capacity):
        setup = self._capacities[capacity]

        self.log.debug('Used setup to achieve capacity %g: c1: %d, c2: %d, c3: '
                       '%d, c1c2serial: %d', capacity, *setup)

        self._adevs['coil1_c1'].maw(setup[0])
        self._adevs['coil1_c2'].maw(setup[1])
        self._adevs['coil1_c3'].maw(setup[2])
        self._adevs['coil1_c1c2serial'].maw(setup[3])

        if self.use_second_coil:
            self._adevs['coil2_c1'].maw(setup[0])
            self._adevs['coil2_c2'].maw(setup[1])
            self._adevs['coil2_c3'].maw(setup[2])
            self._adevs['coil2_c1c2serial'].maw(setup[3])

    def _tuneCapacity(self, frequency):
        necessary_cap = self._calcNecessaryCapacity(frequency)

        caps = list(self._capacities)
        index = bisect_left(caps, necessary_cap)
        caps = caps[max(index - self.tuning_steps, 0):index + self.tuning_steps]

        result = {}
        for entry in caps:
            self._applyCapacity(entry)
            #self._getResonanceFrequency(1)  # logging
            quality = self._getCurrentAdjustmentQuality()
            self.log.debug('Adjustment quality for %g F: %g', entry, quality)
            result[quality] = entry

        best = max(result)

        self.log.debug('Best capacity to achieve resonance '
                       'frequency %g: %g', frequency, result[best])

        self._applyCapacity(result[best])

    def _tuneInput(self, frequency):
        diplexer = self._determineDiplexer(frequency)
        transformator = self._determineTransformer(frequency)
        highpass = self._determineHighpass(frequency)

        self._adevs['diplexer'].maw(diplexer)
        self._adevs['coil1_transformer'].maw(transformator)

        if self.use_second_coil:
            self._adevs['coil2_transformer'].maw(transformator)

        self._adevs['highpass'].maw(highpass)

    def _calculatePossibleCapacities(self):
        caps = {}
        for c3bits in xrange(16):
            for c1c2serial in xrange(2):
                for c1bits in xrange(64):
                    for c2bits in xrange(32):
                        args = (c1bits, c2bits, c3bits, c1c2serial)
                        caps[self._calcSerialCapacity(*args)] = args
        odict = OrderedDict(sorted(iteritems(caps)))
        return odict

    def _calcNecessaryCapacity(self, frequency):
        return (1/(2*pi*frequency)) ** 2 / self.coil_inductivity

    def _determineDiplexer(self, freq):
        return 1 if freq > self.diplexer_threshold_frequency else 0

    def _determineTransformer(self, freq):
        if freq > self.transformer_threshold_frequencies[1]:
            return 2
        elif freq > self.transformer_threshold_frequencies[0]:
            return 1
        else:
            return 0

    def _determineHighpass(self, frequency):
        result = 0

        if frequency == 0 or frequency >= 1e6:
            return result

        # poly val
        x = round(frequency / 1000, 2)
        fg_f = 0
        for (i, coeff) in enumerate(self.HIGHPASS_POLYNOM):
            fg_f += coeff * x ** i

        c = 1 / (2 * pi * 22 * frequency * fg_f)

        c2 = 0
        ii = 1
        nn = 0
        for cap in self.HIGHPASS_CAPACITIES:
            if (c2 + cap) <= c:
                c2 += cap
                result += ii
                nn += 1

                if nn > 3:
                    return result
            ii *= 2

        return result

    def _getCurrentAdjustmentQuality(self):
        """Reads the current adjustment quality multiple times (defined by
        "tuning_points") and returns the median."""
        revp = numpy.median([self._adevs['pa_revp'].read(0)
                             for _ in xrange(self.tuning_points)])
        fwdp = numpy.median([self._adevs['pa_fwdp'].read(0)
                             for _ in xrange(self.tuning_points)])

        return (fwdp - revp) / (fwdp + revp)

    def _getResonanceFrequency(self, coil):
        result = 0.0

        # bank capacities
        serial_capacity = self._getSerialCapacity(coil)
        if serial_capacity == 0:
            return 0.0
        c1 = self._getBankCapacity(coil, 1)
        c2 = self._getBankCapacity(coil, 2)

        # fixed capacities
        serial_output_capacity_c1 = self.serial_output_capacity_c1_c2 \
                                    - self.serial_output_capacity_c2
        coil_capacity = self.coil_self_capacitance + self.cbox2_output_capacity

        if self._isCBox2Bypassed(coil):  # double readout for readability
            coil_capacity += self.cable_capacity + self.cbox2_input_capacity

            if c1 and serial_output_capacity_c1 > 0:
                coil_capacity += serial_output_capacity_c1
            if c2:
                coil_capacity += self.serial_output_capacity_c2

        if coil_capacity == 0:
            result = 1 / (2 * pi
                          * sqrt(self.coil_inductivity * serial_capacity))
        else:
            wp = 1 / sqrt(self.coil_inductivity * coil_capacity)
            p = wp ** 2
            q = -p / (self.coil_inductivity * serial_capacity)
            result = sqrt(-p / 2 + sqrt((p / 2) ** 2 - q)) / (2 * pi)

        result = 100 * round(result / 100, 2)

        self.log.debug('Coil %d resonance frequency: %g', coil, result)
        return result

    def _getSerialCapacity(self, coil):
        result = 0

        # calculate bank capacities
        c1bits = self._adevs['coil%d_c%d' % (coil, 1)].read(0)
        c2bits = self._adevs['coil%d_c%d' % (coil, 2)].read(0)
        c3bits = self._adevs['coil%d_c%d' % (coil, 3)].read(0)
        c1c2serial = self._isC1C2Serial(coil)

        result = self._calcSerialCapacity(c1bits, c2bits, c3bits, c1c2serial)
        self.log.debug('Coil %d, serial capacity: %g', coil, result)
        return result

    def _calcSerialCapacity(self, c1bits, c2bits, c3bits, c1c2serial):
        # calculate bank capacities
        c1 = self._calcBankCapacity(1, c1bits)
        c2 = self._calcBankCapacity(2, c2bits)
        c3 = self._calcBankCapacity(3, c3bits)

        # check for bypasses
        bypass_cbox1 = (not c1 and not c2)
        bypass_cbox2 = not c3

        # calculate capacities of cbox1
        if c1c2serial and c1 and c2:
            cbox1_capacity = (c1 * c2) / (c1 + c2)
        else:  # parallel, or serial and c2 disabled (c2 = 0)
            cbox1_capacity = c1 + c2

        # calculate capacities of cbox2 (at coil)
        if not bypass_cbox2:
            if not bypass_cbox1:
                result = (cbox1_capacity * c3) / (cbox1_capacity + c3)
            else:
                result = c3
        else:
            result = cbox1_capacity

        return result

    def _getBankCapacity(self, coil, bank):
        '''Reads current bank setup and calculates the bank capacity.'''
        bits = self._adevs['coil%d_c%d' % (coil, bank)].read(0)
        result = self._calcBankCapacity(bank, bits)
        self.log.debug('Coil %d, bank %d capacity: %g', coil, bank, result)
        return result

    def _calcBankCapacity(self, bank, bits):
        '''Calculates accumulated bank capacity.'''
        # accumulate the set capacities
        result = 0
        for i, capacity in enumerate(self.BANK_CAPACITIES[bank - 1]):
            if bits & (1 << i):
                result += capacity

        return result

    def _isCBox2Bypassed(self, coil):
        return self._getBankCapacity(coil, 3) == 0

    def _isC1C2Serial(self, coil):
        return self._adevs['coil%d_c1c2serial' % coil].read(0) == 1
