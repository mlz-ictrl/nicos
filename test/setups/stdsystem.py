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
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

from os import path
from test.utils import cache_addr, runtime_root, module_root

name = 'test system setup'
# This setup is called "stdsystem" so that it is not loaded automatically
# on every loadSetup.

sysconfig = dict(
    cache = cache_addr,
    experiment = 'Exp',
    instrument = 'Instr',
    datasinks = [],
    notifiers = ['testnotifier'],
)

modules = ['nicos.commands.standard']

devices = dict(
    Sample = device('devices.sample.Sample'),
    # test that both nicos.(...) and (...) work
    Exp = device('devices.experiment.Experiment',
        sample = 'Sample',
        elog = True,
        dataroot = path.join(runtime_root, 'data'),
        propprefix = 'p',
        templates = path.join(module_root, 'test', 'script_templates'),
        zipdata = True,
        serviceexp = 'service',
        lowlevel = False,
        localcontact = 'M. Aintainer <m.aintainer@frm2.tum.de>',
    ),
    Instr = device('devices.instrument.Instrument',
        instrument = 'INSTR',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        operators = ['NICOS developer team'],
    ),
    testnotifier = device('test.utils.TestNotifier',
        sender = 'sender@example.com',
    ),
)
