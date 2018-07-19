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
#   Christian Franz  <christian.franz@frm2.tum.de>
#
# *****************************************************************************

"""Module for RESEDA specific commands."""

from nicos import session
from nicos.commands import usercommand
from nicos.commands.device import move, stop, wait
from nicos.commands.measure import count
from nicos.commands.scan import manualscan

__all__ = ['zero', 'setecho', 'set_cascade', 'pol', 'miezescan']


@usercommand
def zero():
    """Shutting down all (static) power supplies."""
    ps = ['hrf_0a', 'hrf_0b', 'hrf_1', 'hsf_0a', 'hsf_0b', 'hsf_1', 'sf_0a',
          'sf_0b', 'sf_1', 'gf0', 'gf1', 'gf2', 'gf4', 'gf5', 'gf6', 'gf7',
          'gf8', 'gf9', 'gf10']
    for powersupply in ps:
        powersupply = session.getDevice(powersupply)
        move(powersupply, 0.001)


@usercommand
def set_flipper_off():
    """Shuts down flippers.

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


@usercommand
def miezescan(echolist, counttime):
    echotime = session.getDevice('echotime')
    with manualscan(echotime, counttime):
        for etime in echolist:
            move(echotime, etime)
            set_cascade()
            count(counttime)


@usercommand
def pol(up, down):
    """Calculate contrast or polarisation."""
    return (up - down) / (up + down)
