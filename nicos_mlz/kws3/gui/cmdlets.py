#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Commandlets for KWS-3."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.cmdlets import Cmdlet, register
from nicos.guisupport.qt import QListWidgetItem, Qt
from nicos.utils import findResource, num_sort

from nicos_mlz.kws1.gui.cmdlets import MeasureTable as KWS1MeasureTable
from nicos_mlz.kws1.gui.measdialogs import MeasDef as KWS1MeasDef
from nicos_mlz.kws1.gui.measelement import ChoiceElement, Chopper, MeasTime, \
    Selector


class Detector(ChoiceElement):
    CACHE_KEY = 'detector/values'
    LABEL = 'Detector'


class Resolution(ChoiceElement):
    CACHE_KEY = 'resolution/mapping'
    SORT_KEY = lambda self, x: num_sort(x)
    LABEL = 'Resolution'


class SamplePos(ChoiceElement):
    CACHE_KEY = 'sample_pos/presets'
    SORT_KEY = lambda self, x: num_sort(x)
    LABEL = 'Sample position'


class Beamstop(ChoiceElement):
    LABEL = 'Beamstop'
    VALUES = ['out', 'in']


class Polarizer(ChoiceElement):
    # CACHE_KEY = 'polarizer/mapping'
    # SORT_KEY = lambda self, x: num_sort(x)
    LABEL = 'Polarizer'
    VALUES = ['out', 'up', 'down']


class MeasDef(KWS1MeasDef):

    def getElements(self):
        elements = [
            ('selector', Selector),
            ('resolution', Resolution),
            ('sample_pos', SamplePos),
            ('beamstop', Beamstop),
            ('detector', Detector),
            ('polarizer', Polarizer),
        ]
        if not self.rtmode:
            elements.append(('chopper', Chopper))
            elements.append(('time', MeasTime))
        return elements


class MeasureTable(KWS1MeasureTable):

    meas_def_class = MeasDef

    def __init__(self, parent, client):
        KWS1MeasureTable.__init__(self, parent, client)
        self.rtBox.hide()
        self.rtConfBtn.hide()


register(MeasureTable)


class RestoreState(Cmdlet):

    name = 'Device state as script'
    category = 'Other'

    def __init__(self, parent, client):
        Cmdlet.__init__(self, parent, client,
                        findResource('nicos_mlz/kws3/gui/restore.ui'))
        for devname in self._getDeviceList():
            item = QListWidgetItem(devname, self.devList)
            item.setCheckState(Qt.Unchecked)
        # self.devList.

    def generate(self, mode):
        entries = []
        for i in range(self.devList.count()):
            if self.devList.item(i).checkState() == Qt.Checked:
                dev = self.devList.item(i).text()
                value = self.client.getDeviceValue(dev)
                if value is not None:
                    entries.append((self._getDeviceRepr(dev), value))
        if mode == 'simple':
            return 'maw ' + ''.join(' %s %r' % e for e in entries)
        else:
            return 'maw(\n' + \
                ''.join('    %s, %r,\n' % e for e in entries) + ')'


register(RestoreState)
