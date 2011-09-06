#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS monitor setup file with a few devices
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

name = 'setup for the status monitor'
group = 'special'

_expcolumn = [
    ('Experiment', [
        [{'name': 'Proposal', 'key': 'exp/proposal', 'width': 7},
         {'name': 'Title', 'key': 'exp/title', 'width': 40,
          'istext': True},
         {'name': 'Current status', 'key': 'exp/action', 'width': 30,
          'istext': True},
         {'name': 'Last file', 'key': 'filesink/lastfilenumber'}]]),
]

_warnings = [
    ('a1/value', '> 20', 'a1 value > 20'),
]

_axisblock = (
    'Axis devices',
    [['a1', 'm1', 'c1'],
     ['a2', 'm2']],
    'misc')

_detectorblock = (
    'Detector devices',
    [[{'name': 'timer', 'dev': 'timer'},
      {'name': 'ctr1', 'dev': 'ctr1', 'min': 100, 'max': 500},
      {'name': 'ctr2', 'dev': 'ctr2'}]],
    'detector')

_otherblock = (
    'Other devices',
    [[{'dev': 'slit', 'width': 20, 'name': 'Slit'}],
     [{'dev': 'sw', 'width': 4, 'name': 'Switcher'}],
     [{'dev': 'freq', 'name': 'Frequency'}, {'unit': 'mV', 'key': 'freq/amplitude', 'name': 'Amplitude'}]],
    'misc')

_rightcolumn = [
    _axisblock,
    _detectorblock,
]

_leftcolumn = [
    _otherblock,
]

devices = dict(
    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'Test status monitor',
                     loglevel = 'info',
                     server = 'localhost:14869',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Monospace',
                     padding = 5,
                     layout = [[_expcolumn], [_rightcolumn, _leftcolumn]],
                     warnings = _warnings,
                     notifiers = [])
)
