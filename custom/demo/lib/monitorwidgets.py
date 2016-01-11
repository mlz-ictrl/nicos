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
#
# *****************************************************************************

"""vtas widget"""

from math import sin, cos, pi

from PyQt4.QtGui import QPainter, QWidget, QColor, QBrush, QPen, QPolygonF
from PyQt4.QtCore import Qt, QSize, QPointF, QPoint

from nicos.core.status import BUSY, OK, ERROR, NOTREACHED
from nicos.guisupport.widget import NicosWidget, PropDef

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


class VTas(NicosWidget, QWidget):

    designer_description = 'Display of the TAS table configuration'

    def __init__(self, parent, designMode=False):
        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

        # default values (used when no such devices are configured)
        self.values = {
            'mth': -45,
            'mtt': -90,
            'sth': 30,
            'stt': 60,
            'ath': -45,
            'att': -90,
            'Lms': 1000,
            'Lsa': 580,
            'Lad': 400,
        }
        self.targets = self.values.copy()
        self.status = {
            'mth': OK,
            'mtt': OK,
            'sth': OK,
            'stt': OK,
            'ath': OK,
            'att': OK,
        }
        self._keymap = {}
        self._statuskeymap = {}
        self._targetkeymap = {}

    properties = {
        'mthdev':    PropDef(str, ''),
        'mttdev':    PropDef(str, ''),
        'sthdev':    PropDef(str, ''),
        'sttdev':    PropDef(str, ''),
        'athdev':    PropDef(str, ''),
        'attdev':    PropDef(str, ''),
        'Lmsdev':    PropDef(str, ''),
        'Lsadev':    PropDef(str, ''),
        'Laddev':    PropDef(str, ''),
        'height':    PropDef(int, 30),
        'width':     PropDef(int, 40),
    }

    def registerKeys(self):
        for dev in ['mth', 'mtt', 'sth', 'stt', 'ath', 'att', 'Lms', 'Lsa',
                    'Lad']:
            devname = str(self.props[dev+'dev'])
            if devname:
                k1 = self._source.register(self, devname + '/value')
                self._keymap[k1] = dev
                k2 = self._source.register(self, devname + '/status')
                self._statuskeymap[k2] = dev
                k3 = self._source.register(self, devname + '/target')
                self._targetkeymap[k3] = dev

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

    def paintEvent(self, event):
        w, h = self.width * self._scale, self.height * self._scale
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QColor('black'))
        painter.setBrush(_white)
        painter.drawRect(1, 1, w, h)

        # determine positions

        # incoming beam
        if self.values['mth'] < 0:
            bx, by = 4, 50
        else:
            bx, by = 4, h + 2 - 50
        # monochromator
        mx, my = w/2.5, by
        # sample
        L = self.values['Lms'] / 10.  # length is in mm -- scale down a bit
        mttangle = self.values['mtt'] * pi/180.
        sx, sy = mx + L*cos(mttangle), my - L*sin(mttangle)
        mttangle_t = self.targets['mtt'] * pi/180.
        sx_t, sy_t = mx + L*cos(mttangle_t), my - L*sin(mttangle_t)
        # analyzer
        L = self.values['Lsa'] / 10.  # length is in mm -- scale down a bit
        sttangle = self.values['stt'] * pi/180.
        ax, ay = sx + L * cos(sttangle + mttangle), sy - L * sin(sttangle +
                                                                 mttangle)
        sttangle_t = self.targets['stt'] * pi/180.
        ax_t, ay_t = sx_t + L*cos(sttangle_t + mttangle_t), \
            sy_t - L*sin(sttangle_t + mttangle_t)
        # detector
        L = self.values['Lad'] / 10.  # length is in mm -- scale down a bit
        attangle = self.values['att'] * pi/180.
        dx, dy = ax + L*cos(attangle + sttangle + mttangle), \
            ay - L*sin(attangle + sttangle + mttangle)
        attangle_t = self.targets['att'] * pi/180.
        dx_t, dy_t = ax_t + L*cos(attangle_t + sttangle_t + mttangle_t), \
            ay_t - L*sin(attangle_t + sttangle_t + mttangle_t)

        # draw table "halos"
        painter.setPen(nopen)
        if self.status['mth'] != OK:
            painter.setBrush(statusbrush[self.status['mth']])
            painter.drawEllipse(QPoint(mx, my), 60, 60)
        elif self.status['mtt'] != OK:
            painter.setBrush(statusbrush[self.status['mtt']])
            painter.drawEllipse(QPoint(mx, my), 60, 60)
        if self.status['sth'] != OK:
            painter.setBrush(statusbrush[self.status['sth']])
            painter.drawEllipse(QPoint(sx, sy), 50, 50)
        elif self.status['stt'] != OK:
            painter.setBrush(statusbrush[self.status['stt']])
            painter.drawEllipse(QPoint(sx, sy), 50, 50)
        if self.status['ath'] != OK:
            painter.setBrush(statusbrush[self.status['ath']])
            painter.drawEllipse(QPoint(ax, ay), 50, 50)
        elif self.status['att'] != OK:
            painter.setBrush(statusbrush[self.status['att']])
            painter.drawEllipse(QPoint(ax, ay), 50, 50)

        # draw table targets
        painter.setPen(targetpen)
        painter.setBrush(_nobrush)
        painter.drawEllipse(QPoint(sx_t, sy_t), 29.5, 29.5)
        painter.drawEllipse(QPoint(ax_t, ay_t), 29.5, 29.5)
        painter.drawEllipse(QPoint(dx_t, dy_t), 19.5, 19.5)

        # draw the tables
        painter.setPen(defaultpen)
        painter.setBrush(monotablebrush)
        painter.drawEllipse(QPoint(mx, my), 40, 40)
        painter.setBrush(sampletablebrush)
        painter.drawEllipse(QPoint(sx, sy), 30, 30)
        painter.setBrush(anatablebrush)
        painter.drawEllipse(QPoint(ax, ay), 30, 30)
        painter.setBrush(dettablebrush)
        painter.drawEllipse(QPoint(dx, dy), 20, 20)
        painter.setBrush(_white)
        painter.setPen(nopen)
        painter.drawEllipse(QPoint(mx, my), 20, 20)
        # painter.drawEllipse(QPoint(sx, sy), 20, 20)
        painter.drawEllipse(QPoint(ax, ay), 15, 15)
        # painter.drawEllipse(QPoint(dx, dy), 20, 20)

        beam = QPolygonF([
            QPointF(bx, by), QPointF(mx, my), QPointF(sx, sy),
            QPointF(ax, ay), QPointF(dx, dy)])
        painter.setPen(beambackgroundpen)
        painter.drawPolyline(beam)

        # draw mono crystals
        painter.setPen(monopen)
        mthangle = self.values['mth'] * pi/180.
        painter.drawLine(mx - 10*cos(mthangle), my + 10*sin(mthangle),
                         mx + 10*cos(mthangle), my - 10*sin(mthangle))
        athangle = self.values['ath'] * pi/180.
        alpha = athangle + sttangle + mttangle
        painter.drawLine(ax - 10*cos(alpha), ay + 10*sin(alpha),
                         ax + 10*cos(alpha), ay - 10*sin(alpha))

        # draw sample
        painter.setPen(samplepen)
        painter.setBrush(samplebrush)
        sthangle = self.values['sth'] * pi/180.
        alpha = sthangle + mttangle + pi/4.
        # painter.drawRect(sx - 5, sy - 5, 10, 10)
        sz = 10
        painter.drawPolygon(QPolygonF([
            QPointF(sx + sz*cos(alpha), sy - sz*sin(alpha)),
            QPointF(sx + sz*cos(alpha+pi/2), sy - sz*sin(alpha+pi/2)),
            QPointF(sx + sz*cos(alpha+pi), sy - sz*sin(alpha+pi)),
            QPointF(sx + sz*cos(alpha+3*pi/2), sy - sz*sin(alpha+3*pi/2)),
            QPointF(sx + sz*cos(alpha), sy - sz*sin(alpha))]))
        painter.setPen(samplecoordpen)
        painter.drawLine(sx - 3*sz*cos(alpha-pi/4), sy + 3*sz*sin(alpha-pi/4),
                         sx + 3*sz*cos(alpha-pi/4), sy - 3*sz*sin(alpha-pi/4))
        painter.drawLine(sx - 3*sz*cos(alpha-3*pi/4), sy + 3*sz*sin(alpha-3*pi/4),
                         sx + 3*sz*cos(alpha-3*pi/4), sy - 3*sz*sin(alpha-3*pi/4))

        # draw detector
        painter.setPen(monopen)
        painter.setBrush(_white)
        painter.drawEllipse(QPoint(dx, dy), 4, 4)

        # draw beam
        painter.setPen(beampen)
        painter.drawPolyline(beam)
