#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""Classes to display the PUMA Multi analyzer."""

from __future__ import absolute_import, division, print_function

from nicos.guisupport.qt import QSize
from nicos.guisupport.widget import NicosWidget, PropDef

from .multiview import MultiAnalyzerView


class MultiAnalyzerWidget(NicosWidget, MultiAnalyzerView):

    rd1 = PropDef('rd1', str, 'rd1', 'Detector 1 position')
    rd2 = PropDef('rd2', str, 'rd2', 'Detector 2 position')
    rd3 = PropDef('rd3', str, 'rd3', 'Detector 3 position')
    rd4 = PropDef('rd4', str, 'rd4', 'Detector 4 position')
    rd5 = PropDef('rd5', str, 'rd5', 'Detector 5 position')
    rd6 = PropDef('rd6', str, 'rd6', 'Detector 6 position')
    rd7 = PropDef('rd7', str, 'rd7', 'Detector 7 position')
    rd8 = PropDef('rd8', str, 'rd8', 'Detector 8 position')
    rd9 = PropDef('rd9', str, 'rd9', 'Detector 9 position')
    rd10 = PropDef('rd10', str, 'rd10', 'Detector 10 position')
    rd11 = PropDef('rd11', str, 'rd11', 'Detector 11 position')

    rg1 = PropDef('rg1', str, 'rg1', 'Guide 1 rotation')
    rg2 = PropDef('rg2', str, 'rg2', 'Guide 2 rotation')
    rg3 = PropDef('rg3', str, 'rg3', 'Guide 3 rotation')
    rg4 = PropDef('rg4', str, 'rg4', 'Guide 4 rotation')
    rg5 = PropDef('rg5', str, 'rg5', 'Guide 5 rotation')
    rg6 = PropDef('rg6', str, 'rg6', 'Guide 6 rotation')
    rg7 = PropDef('rg7', str, 'rg7', 'Guide 7 rotation')
    rg8 = PropDef('rg8', str, 'rg8', 'Guide 8 rotation')
    rg9 = PropDef('rg9', str, 'rg9', 'Guide 9 rotation')
    rg10 = PropDef('rg10', str, 'rg10', 'Guide 10 rotation')
    rg11 = PropDef('rg11', str, 'rg11', 'Guide 11 rotation')

    ra1 = PropDef('ra1', str, 'ra1', 'Monochromator crystal 1 rotation')
    ra2 = PropDef('ra2', str, 'ra2', 'Monochromator crystal 2 rotation')
    ra3 = PropDef('ra3', str, 'ra3', 'Monochromator crystal 3 rotation')
    ra4 = PropDef('ra4', str, 'ra4', 'Monochromator crystal 4 rotation')
    ra5 = PropDef('ra5', str, 'ra5', 'Monochromator crystal 5 rotation')
    ra6 = PropDef('ra6', str, 'ra6', 'Monochromator crystal 6 rotation')
    ra7 = PropDef('ra7', str, 'ra7', 'Monochromator crystal 7 rotation')
    ra8 = PropDef('ra8', str, 'ra8', 'Monochromator crystal 8 rotation')
    ra9 = PropDef('ra9', str, 'ra9', 'Monochromator crystal 9 rotation')
    ra10 = PropDef('ra10', str, 'ra10', 'Monochromator crystal 10 rotation')
    ra11 = PropDef('ra11', str, 'ra11', 'Monochromator crystal 11 rotation')

    ta1 = PropDef('ta1', str, 'ta1', 'Monochromator crystal 1 translation')
    ta2 = PropDef('ta2', str, 'ta2', 'Monochromator crystal 2 translation')
    ta3 = PropDef('ta3', str, 'ta3', 'Monochromator crystal 3 translation')
    ta4 = PropDef('ta4', str, 'ta4', 'Monochromator crystal 4 translation')
    ta5 = PropDef('ta5', str, 'ta5', 'Monochromator crystal 5 translation')
    ta6 = PropDef('ta6', str, 'ta6', 'Monochromator crystal 6 translation')
    ta7 = PropDef('ta7', str, 'ta7', 'Monochromator crystal 7 translation')
    ta8 = PropDef('ta8', str, 'ta8', 'Monochromator crystal 8 translation')
    ta9 = PropDef('ta9', str, 'ta9', 'Monochromator crystal 9 translation')
    ta10 = PropDef('ta10', str, 'ta10', 'Monochromator crystal 10 translation')
    ta11 = PropDef('ta11', str, 'ta11', 'Monochromator crystal 11 translation')

    cad = PropDef('cad', str, 'cad', 'CAD device')
    lsa = PropDef('lsa', str, 'lsa', 'Distance sample analyser center')

    height = PropDef('height', int, 30, 'Widget height in characters')
    width = PropDef('width', int, 40, 'Widget width in characters')

    def __init__(self, parent):
        MultiAnalyzerView.__init__(self)
        NicosWidget.__init__(self)

        self._keymap = {}
        self._statuskeymap = {}
        self._targetkeymap = {}

    def registerKeys(self):
        for dev in ['ta1', 'ta2', 'ta3', 'ta4', 'ta5', 'ta6', 'ta7', 'ta8',
                    'ta9', 'ta10', 'ta11',
                    'ra1', 'ra2', 'ra3', 'ra4', 'ra5', 'ra6', 'ra7', 'ra8',
                    'ra9', 'ra10', 'ra11',
                    'rd1', 'rd2', 'rd3', 'rd4', 'rd5', 'rd6', 'rd7', 'rd8',
                    'rd9', 'rd10', 'rd11',
                    'rg1', 'rg2', 'rg3', 'rg4', 'rg5', 'rg6', 'rg7', 'rg8',
                    'rg9', 'rg10', 'rg11',
                    'cad', 'lsa']:
            devname = self.props.get(dev)
            if devname:
                k = self._source.register(self, devname + '/value')
                self._keymap[k] = dev
                k = self._source.register(self, devname + '/status')
                self._statuskeymap[k] = dev
                k = self._source.register(self, devname + '/target')
                self._targetkeymap[k] = dev

    def on_keyChange(self, key, value, time, expired):
        if key in self._keymap and not expired:
            self.values[self._keymap[key]] = value
            self.update()
        elif key in self._statuskeymap and not expired:
            self.status[self._statuskeymap[key]] = value[0]
            self.update()
        elif key in self._targetkeymap and not expired:
            self.targets[self._targetkeymap[key]] = value
            self.update()

    def sizeHint(self):
        return QSize(self.props['width'] * self._scale + 2,
                     self.props['height'] * self._scale + 2)
