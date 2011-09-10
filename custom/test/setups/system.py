#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

name = 'system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink'],
    notifiers = [],
)

devices = dict(
    Sample   = device('nicos.tas.TASSample'),

    Exp      = device('nicos.experiment.Experiment',
                      datapath = ['data'],
                      sample = 'Sample'),

    filesink = device('nicos.data.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('nicos.data.ConsoleSink'),

    Space    = device('nicos.data.FreeSpace',
                      path = 'data',
                      minfree = 5),
)
