#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Poller setup
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

name = 'setup for the poller'
group = 'special'

includes = ['all_devices']

_processes = {
    'mieze':    ['amp1', 'amp2', 'amp3', 'amp4',
                 'freq1', 'freq2', 'freq3', 'freq4'],
    #'power':    ['rp1', 'fp1', 'rp2', 'fp2'],
    #'reactor':  ['Power', 'NL6', 'Sixfold', 'Crane'],
    'lakeshore':['T', 'TA', 'TB', 'TC', 'TD'],
    'misc':     ['MonHV', 'DetHV', 'PSDHV'],
    'detector': ['det'],
    'valves':   ['atten1', 'atten2', 'lamfilter', 'FOLin', 'FlipperMira1in',
                 'FlipperMira2in'],
    #'mono1':    ['mth', 'mtt', 'mtx', 'mty', 'mgx', 'mchanger'],
    'mono2':    ['m2th', 'm2tt', 'm2tx', 'm2ty', 'm2gx', 'm2fv'],
    'sample':   ['phi', 'om', 'stx', 'sty', 'stz', 'sgx', 'sgy'],
    'slits':    ['s3', 's4'],
}

devices = dict(
    Poller = device('nicos.poller.Poller',
                    processes = _processes,
                    loglevel = 'info'),
    System = device('nicos.system.System',
                    cache = 'Cache',
                    datasinks = [],
                    experiment = None,
                    instrument = None,
                    notifiers = []),
)
