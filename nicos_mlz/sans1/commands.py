#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands import usercommand
from nicos.commands.device import maw, move
from nicos.commands.measure import count

__all__ = ['tcount', 'freqmes']

@usercommand
def tcount(time_to_measure):
    """Initiate a count using the flipbox

    1) close the relais of the flipbox in order to burst the multifg device
    2) count for x seconds (in listmode)
    3) open the relais of the flipbox to prepare for a new count
    """

    session.delay(5)

    out_1 = session.getDevice('out_1')
    #tisane_fg1_sample = session.getDevice('tisane_fg1_sample')
    #tisane_fg2_det = session.getDevice('tisane_fg2_det')
    #maw(out_1, 0)
    #maw(tisane_fg1_sample, 'On')
    #maw(tisane_fg2_det, 'On')

    maw(out_1, 1)

    session.delay(5)

    count(time_to_measure)

    session.delay(5)

    maw(out_1, 0)

    session.delay(5)

    #maw(tisane_fg1_sample, 'Off')
    #maw(tisane_fg2_det, 'Off')
    print("measurement finished")


@usercommand
def freqmes(assumed_freq, number_of_counts):
    """Triggers and measures the current tisane frequency

    by averaging over `number_of_counts` measurements.
    Also prints average and standard deviation.

    Needs to have a (rough) estimation of the frequency beforehand.

    Used for tisane measurements.
    """
    import numpy
    valuedev = session.getDevice('tisane_fc')
    #erwartete frequenz setzen
    valuedev._dev.expectedFreq = assumed_freq

    armdev = session.getDevice('tisane_fc_trigger')
    #tisane_fc_trigger -> arm; parameter in fc schreiben
    maw(armdev, 'arm')
    session.delay(0.5)

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
        session.delay(0.1)
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

    maw(armdev, 'idle')


@usercommand
def setfg(freq_sample, amplitude_sample, offset_sample, shape_sample, freq_detector):
    """Set several values of the multi frequency generator at once

    and switch to burst mode.

    example: setfg(100, 0.5, 0.1, 'sin', 200)
    options for shape_samle:
    SINE = 'sin'
    Square = 'squ'
    Ramp = 'ramp' (with symmetry of 50%)
    Triangle = 'tri'

    Used for tisane measurements.
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
    template = ':SOUR1:FUNC:SHAP {0};:SOUR1:FREQ {1};:SOUR1:VOLT {2};:SOUR1:VOLT:UNIT VPP;' \
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
    strings['arm'] = template
    multifg.strings = strings
    move(multifg, 'arm')


@usercommand
def tcalc(sd, cs, chop_speed, wav_mean, wav_spread):
    """Calculate the tisane frequencies from a given set of parameters.

    Used for preparation of tisane measurements.
    """

    import math

    chop_num = 14.0

    #the chopper
    T_c = 1 / (chop_num * chop_speed)

    #lets calculate the sample repetition time using the TISANE equation
    T_s = T_c * sd / (sd + cs)

    #sample frequency
    F_s = 1/T_s

    #lets calculate the detector repetition tiem using the TISANE equation
    T_d = T_s * (sd + cs) / cs

    #detector frequency
    F_d = 1 / T_d

    #define wavelength [A]
    wav = []

    i = 4
    while i <= 20:
        wav.append(float(i))
        i += 0.01

    speed = []
    for i in wav:
        speed.append(6.262e-34 / (1.674e-27 * i * 1e-10))

    #transmission function of the selector is assumed to be gaussian
    trans_selector = []
    for i in wav:
        trans_selector.append(math.exp(-0.5 * ((i - wav_mean)**2) - ((0.5 * wav_mean * 0.01 * wav_spread)**2)))

    #define a cutoff for the slowest and the fastest neutrons
    # use two sigma for an assumption of the maximal and mininmal test_doppler_wavelength_0
    wav_min = wav_mean * (1 - 0.01 * wav_spread)
    wav_max = wav_mean * (1 + 0.01 * wav_spread)

    speed_min = 6.262e-34 / (1.674e-27 * wav_max * 1e-10)
    speed_max = 6.262e-34 / (1.674e-27 * wav_min * 1e-10)

    #calculate the frame overlap
    frame_overlap_detector = ((cs + sd) / speed_min - (cs + sd) / speed_max) / T_c
    frame_overlap_sample = (cs / speed_min - cs / speed_max) / T_c

    print("Chopper speed             = %f [Hz]" % chop_speed)
    print("Chopper opening frequency = %f [rpm]" % (chop_speed*60))
    print("Chopper numbers           = %f" % chop_num)
    print("SD                        = %f [m]" % sd)
    print("Sample frequency          = %.6f [Hz]" % F_s)
    print("Sample time               = %f [mu s]" % (T_s*1000000))
    print("Detector frequency        = %.6f [Hz]" % F_d)
    print("Frame overlap sample      = %f" % frame_overlap_sample)
    print("Frame overlap detector    = %f" % frame_overlap_detector)
