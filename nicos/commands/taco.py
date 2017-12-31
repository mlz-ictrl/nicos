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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TACO specific commands for NICOS."""

import os
import subprocess

from nicos import session
from nicos.commands import usercommand
from nicos.utils import printTable, createSubprocess
from nicos.pycompat import string_types

from nicos.devices.taco.core import TacoDevice

import TACOClient
import TACOStates as st
import TACOCommands as cmds


__all__ = ['TacoRes', 'TacoStatus']


def _client(dev):
    if isinstance(dev, TacoDevice):
        return dev._dev
    return TACOClient.Client(dev)


@usercommand
def TacoRes(dev):
    """List all resources for the given TACO device."""
    cl = _client(dev)
    items = []
    for res, info in sorted(cl.deviceQueryResourceInfo().items()):
        try:
            rv = cl.deviceQueryResource(res)
        except Exception:
            rv = '<n/a>'
        items.append((res, info['info'], rv))
    session.log.info('TACO resources for %s:', cl.deviceName())
    printTable(('name', 'info', 'value'), items, session.log.info)


def _list_devices(server):
    subp = createSubprocess('/opt/taco/bin/db_devicelist -n %s' % server,
                            shell=True, stdout=subprocess.PIPE)
    out = subp.communicate()[0]
    for line in out.splitlines():
        if line.startswith('\t'):
            yield line.strip()

bold = red = blue = darkgray = darkgreen = lambda x: x

typemap = {
    ('IOStringIO', 'RS232StringIO'): 1,
    ('IOAnalogOutput', 'MotorMotor'): 1,
    ('Modbus', 'RS485'): 1,
    ('EncoderEncoder', 'IOAnalogInput'): 0,
    ('IOAnalogOutput', 'TemperatureController'): 1,
    ('IOAnalogInput', 'TemperatureSensor'): 1,
}

typedisplay = {
    'EncoderEncoder': 'Encoder',
    'IOAnalogInput': 'AnalogInput',
    'IOAnalogOutput': 'AnalogOutput',
    'IOCounter': 'Counter',
    'IODigitalInput': 'DigitalInput',
    'IODigitalOutput': 'DigitalOutput',
    'IOStringIO': 'StringIO',
    'IOTimer': 'Timer',
    'PowerSupplyCurrentControl': 'PowerSupply',
    'RS232StringIO': 'RS232',
    'RS485': 'RS485',
    'MotorMotor': 'Motor',
    'TemperatureController': 'TempCtrl',
    'TemperatureSensor': 'TempSens',
}


@usercommand
def TacoStatus(server=''):
    """List all TACO devices and check their status."""
    # "unused" locals -- pylint: disable=W0612
    def check_IOCounter(dev, client, state):
        return state in [st.COUNTING, st.STOPPED]

    def check_IOTimer(dev, client, state):
        return state in [st.STARTED, st.STOPPED, st.PRESELECTION_REACHED]

    def check_MotorMotor(dev, client, state):
        return state in [st.DEVICE_NORMAL, st.MOVING]

    def check_RS485(dev, client, state):
        return state == st.ON

    def check_TemperatureController(dev, client, state):
        return state in [st.PRESELECTION_REACHED, st.MOVING, st.DEVICE_NORMAL,
                         st.UNDEFINED]

    def check_TMCSAdmin(dev, client, state):
        return state in [st.STARTED, st.STOPPED]

    def check_PowerSupplyCurrentControl(dev, client, state):
        try:
            client.execute(cmds.READ_DOUBLE)
        except TACOClient.TACOError as err:
            return 'not readable: %s' % err
        else:
            return True

    def check_IOAnalogInput(dev, client, state):
        try:
            client.execute(cmds.READ_DOUBLE)
        except TACOClient.TACOError as err:
            return 'not readable: %s' % err
        else:
            return True

    if not server:
        server = os.getenv('NETHOST')
    session.log.info('Checking TACO devices on %s...', bold(server))
    for dev in sorted(_list_devices(server)):
        dev = '//%s/%s' % (server, dev)
        try:
            client = TACOClient.Client(dev)
            state = client.deviceState()
            status = st.stateDescription(state)
        except TACOClient.TACOError as err:
            ok = False
            disp = '-' * 15
            errmsg = err.args[0]
            if errmsg == 'Device has not been fully imported yet, ' \
                         '(hint: start the device server)':
                errmsg = 'Server not started'
            status = '*** ' + errmsg
        else:
            dtypes = client.deviceTypes()
            if tuple(dtypes) in typemap:
                dtype = dtypes[typemap[tuple(dtypes)]]
            else:
                dtype = dtypes and dtypes[-1] or '???'
            disp = typedisplay.get(dtype, dtype)
            if not disp:
                disp = '/'.join(dtypes)

            checker = locals().get('check_' + dtype, None)
            if checker:
                ok = checker(dev, client, state)
                if isinstance(ok, string_types):
                    status = ok
                    ok = False
            else:
                ok = state == st.DEVICE_NORMAL

        session.log.info('%s %s %s %s',
                         darkgray('[' + disp.ljust(15) + ']'),
                         blue(dev.ljust(35)),
                         ok and darkgreen('  ok:') or red('FAIL:'),
                         ok and status or bold(status))
