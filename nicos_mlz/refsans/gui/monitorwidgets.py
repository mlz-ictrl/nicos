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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from nicos.core.status import OK
from nicos.guisupport.qt import QBrush, QColor, QPainter, QPen, QPointF, \
    QPolygonF, QSize, Qt, QWidget
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.utils import readonlylist

from nicos_mlz.refsans.gui.refsansview import RefsansView
from nicos_mlz.refsans.gui.timedistancewidget import TimeDistanceWidget
from nicos_mlz.sans1.gui.monitorwidgets import CollimatorTable

_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
_red = QBrush(QColor('#FF3333'))
_nobrush = QBrush()

nopen = QPen(QColor('white'))
defaultpen = QPen(QColor('black'))
beampen = QPen(QColor('blue'))
monopen = QPen(QColor('black'))
monopen.setWidth(3)
beambackgroundpen = QPen(QColor('white'))
beambackgroundpen.setWidth(4)
samplepen = QPen(QColor('#006600'))
samplepen.setWidth(2)
samplebrush = QBrush(QColor('#006600'))
samplecoordpen = QPen(QColor('#666666'))
targetpen = QPen(QColor('black'))
targetpen.setStyle(Qt.DashLine)

monotablebrush = QBrush(QColor('#6666ff'))
sampletablebrush = QBrush(QColor('#66ff66'))
anatablebrush = QBrush(QColor('#6666ff'))
dettablebrush = QBrush(QColor('#ff66ff'))


class VRefsans(NicosWidget, QWidget):

    designer_description = 'Display of the REFSANS NOK configuration'

    nok0dev = PropDef('nok0dev', str, '', 'NOK 0 device')
    shutter_gammadev = PropDef('shutter_gammadev', str, '', 'NOK 1 device')
    nok2dev = PropDef('nok2dev', str, '', 'NOK 2 device')
    nok3dev = PropDef('nok3dev', str, '', 'NOK 3 device')
    nok4dev = PropDef('nok4dev', str, '', 'NOK 4 device')
    nok5adev = PropDef('nok5adev', str, '', 'NOK 5a device')
    nok5bdev = PropDef('nok5bdev', str, '', 'NOK 5b device')
    nok6dev = PropDef('nok6dev', str, '', 'NOK 6 device')
    nok7dev = PropDef('nok7dev', str, '', 'NOK 7 device')
    nok8dev = PropDef('nok8dev', str, '', 'NOK 8 device')
    height = PropDef('height', int, 30, 'Widget height in characters')
    width = PropDef('width', int, 40, 'Widget width in characters')

    def __init__(self, parent, designMode=False):
        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

        # default values (used when no such devices are configured)
        self.values = {
            'nok0': 0,
            'shutter_gamma': 0,
            'nok2': (0, 0),
            'nok3': (0, 0),
            'nok4': (0, 0),
            'nok5a': (0, 0),
            'nok5b': (0, 0),
            'nok6': (0, 0),
            'nok7': (0, 0),
            'nok8': (0, 0),
        }
        self.targets = self.values.copy()
        self.status = {
            'nok0': OK,
            'shutter_gamma': OK,
            'nok2': OK,
            'nok3': OK,
            'nok4': OK,
            'nok5a': OK,
            'nok5b': OK,
            'nok6': OK,
            'nok7': OK,
            'nok8': OK,
        }
        self._keymap = {}
        self._statuskeymap = {}
        self._targetkeymap = {}
        self._lengthkeymap = {}
        self._length = [0, 100, 300, 600, 1000, 1720, 1720, 1720, 1190, 880]
        self._fulllength = sum(self._length)

    def registerKeys(self):
        for dev in ['nok0', 'shutter_gamma', 'nok2', 'nok3', 'nok4', 'nok5a', 'nok5b',
                    'nok6', 'nok7', 'nok8']:
            devname = str(self.props[dev + 'dev'])
            if devname:
                k1 = self._source.register(self, devname + '/value')
                self._keymap[k1] = dev
                k2 = self._source.register(self, devname + '/status')
                self._statuskeymap[k2] = dev
                k3 = self._source.register(self, devname + '/target')
                self._targetkeymap[k3] = dev
                k4 = self._source.register(self, devname + '/length')
                self._lengthkeymap[k4] = dev

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
        elif key in self._lengthkeymap and not expired:
            self.targets[self._lengthkeymap[key]] = value
            self.update()

    def sizeHint(self):
        return QSize(self.props['width'] * self._scale + 2,
                     self.props['height'] * self._scale + 2)

    def _calculatePoint(self, ind, x, y):
        w, h = self.width * self._scale, self.height * self._scale
        x = sum(self._length[0:ind])
        mx = 4 + w * x / self._fulllength
        my = 5 + h * y / 400
        return (mx, my)

    def paintEvent(self, event):
        w, h = self.width * self._scale, self.height * self._scale
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QColor('black'))
        painter.setBrush(_white)
        painter.drawRect(1, 1, w, h)

        # determine positions
        beam = QPolygonF([QPointF(4, 5)])
        i = 0
        for k in ['nok0', 'shutter_gamma', 'nok2', 'nok3', 'nok4', 'nok5a', 'nok5b',
                  'nok6', 'nok7', 'nok8']:
            v = self.values[k]
            if isinstance(v, (tuple, readonlylist)):
                x, y = v  # pylint: disable=W0633
            elif isinstance(v, int):
                x, y = 0, v
            else:
                raise Exception('%r' % type(v))
            p = self._calculatePoint(i, x, y)
            beam.append(QPointF(p[0], p[1]))
            i += 1
        x, y = self.values['nok8']
        p = self._calculatePoint(i + 1, x, y)

        painter.setPen(beambackgroundpen)
        painter.drawPolyline(beam)

        # draw beam
        painter.setPen(beampen)
        painter.drawPolyline(beam)


class BeamPosition(CollimatorTable):

    designer_description = 'REFSANS NOK and slit table'

    key = PropDef('key', str, '', 'Cache key to display')

    def __init__(self, parent, designMode=False):
        CollimatorTable.__init__(self, parent, designMode)

    def registerKeys(self):
        self.registerKey(self.props['key'])
        CollimatorTable.registerKeys(self)


class TimeDistance(NicosWidget, TimeDistanceWidget):

    designer_description = 'REFSANS time distance diagram display'

    chopper1 = PropDef('chopper1', str, 'chopper1', 'Chopper 1 device')
    chopper2 = PropDef('chopper2', str, 'chopper2', 'Chopper 2 device')
    chopper3 = PropDef('chopper3', str, 'chopper3', 'Chopper 3 device')
    chopper4 = PropDef('chopper4', str, 'chopper4', 'Chopper 4 device')
    chopper5 = PropDef('chopper5', str, 'chopper5', 'Chopper 5 device')
    chopper6 = PropDef('chopper6', str, 'chopper6', 'Chopper 6 device')

    disc2_pos = PropDef('disc2_pos', str, 'disc2_pos',
                        'Position of disc2 translation')

    periods = PropDef('periods', int, 2,
                      'Number of periods to display')
    D = PropDef('D', float, 22.8, 'Beamline length')

    fp = PropDef('flightpath', str, 'real_flight_path', 'Flight path device')

    def __init__(self, parent, designMode=False):
        TimeDistanceWidget.__init__(self, parent)
        NicosWidget.__init__(self)
        self._speed = 0
        self._phases = [0] * 6
        self._disk2_pos = 5
        self._fp = 0

    def registerKeys(self):
        # chopperspeed, chopper phases,a
        for dev in ['chopper1', 'disc2_pos']:
            devname = self.props.get(dev)
            if devname:
                self._source.register(self, devname + '/value')

        for dev in ['chopper1', 'chopper2', 'chopper3', 'chopper4', 'chopper5',
                    'chopper6']:
            devname = self.props.get(dev)
            if devname:
                self._source.register(self, devname + '/phase')

        devname = self.props.get('chopper2')
        if devname:
            self._source.register(self, devname + '/pos')

        devname = self.props.get('fp')
        if devname:
            self._source.register(self, devname + '/value')

    def on_keyChange(self, key, value, time, expired):
        _, dev, param = key.split('/')
        devs = [key for key, d in self.props.items() if d == dev]
        if devs:
            devname = devs[0]
            if param == 'value':
                if value is None:
                    return
                if devname == 'chopper1':
                    self._speed = int(value)
                elif devname == 'disc2_pos':
                    self._disk2_pos = int(value)
                elif devname == 'fp':
                    self._fp = int(value)
            elif param == 'phase':
                if devname.startswith('chopper'):
                    if value is not None:
                        index = int(devname[-1]) - 1
                        self._phases[index] = float(value)
            elif param == 'pos' and devname == 'chopper2':
                if value is not None:
                    self._disk2_pos = int(value)
            self.plot(self._speed, self._phases, self.props['periods'],
                      self._disk2_pos, self.props['D'], self._fp)


class RefsansWidget(NicosWidget, RefsansView):

    tubeangle = PropDef('tubeangle', str, '',
                        'Inclination of the tube')
    pivot = PropDef('pivot', str, '',
                    'Mounting point of the tube (pivot)')
    detpos = PropDef('detpos', str, '',
                     'Detector position inside tube')

    def __init__(self, parent):
        RefsansView.__init__(self, parent=parent)
        NicosWidget.__init__(self)

        self._keymap = {}
        self._statuskeymap = {}
        self._targetkeymap = {}

    def registerKeys(self):
        for dev in ['tubeangle', 'pivot', 'detpos']:
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
