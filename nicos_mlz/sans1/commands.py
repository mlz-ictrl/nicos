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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

"""Module for SANS-1 specific commands."""

from nicos import session
from nicos.commands import usercommand
from nicos.commands.device import maw, move
from nicos.commands.measure import count

__all__ = ['tcount', 'freqmes']

@usercommand
def tcount(time_to_measure):
    """Set the switch, fg1 and fg2 for tisane counts."""
    out_1 = session.getDevice('out_1')
    #tisane_fg1_sample = session.getDevice('tisane_fg1_sample')
    #tisane_fg2_det = session.getDevice('tisane_fg2_det')
    #maw(out_1, 0)
    #maw(tisane_fg1_sample, 'On')
    #maw(tisane_fg2_det, 'On')

    maw(out_1, 1)
    count(time_to_measure)

    maw(out_1, 0)
    #maw(tisane_fg1_sample, 'Off')
    #maw(tisane_fg2_det, 'Off')


@usercommand
def freqmes(assumed_freq, number_of_counts):
    """Determine mean frequency of the frequency counter for *number_of_counts*.

    Used or tisane measurements.
    """
    import numpy
    import time
    valuedev = session.getDevice('tisane_fc')
    #erwartete frequenz setzen
    valuedev._dev.expectedFreq = assumed_freq

    value_list = []
    wrong_list = []
    obere_grenze = assumed_freq*1.1
    untere_grenze = assumed_freq*0.9

    print('Berechnung über %i Messpunkte' % number_of_counts)

    for i in range(number_of_counts):
        print(i + 1)
        value = valuedev.read(0)
        if value > untere_grenze and value < obere_grenze:
            value_list.append(value)
        else:
            wrong_list.append(value)
        time.sleep(0.1)
    mean_value = numpy.mean(value_list)
    std_value = numpy.std(value_list)
    print("------------------------------------")
    print("Erwartungswert              = %f" % assumed_freq)
    print("Untere Grenze (90)          = %f" % untere_grenze)
    print("Obere Grenze (110)          = %f" % obere_grenze)
    print("Anzahl aller Messpunkte     = %i" % number_of_counts)
    print("Anzahl korrekter Messpunkte = %i" % len(value_list))
    print("Mittelwert [Hz]             = %f" % mean_value)
    print("Mittelwert [rpm]            = %f" % (mean_value*60))
    print("Standardabweichung          = %f" % std_value)
    print("Verworfene Werte: %s" % wrong_list)


@usercommand
def setfg(freq_sample, amplitude_sample, offset_sample, shape_sample, freq_detector):
    """Open the trigger relais and sets desired values of the multi frequency.

    generator for the sample and the detector
    example: setfg(100, 0.5, 0.1, 'sin', 200)
    options for shape_samle:
    SINE = 'sin'
    Square = 'squ'
    Ramp = 'ramp' (with symmetry of 50%)
    Triangle = 'tri'
    """
    multifg = session.getDevice('tisane_fg_multi')

    out_1 = session.getDevice('out_1')
    maw(out_1, 0)

    # template = ':SOUR1:FUNC:SHAP SQU;:SOUR1:FREQ 116.621036;:SOUR1:VOLT 2.4;:SOUR1:VOLT:UNIT ' \
    #            'VPP;:SOUR1:VOLT:OFFS 1.3;:SOUR1:FUNCtion:SQU:DCYCle 50;:SOUR1:AM:STATe ' \
    #            'OFF;:SOUR1:SWEep:STATe OFF;:SOUR1:BURSt:MODE TRIG;:OUTP1:LOAD 50;:OUTP1:POL ' \
    #            'NORM;:TRIG1:SOUR EXT;:SOUR1:BURSt:NCYCles 9.9E37;:SOUR2:FUNC:SHAP ' \
    #            'SQU;:SOUR2:FREQ 116.621036;:SOUR2:VOLT 5;:SOUR2:VOLT:UNIT VPP;:SOUR2:VOLT:OFFS ' \
    #            '1.3;:SOUR2:FUNCtion:SQU:DCYCle 50;:SOUR2:AM:STATe OFF;:SOUR2:SWEep:STATe ' \
    #            'OFF;:SOUR2:BURSt:MODE TRIG;:OUTP2:LOAD 50;:OUTP2:POL NORM;:TRIG2:SOUR ' \
    #            'EXT;:SOUR2:BURSt:NCYCles 9.9E37;:SOUR1:BURSt:STATe ON;:SOUR2:BURSt:STATe ' \
    #            'ON;:OUTP1 ON;:OUTP2 ON;'
    template_new = ':SOUR1:FUNC:SHAP {0};:SOUR1:FREQ {1};:SOUR1:VOLT {2};:SOUR1:VOLT:UNIT VPP;' \
                   ':SOUR1:VOLT:OFFS {3};:SOUR1:FUNCtion:SQU:DCYCle 50;:SOUR1:AM:STATe OFF;' \
                   ':SOUR1:SWEep:STATe OFF;:SOUR1:BURSt:MODE TRIG;:OUTP1:LOAD 50;:OUTP1:POL NORM;' \
                   ':TRIG1:SOUR EXT;:SOUR1:BURSt:NCYCles 9.9E37;:SOUR2:FUNC:SHAP SQU;' \
                   ':SOUR2:FREQ {4};:SOUR2:VOLT 5;:SOUR2:VOLT:UNIT VPP;:SOUR2:VOLT:OFFS 1.3;' \
                   ':SOUR2:FUNCtion:SQU:DCYCle 50;:SOUR2:AM:STATe OFF;:SOUR2:SWEep:STATe OFF;' \
                   ':SOUR2:BURSt:MODE TRIG;:OUTP2:LOAD 50;:OUTP2:POL NORM;:TRIG2:SOUR EXT;' \
                   ':SOUR2:BURSt:NCYCles 9.9E37;:SOUR1:BURSt:STATe ON;:SOUR2:BURSt:STATe ON;' \
                   ':OUTP1 ON;:OUTP2 ON;'.format(shape_sample, freq_sample, amplitude_sample,
                                                 offset_sample, freq_detector)
    strings = dict(multifg.strings)
    strings['arm'] = template_new
    multifg.strings = strings
    move(multifg, 'arm')
