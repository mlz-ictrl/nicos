# -*- coding: utf-8 -*-
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
#   Christian Franz  <christian.franz@frm2.tum.de>
#
# *****************************************************************************

"""Module for RESEDA specific commands."""

from __future__ import absolute_import, division, print_function

import scipy.constants as co

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.device import maw, move, stop, wait
from nicos.commands.measure import count
from nicos.commands.scan import manualscan

__all__ = ['zero', 'setecho', 'set_cascade', 'pol', 'miezescan', 'miezetau']


@helparglist('wavelength, deltaFreq, distance')
@usercommand
def miezetau(wavelength, deltaFreq, distance):
    """Calculate MIEZE time.

    It will be calculated for wavelength (A), difference frequency of coils
    (Hz) and sample detector distance (m).
    deltaFreq is the single difference, not double difference.
    """
    # co.m_n  Mass of neutron
    # co.h    Planck constant
    return (2*co.m_n**2/co.h**2 * (wavelength*1e-10)**3 * deltaFreq * distance *
            1e9)

@usercommand
def zero():
    """Shut down all (static) power supplies."""
    ps = ['hrf_0a', 'hrf_0b', 'hrf_1a', 'hrf_1b', 'hsf_0a', 'hsf_0b', 'hsf_1', 'sf_0a',
          'sf_0b', 'sf_1', 'gf0', 'gf1', 'gf2', 'gf4', 'gf5', 'gf6', 'gf7',
          'gf8', 'gf9', 'gf10']
    for powersupply in ps:
        powersupply = session.getDevice(powersupply)
        move(powersupply, 0.001)


@usercommand
def set_flipper_off():
    """Shut down flippers.

    After shutting down the neutrons are guided through instrument for
    image mode (MIEZE)
    """
    ps = ['sf_0a', 'sf_0b', 'cbox_0a_fg_amp', 'cbox_0b_fg_amp']
    reg = ['cbox_0a_reg_amp', 'cbox_0b_reg_amp']
    for powersupply in ps:
        powersupply = session.getDevice(powersupply)
        move(powersupply, 0.01)
    for regulator in reg:
        regulator = session.getDevice(regulator)
        stop(regulator)


@helparglist('time')
@usercommand
def setecho(time):
    """Wrap setting of an echotime."""
    echotime = session.getDevice('echotime')
    move(echotime, time)
    set_cascade()
    wait(echotime)


@usercommand
def set_cascade():
    """Set Cascade Frequency Generator Freqs and Trigger."""
    echotime = session.getDevice('echotime')
    psd_chop_freq = session.getDevice('psd_chop_freq')
    psd_timebin_freq = session.getDevice('psd_timebin_freq')
    fg_burst = session.getDevice('fg_burst')
    tau = echotime.target
    f1 = echotime.currenttable[tau]['cbox_0a_fg_freq']
    f2 = echotime.currenttable[tau]['cbox_0b_fg_freq']
    move(psd_chop_freq, 2 * (f2 - f1))
    move(psd_timebin_freq, 32 * (f2 - f1))
    move(fg_burst, 'arm')
    move(fg_burst, 'trigger')


@helparglist('echolist, counttime')
@usercommand
def miezescan(echolist, counttime):
    """Iterate over a list of echotimes -> measure one S(Q,t) curve

    echolist: list of echotimes
    counttime: counting time (the **same** for all list entries)
    """
    echotime = session.getDevice('echotime')
    with manualscan(echotime, counttime):
        for etime in echolist:
            move(echotime, etime)
            set_cascade()
            count(counttime)


@helparglist('up, down')
@usercommand
def pol(up, down):
    """Calculate contrast or polarisation."""
    return (up - down) / (up + down)


@helparglist('device, start, step, numsteps')
@usercommand
def freqscan(device, start, step, numsteps):
    """Special scan for finding a resonance.

    Detector must be set to according device (e.g. cbox_0a_coil_rms)
    device: cbox_0a_fg_freq
    start:  starting frequency in Hz
    step:   steps in Hz
    numsteps: number of steps
    """
    with manualscan(device):
        for i in range(numsteps):
            maw(device, start + step*i)
            session.delay(0.2)
            count(1)


@usercommand
def img():
    "Setting the Cascade Detector to image mode"

    session.getDevice('psd_channel').mode = 'image'


@usercommand
def tof():
    "Settting the Cascade Detector to tof mode"

    session.getDevice('psd_channel').mode = 'tof'
