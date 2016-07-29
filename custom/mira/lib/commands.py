#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Module for MIRA specific commands."""

from nicos import session
from nicos.commands import usercommand
from nicos.commands.output import printinfo
from nicos.commands.device import move, read


@usercommand
def FlushCryo():
    """Flush CCR5 sample tube with Helium and then evacuate it again."""
    CryoGas = session.getDevice('ccr5_gas_switch')
    CryoVac = session.getDevice('ccr5_vacuum_switch')
    Pcryo = session.getDevice('ccr5_p1')
    move(CryoGas, 'on')
    while Pcryo.read() < 995:
        session.delay(1)
    session.delay(5)
    read(Pcryo)
    move(CryoGas, 'off')
    move(CryoVac,'on')
    while Pcryo.read() > 0.15:
        session.delay(1)
    session.delay(5)
    read(Pcryo)
    move(CryoVac, 'off')
    printinfo('Cryo flushed!')

@usercommand
def SetCryoGas(target):
    """Open CCR5 sample tube gas valve until target pressure is reached."""
    CryoGas = session.getDevice('ccr5_gas_switch')
    Pcryo = session.getDevice('ccr5_p1')
    move(CryoGas,'on')
    while Pcryo.read() < target:
        session.delay(0.01)
    move(CryoGas,'off')

@usercommand
def SetCryoVac(target):
    """Open CCR5 sample tube vacuum valve until target pressure is reached."""
    CryoVac = session.getDevice('ccr5_vacuum_switch')
    Pcryo = session.getDevice('ccr5_p1')
    move(CryoVac,'on')
    while Pcryo.read() > target:
        session.delay(0.01)
    move(CryoVac,'off')
