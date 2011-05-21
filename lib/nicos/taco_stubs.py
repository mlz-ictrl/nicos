#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""NICOS TACO stub implementation, to support running on systems without
installed TACO libraries.

If this module is imported, it is assumed that the TACO client libraries already
haven't been found.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import new
import sys

from nicos.errors import ProgrammingError


class NICOSTACOStub(object):
    def __init__(self, devname):
        raise ProgrammingError('trying to instantiate a stub TACO class')


STUBS = dict(
    TACOClient = ['exception TACOError'],
    TACOStates = [],
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
)


def generate():
    for modname, content in STUBS.iteritems():
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
