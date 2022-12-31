#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

from math import ceil

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.basic import AddSetup, RemoveSetup, sleep
from nicos.commands.device import maw
from nicos.commands.scan import manualscan
from nicos.core import UsageError
from nicos.services.daemon.script import parseScript


@usercommand
@helparglist('scan dev in the range between start and end with stepwidth step'
             ' and execute command at each step')
def scanmotor(dev, start, end, step, command):
    if abs(step) > .0001:
        np = ceil(((end - start) / float(step))) + 1
    else:
        raise UsageError('step must be bigger then 0')
    nxsink = session.getDevice('nxsink')
    nxsink.settypes = ['point', ]
    with manualscan(dev):
        for i in range(np):
            maw(dev, start + i * step)
            code, _ = parseScript(command)
            for i, c in enumerate(code):
                exec(c, session.namespace)
    nxsink.settypes = ['point', 'scan']


@usercommand
@helparglist('Switch into TOF mode')
def tofel():
    RemoveSetup('detector')
    AddSetup('detector_strobo')
    dev = session.getDevice('port14')
    dev.execute('EL1D')
    sleep(3)
    dev.execute('TIWI 8')
    sleep(3)
    dev.execute('COIN 7')
    sleep(3)


@usercommand
@helparglist('Switch into 2D mode')
def antitofel():
    RemoveSetup('detector_strobo')
    AddSetup('detector')
    dev = session.getDevice('port14')
    dev.execute('EL2D')
    sleep(3)
    dev.execute('TIWI 8')
    sleep(3)
    dev.execute('COIN 7')
    sleep(3)
