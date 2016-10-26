#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

"""TAS specific display widgets."""

from math import cos, pi, sin

from nicos.guisupport.widget import NicosWidget, PropDef

from PyQt4.QtGui import QPainter, QWidget, QColor, QBrush, QPen, QPolygonF
from PyQt4.QtCore import Qt, QSize, QPointF, QPoint

from nicos.core.status import BUSY, OK, ERROR, NOTREACHED, WARN

_yellow = QBrush(QColor('yellow'))
_white = QBrush(QColor('white'))
_red = QBrush(QColor('#FF3333'))
_orange = QBrush(QColor('#FF9900'))
_nobrush = QBrush()

statusbrush = {
    BUSY: _yellow,
    ERROR: _red,
    WARN: _orange,
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

# Definitions like in C
pi_2 = pi / 2
pi_4 = pi / 4

# Conversion factor degree to radian
deg2rad = pi / 180.

monoradius = 40
sampleradius = 20
anaradius = 30
detradius = 20
halowidth = 20


class TasWidget(NicosWidget, QWidget):
    """Display of the TAS table configuration."""

    designer_description = __doc__

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
        'mthdev':    PropDef(str, '', 'Monochromator rocking angle device'),
        'mttdev':    PropDef(str, '', 'Monochromator scattering angle device'),
        'sthdev':    PropDef(str, '', 'Sample rotation device'),
        'sttdev':    PropDef(str, '', 'Sample scattering angle device'),
        'athdev':    PropDef(str, '', 'Analyzer rocking angle device'),
        'attdev':    PropDef(str, '', 'Analyzer scattering angle device'),
        'Lmsdev':    PropDef(str, '', 'Distance monochromator->sample device'),
        'Lsadev':    PropDef(str, '', 'Distance sample->analyzer device'),
        'Laddev':    PropDef(str, '', 'Distance analyzer->detector device'),
        'height':    PropDef(int, 30, 'Widget height in characters'),
        'width':     PropDef(int, 40, 'Widget width in characters'),
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
        s = self.size()
        w, h = s.width(), s.height()
        # calculate the maximum length if all elements in a line
        maxL = self.values['Lms'] + self.values['Lsa'] + self.values['Lad']
        # add the size of the Monochromator and detector
        scale = min((w / 2 - anaradius) / float(maxL),
                    (h - monoradius - anaradius) / float(maxL))

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setPen(QColor('black'))
        painter.setBrush(_white)
        painter.drawRect(0, 0, w, h)

        # determine positions

        # incoming beam
        if self.values['mth'] < 0:
            bx, by = 3, h - (2 + monoradius)
        else:
            bx, by = 3, 2 + monoradius
        # monochromator
        mx, my = w / 2., by

        # sample
        L = self.values['Lms'] * scale  # length is in mm -- scale down a bit
        mttangle = self.values['mtt'] * deg2rad
        mttangle_t = self.targets['mtt'] * deg2rad
        if self.values['mth'] < 0:
            mttangle = -mttangle
            mttangle_t = -mttangle_t

        sx, sy = mx + L * cos(mttangle), my - L * sin(mttangle)
        sx_t, sy_t = mx + L * cos(mttangle_t), my - L * sin(mttangle_t)

        # analyzer
        L = self.values['Lsa'] * scale  # length is in mm -- scale down a bit
        sttangle = self.values['stt'] * deg2rad
        sttangle_t = self.targets['stt'] * deg2rad
        if self.values['sth'] < 0:
            sttangle = mttangle - sttangle
            sttangle_t = mttangle_t - sttangle_t
        else:
            sttangle = mttangle + sttangle
            sttangle_t = mttangle_t + sttangle_t
        ax, ay = sx + L * cos(sttangle), sy - L * sin(sttangle)
        ax_t, ay_t = sx_t + L * cos(sttangle_t), sy_t - L * sin(sttangle_t)

        # detector
        L = self.values['Lad'] * scale  # length is in mm -- scale down a bit
        attangle = self.values['att'] * deg2rad
        attangle_t = self.targets['att'] * deg2rad
        if self.values['ath'] < 0:
            attangle = sttangle - attangle
            attangle_t = sttangle_t - attangle_t
        else:
            attangle = sttangle + attangle
            attangle_t = sttangle_t + attangle_t

        dx, dy = ax + L * cos(attangle), ay - L * sin(attangle)
        dx_t, dy_t = ax_t + L * cos(attangle_t), ay_t - L * sin(attangle_t)

        # draw table "halos"
        painter.setPen(nopen)
        if self.status['mth'] != OK:
            painter.setBrush(statusbrush[self.status['mth']])
            painter.drawEllipse(QPoint(mx, my), monoradius + halowidth,
                                monoradius + halowidth)
        elif self.status['mtt'] != OK:
            painter.setBrush(statusbrush[self.status['mtt']])
            painter.drawEllipse(QPoint(mx, my), monoradius + halowidth,
                                monoradius + halowidth)
        if self.status['sth'] != OK:
            painter.setBrush(statusbrush[self.status['sth']])
            painter.drawEllipse(QPoint(sx, sy), sampleradius + halowidth,
                                sampleradius + halowidth)
        elif self.status['stt'] != OK:
            painter.setBrush(statusbrush[self.status['stt']])
            painter.drawEllipse(QPoint(sx, sy), sampleradius + halowidth,
                                sampleradius + halowidth)
        if self.status['ath'] != OK:
            painter.setBrush(statusbrush[self.status['ath']])
            painter.drawEllipse(QPoint(ax, ay), anaradius + halowidth,
                                anaradius + halowidth)
        elif self.status['att'] != OK:
            painter.setBrush(statusbrush[self.status['att']])
            painter.drawEllipse(QPoint(ax, ay), anaradius + halowidth, anaradius
                               + halowidth)

        # draw table targets
        painter.setPen(targetpen)
        painter.setBrush(_nobrush)
        painter.drawEllipse(QPoint(sx_t, sy_t), sampleradius - .5,
                            sampleradius - .5)
        painter.drawEllipse(QPoint(ax_t, ay_t), anaradius - .5, anaradius - .5)
        painter.drawEllipse(QPoint(dx_t, dy_t), detradius - .5, detradius - .5)

        # draw the tables
        painter.setPen(defaultpen)
        painter.setBrush(monotablebrush)
        painter.drawEllipse(QPoint(mx, my), monoradius, monoradius)
        painter.setBrush(sampletablebrush)
        painter.drawEllipse(QPoint(sx, sy), sampleradius, sampleradius)
        painter.setBrush(anatablebrush)
        painter.drawEllipse(QPoint(ax, ay), anaradius, anaradius)
        painter.setBrush(dettablebrush)
        painter.drawEllipse(QPoint(dx, dy), detradius, detradius)
        painter.setBrush(_white)
        painter.setPen(nopen)
        painter.drawEllipse(QPoint(mx, my), monoradius / 2, monoradius / 2)
        # painter.drawEllipse(QPoint(sx, sy), 20, 20)
        painter.drawEllipse(QPoint(ax, ay), anaradius / 2, anaradius / 2)
        # painter.drawEllipse(QPoint(dx, dy), 20, 20)

        beam = QPolygonF([
            QPointF(bx, by), QPointF(mx, my), QPointF(sx, sy),
            QPointF(ax, ay), QPointF(dx, dy)])
        painter.setPen(beambackgroundpen)
        painter.drawPolyline(beam)

        # draw mono crystals
        painter.setPen(monopen)
        mthangle = -self.values['mth'] * deg2rad
        painter.drawLine(mx + 10 * cos(mthangle), my - 10 * sin(mthangle),
                         mx - 10 * cos(mthangle), my + 10 * sin(mthangle))

        # draw ana crystals
        athangle = -self.values['ath'] * deg2rad
        alpha = athangle + sttangle
        # TODO if the angle is too small then it could be that the ath value
        # must be turned by 90 deg (PANDA: chair setup) ??
        if attangle < 0 and alpha < attangle:
            alpha += pi_2
        painter.drawLine(ax + 10 * cos(alpha), ay - 10 * sin(alpha),
                         ax - 10 * cos(alpha), ay + 10 * sin(alpha))

        # draw sample
        painter.setPen(samplepen)
        painter.setBrush(samplebrush)
        sthangle = self.values['sth'] * deg2rad
        alpha = sthangle + mttangle + pi_4
        # painter.drawRect(sx - 5, sy - 5, 10, 10)
        sz = 10
        painter.drawPolygon(QPolygonF([
            QPointF(sx + sz * cos(alpha), sy - sz * sin(alpha)),
            QPointF(sx + sz * cos(alpha + pi_2), sy - sz * sin(alpha + pi_2)),
            QPointF(sx - sz * cos(alpha), sy + sz * sin(alpha)),
            QPointF(sx - sz * cos(alpha + pi_2), sy + sz * sin(alpha + pi_2)),
            QPointF(sx + sz * cos(alpha), sy - sz * sin(alpha))]))

        painter.setPen(samplecoordpen)
        sr = sampleradius
        for angle in [alpha - pi_4, alpha - 3 * pi_4]:
            painter.drawLine(sx - sr * cos(angle), sy + sr * sin(angle),
                             sx + sr * cos(angle), sy - sr * sin(angle))

        # draw detector
        painter.setPen(monopen)
        painter.setBrush(_white)
        painter.drawEllipse(QPoint(dx, dy), 4, 4)

        # draw beam
        painter.setPen(beampen)
        painter.drawPolyline(beam)
