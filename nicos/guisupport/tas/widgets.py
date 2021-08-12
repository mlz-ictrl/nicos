#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
"""Classes to display the TAS instruments."""

from math import cos, radians, sin

from nicos.core import status
from nicos.guisupport.elements import AnaTable, Beam, DetTable, MonoTable, \
    SampleTable, TableBase, TableTarget
from nicos.guisupport.qt import QGraphicsScene, QGraphicsView, QPainter


class TasView(QGraphicsView):
    """Widget to visualise the current positions of the TAS."""

    anaradius = 30
    monoradius = 40
    sampleradius = 20
    detectorradius = 10
    _beams = []

    def __init__(self, parent=None, designMode=False):
        self.scene = QGraphicsScene(parent)
        QGraphicsView.__init__(self, self.scene, parent)
        self.setRenderHints(QPainter.Antialiasing)

        # default values (used when no such devices are configured)
        self.values = {
            'mth': -45,
            'mtt': -90,
            'sth': 30,
            'stt': 60,
            'ath': -45,
            'att': -90,
            # scale the distances
            'Lms': 1000 / 10,
            'Lsa': 580 / 10,
            'Lad': 400 / 10,
        }
        self.targets = self.values.copy()
        self.status = {
            'mth': status.OK,
            'mtt': status.OK,
            'sth': status.OK,
            'stt': status.OK,
            'ath': status.OK,
            'att': status.OK,
        }
        self._designMode = designMode

    def initUi(self):
        scene = self.scene
        self._mono = MonoTable(0., 0, self.monoradius, scene=scene)
        self._sample = SampleTable(0, 0, self.sampleradius, scene=scene)
        self._sample_t = TableTarget(0, 0, self.sampleradius, scene=scene)
        self._ana = AnaTable(0, 0, self.anaradius, scene=scene)
        self._ana_t = TableTarget(0, 0, self.anaradius, scene=scene)
        self._det = DetTable(0, 0, self.detectorradius, scene=scene)
        self._det_t = TableTarget(0, 0, self.detectorradius, scene=scene)
        self._src = TableBase(0, 0, 0, scene=scene)
        self._src_beam = Beam(self._src, self._mono, scene=scene)
        self._mono_beam = Beam(self._mono, self._sample, scene=scene)
        self._sample_beam = Beam(self._sample, self._ana, scene=scene)
        self._ana_beam = Beam(self._ana, self._det, scene=scene)
        self._beams = (self._src_beam, self._mono_beam, self._sample_beam,
                       self._ana_beam)
        if self._designMode:
            self.update()

    def resizeEvent(self, rsevent):
        s = self.size()
        w, h = s.width(), s.height()
        Lms = self.values['Lms']
        Lsa = self.values['Lsa']
        Lad = self.values['Lad']

        maxL = Lms + Lsa + Lad
        scale = min(w / (2 * (maxL + self.detectorradius)),
                    h / (maxL + self.monoradius + self.detectorradius))
        transform = self.transform()
        transform.reset()
        transform.scale(scale, scale)
        self.setTransform(transform)
        QGraphicsView.resizeEvent(self, rsevent)

    def update(self):
        Lms = self.values['Lms']
        Lsa = self.values['Lsa']
        Lad = self.values['Lad']
        maxL = Lms + Lsa + Lad
        mth = self.values['mth']

        # incoming beam
        self._src.setPos(-(maxL - 3), 0)

        # monochromator
        self._mono.setState(max(self.status['mth'], self.status['mtt']))
        self._mono.setPos(0, 0)
        self._mono.setRotation(mth)

        # sample
        mtt = self.values['mtt']
        mttangle = radians(mtt)
        mttangle_t = radians(self.targets['mtt'])
        if mth < 0:
            mttangle = -mttangle
            mttangle_t = -mttangle_t

        sx, sy = Lms * cos(mttangle), -Lms * sin(mttangle)
        sx_t, sy_t = Lms * cos(mttangle_t), -Lms * sin(mttangle_t)
        sth = self.values['sth']
        stt = self.values['stt']

        self._sample_t.setPos(sx_t, sy_t)
        self._sample.setState(max(self.status['stt'], self.status['sth']))
        self._sample.setPos(sx, sy)
        self._sample.setRotation(sth - mtt + 45.)

        # analyzer
        sttangle = radians(stt)
        sttangle_t = radians(self.targets['stt'])
        if sth < 0:
            sttangle = mttangle - sttangle
            sttangle_t = mttangle_t - sttangle_t
        else:
            sttangle = mttangle + sttangle
            sttangle_t = mttangle_t + sttangle_t
        ax, ay = sx + Lsa * cos(sttangle), sy - Lsa * sin(sttangle)
        ax_t, ay_t = sx_t + Lsa * cos(sttangle_t), sy_t - Lsa * sin(sttangle_t)
        ath = self.values['ath']

        self._ana_t.setPos(ax_t, ay_t)
        self._ana.setState(max(self.status['ath'], self.status['att']))
        self._ana.setPos(ax, ay)
        self._ana.setRotation(mtt + ath - stt)

        # detector
        att = self.values['att']
        attangle = radians(att)
        attangle_t = radians(self.targets['att'])
        if ath < 0:
            attangle = sttangle - attangle
            attangle_t = sttangle_t - attangle_t
        else:
            attangle = sttangle + attangle
            attangle_t = sttangle_t + attangle_t

        dx, dy = ax + Lad * cos(attangle), ay - Lad * sin(attangle)
        dx_t, dy_t = ax_t + Lad * cos(attangle_t), ay_t - Lad * sin(attangle_t)

        self._det_t.setPos(dx_t, dy_t)
        self._det.setState(self.status['att'])
        self._det.setPos(dx, dy)

        # This call is needed to refresh drawing of the beams after moving
        # the tables
        for b in self._beams:
            b.update()

        QGraphicsView.update(self)
