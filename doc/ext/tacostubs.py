# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

# generate stub TACO modules as needed to be able to import nicos.devices.taco
# modules and document them

import sys
import new


class NICOSTACOStub(object):
    pass


STUBS = dict(
    TACOClient = ['class Client', 'exception TACOError'],
    TACOStates = [],
    TACOCommands = [],
    DEVERRORS = [],
    IOCommon = ['MODE_NORMAL=0', 'MODE_RATEMETER=1', 'MODE_PRESELECTION=2'],
    IO = ['class AnalogInput', 'class AnalogOutput', 'class DigitalInput',
          'class DigitalOutput', 'class StringIO', 'class Timer',
          'class Counter'],
    Encoder = ['class Encoder'],
    Motor = ['class Motor'],
    PowerSupply = ['class CurrentControl', 'class VoltageControl'],
    RS485Client = ['class RS485Client'],
    Temperature = ['class Sensor', 'class Controller'],
    TMCS = ['class Channel', 'class Admin'],
    Modbus = ['class Modbus'],
    ProfibusDP = ['class IO'],
    Detector = ['class Detector'],
)


def generate_stubs():
    for modname, content in STUBS.iteritems():
        try:
            __import__(modname)
        except Exception:
            pass  # generate stub below
        else:
            continue
        mod = new.module(modname, "NICOS stub module")
        for obj in content:
            if obj.startswith('class '):
                setattr(mod, obj[6:], type(obj[6:], (NICOSTACOStub,), {}))
            elif obj.startswith('exception '):
                setattr(mod, obj[10:], type(obj[10:], (Exception,), {}))
            else:
                name, value = obj.split('=')
                setattr(mod, name, eval(value))
        sys.modules[modname] = mod


def setup(app):
    generate_stubs()
    return {'parallel_read_safe': True}
