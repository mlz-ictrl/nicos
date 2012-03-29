#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

description = 'system setup'

sysconfig = dict(
    cache = 'bunker.pgaa.frm2',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

devices = dict(
    Sample   = device('nicos.experiment.Sample'),

    Instrument = device('nicos.instrument.Instrument',
                        responsible = 'Dr. Petra Kudejova',
                       ),

    Exp      = device('nicos.experiment.Experiment',
                      dataroot = '/mnt/tequila/data/',
                      sample = 'Sample'),

    filesink = device('nicos.data.AsciiDatafileSink',
                     ),

    conssink = device('nicos.data.ConsoleSink'),

    daemonsink = device('nicos.data.DaemonSink'),

    Space    = device('nicos.generic.FreeSpace',
                      minfree = 0.5),
)
