#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

# from math import sin, cos, pi

from nicos.guisupport.widget import NicosWidget, PropDef

from PyQt4.QtGui import QPainter, QWidget, QColor, QBrush, QPen, QPolygonF
from PyQt4.QtCore import Qt, QSize, QPointF
# , QPoint

from nicos.core.status import BUSY, OK, ERROR, NOTREACHED
from nicos.utils import readonlylist

_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
_red = QBrush(QColor('#FF3333'))
_nobrush = QBrush()

statusbrush = {
    BUSY: _yellow,
    ERROR: _red,
    NOTREACHED: _red,
    OK: _white,
}

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

    def __init__(self, parent, designMode=False):
        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

        # default values (used when no such devices are configured)
        self.values = {
            'nok0': 0,
            'nok1': 0,
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
            'nok1': OK,
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

    properties = {
        'nok0dev':   PropDef(str, ''),
        'nok1dev':   PropDef(str, ''),
        'nok2dev':   PropDef(str, ''),
        'nok3dev':   PropDef(str, ''),
        'nok4dev':   PropDef(str, ''),
        'nok5adev':  PropDef(str, ''),
        'nok5bdev':  PropDef(str, ''),
        'nok6dev':   PropDef(str, ''),
        'nok7dev':   PropDef(str, ''),
        'nok8dev':   PropDef(str, ''),
        'height':    PropDef(int, 30),
        'width':     PropDef(int, 40),
    }

    def registerKeys(self):
        for dev in ['nok0', 'nok1', 'nok2', 'nok3', 'nok4', 'nok5a', 'nok5b',
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
        beam = QPolygonF([QPointF(4, 5), ])
        i = 0
        for k in ['nok0', 'nok1', 'nok2', 'nok3', 'nok4', 'nok5a', 'nok5b',
                  'nok6', 'nok7', 'nok8']:
            v = self.values[k]
            if isinstance(v, tuple) or isinstance(v, readonlylist):
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
