#  -*- coding: utf-8 -*-
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'refsans10.refsans.frm2',
    instrument = 'REFSANS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['commands.standard', 'refsans.commands']

# SYSTEM NEVER INCLUDES OTHER SETUPS !!!


devices = dict(
    REFSANS  = device('devices.instrument.Instrument',
                      description = 'Container storing Instrument properties',
                      instrument = 'REFSANS',
                      responsible = 'Matthias Pomm <matthias.pomm@hzg.de>',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'Container storing Sample properties',
                     ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'Container storing Experiment properties',
                      dataroot = '/data',
                      sample = 'Sample',
                      #~ elog = False,
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      description = 'Device saving scanfiles',
                     ),

    conssink = device('devices.datasinks.ConsoleSink',
                      description = 'Device outputting logmessages to the console',
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        description = 'The daemon Device, coordinating all the heavy lifting',
                       ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      minfree = 5,
                     ),
)
