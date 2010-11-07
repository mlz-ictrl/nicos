#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS setup file for system "devices"
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

name = 'system setup'

devices = dict(
    histlogger = device('nicm.history.LogfileHistory',
                        basefilename = 'log/'),

    localhistory = device('nicm.history.LocalHistory'),

    cachehistory = device('nicm.history.CacheHistory',
                          server = 'localhost:14869',
                          prefix = 'nicos/test/',
                          ),

    filesink = device('nicm.data.AsciiDatafileSink',
                      prefix = 'data'),

    consolesink = device('nicm.data.ConsoleSink',
                         ),

    System = device('nicm.system.System',
                    logpath = '.',
                    datapath = 'data/',
                    sinks = ['consolesink', 'filesink'],
                    histories = ['cachehistory'],
                    ),

    Experiment = device('nicm.experiment.Experiment',
                        users = []),
)
