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
"""Classes to display the PUMA Multi analyzer."""

from math import atan, degrees, sqrt

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.core import status
from nicos.guisupport.elements import Beam, Sample, TableTarget
from nicos.guisupport.qt import QGraphicsEllipseItem, QGraphicsScene, \
    QGraphicsView, QPainter, QSize
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.utils import findResource

from nicos_mlz.puma.guisupport.elements import CrystalTable, DetectorBox, \
    DetectorGuide, DetectorTable, Reflex


class MultiAnalyzerView(QGraphicsView):
    """Widget to visualise the current positions of the TAS."""

    num_crystals = 11
    detradius = 762  # detector radius

    _crystals = [None] * num_crystals
    _crystals_t = [None] * num_crystals
    _inbeams = [None] * num_crystals
    _outbeams = [None] * num_crystals
    _detectors = [None] * num_crystals
    _detectors_t = [None] * num_crystals
    _reflections = [None] * num_crystals
    _guides = [None] * num_crystals
    _sample = None

    detsize = 12
    crystalsize = 10
    detopen = 62

    def __init__(self):
        scene = QGraphicsScene()
        QGraphicsView.__init__(self, scene)
        self.setRenderHints(QPainter.Antialiasing)

        self._sample = Sample(0, 0, scene=scene)

        # draw the center point of the detector circle
        scene.addItem(QGraphicsEllipseItem(-2, -2, 4, 4))

        # draw detector box
        self._detbox = DetectorBox(self.detradius, self.detopen)
        scene.addItem(self._detbox)

        # default values (used when no such devices are configured)
        self.values = {
            'rd1': -27.5,
            'rd2': -25.0,
            'rd3': -22.5,
            'rd4': -20.0,
            'rd5': -17.5,
            'rd6': -15.0,
            'rd7': -12.5,
            'rd8': -10.0,
            'rd9': -7.5,
            'rd10': -5.0,
            'rd11': -2.5,
            'rg1': 0.0,
            'rg2': 0.0,
            'rg3': 0.0,
            'rg4': 0.0,
            'rg5': 0.0,
            'rg6': 0.0,
            'rg7': 0.0,
            'rg8': 0.0,
            'rg9': 0.0,
            'rg10': 0.0,
            'rg11': 0.0,
            'ra1': -1.0,
            'ra2': -2.0,
            'ra3': -3.0,
            'ra4': -4.0,
            'ra5': -5.0,
            'ra6': -6.0,
            'ra7': -7.0,
            'ra8': -8.0,
            'ra9': -9.0,
            'ra10': -10.0,
            'ra11': -11.0,
            'ta1': 125.0,
            'ta2': 112.0,
            'ta3': 99.0,
            'ta4': 86.0,
            'ta5': 73.0,
            'ta6': 60.0,
            'ta7': 47.0,
            'ta8': 34.0,
            'ta9': 21.0,
            'ta10': 8.0,
            'ta11': -5.0,
            'cad': 0.0,
            'lsa': 910.,
        }
        self.targets = self.values.copy()
        self.status = {
            'rd1': status.OK,
            'rd2': status.OK,
            'rd3': status.OK,
            'rd4': status.OK,
            'rd5': status.OK,
            'rd6': status.OK,
            'rd7': status.OK,
            'rd8': status.OK,
            'rd9': status.OK,
            'rd10': status.OK,
            'rd11': status.OK,
            'rg1': status.OK,
            'rg2': status.OK,
            'rg3': status.OK,
            'rg4': status.OK,
            'rg5': status.OK,
            'rg6': status.OK,
            'rg7': status.OK,
            'rg8': status.OK,
            'rg9': status.OK,
            'rg10': status.OK,
            'rg11': status.OK,
            'ra1': status.OK,
            'ra2': status.OK,
            'ra3': status.OK,
            'ra4': status.OK,
            'ra5': status.OK,
            'ra6': status.OK,
            'ra7': status.OK,
            'ra8': status.OK,
            'ra9': status.OK,
            'ra10': status.OK,
            'ra11': status.OK,
            'ta1': status.OK,
            'ta2': status.OK,
            'ta3': status.OK,
            'ta4': status.OK,
            'ta5': status.OK,
            'ta6': status.OK,
            'ta7': status.OK,
            'ta8': status.OK,
            'ta9': status.OK,
            'ta10': status.OK,
            'ta11': status.OK,
            'cad': status.OK,
            'lsa': status.OK,
        }

        for i in range(self.num_crystals):
            self._detectors[i] = DetectorTable(self.detsize, self.detradius,
                                               scene=scene)
            self._guides[i] = DetectorGuide(self._detectors[i])

            self._detectors_t[i] = t = TableTarget(0, 0, self.detsize,
                                                   scene=scene)
            # move the origin to make the rotation very easy
            t.setPos(-self.detradius, 0)
            t.setTransformOriginPoint(self.detradius, 0)

            y = (self.num_crystals / 2 - i) * 20
            self._crystals[i] = CrystalTable(0, y, self.crystalsize,
                                             scene=scene)
            self._crystals_t[i] = TableTarget(0, y, self.crystalsize,
                                              scene=scene)
            self._reflections[i] = Reflex(self.detradius, self._crystals[i],
                                          self._sample, self._detectors[i],
                                          scene=scene)
            self._inbeams[i] = Beam(self._sample, self._crystals[i],
                                    scene=scene)
            self._outbeams[i] = Beam(self._crystals[i], self._reflections[i],
                                     scene=scene)
        self.update()

    def resizeEvent(self, rsevent):
        s = rsevent.size()
        w, h = s.width(), s.height()
        scale = min(w / (self.detradius + 50 + self._sample.pos().x() +
                         self._sample.boundingRect().width()),
                    h / (self.detradius + 3 * 50 + self._crystals[0].pos().y() +
                         self._crystals[0].boundingRect().height()))
        transform = self.transform()
        transform.reset()
        transform.scale(scale, scale)
        self.setTransform(transform)
        QGraphicsView.resizeEvent(self, rsevent)

    def update(self):
        self._sample.setPos(self.values['lsa'], 0)
        cadrot = -self.values.get('cad', 0)  # rotation has opposite sign
        # 16 is the angle of the left side from 0 beam
        self._detbox.setRotation(cadrot - 16)
        for i in range(self.num_crystals):
            self._detectors[i].setState(max(self.status['rd%d' % (i + 1)],
                                            self.status['rg%d' % (i + 1)]))
            self._detectors[i].setRotation(
                -(self.values['rd%d' % (i + 1)] - cadrot))
            if self.targets.get('rd%d' % (i + 1)) is not None:
                self._detectors_t[i].setRotation(
                    -(self.targets['rd%d' % (i + 1)] - cadrot))
            self._guides[i].setRotation(-self.values['rg%d' % (i + 1)])

            self._crystals[i].setState(max(self.status['ta%d' % (i + 1)],
                                           self.status['ra%d' % (i + 1)]))
            self._crystals[i].setRotation(-self.values['ra%d' % (i + 1)])
            self._crystals[i].setX(self.values['ta%d' % (i + 1)])
            if self.targets.get('ta%d' % (i + 1)) is not None:
                self._crystals_t[i].setX(self.targets.get('ta%d' % (i + 1)))
            outangle, _r = self._calculate_reflection(i)
            self._reflections[i].setRotation(outangle)
        for l in self._inbeams + self._outbeams:
            l.update()
        QGraphicsView.update(self)

    def _calculate_reflection(self, i=0):
        """Calculates the outgoing angle and the radius"""
        c = self._crystals[i]
        d = self._detectors[i]
        inangle = degrees(atan(
            (c.y() - self._sample.y()) / abs(self._sample.x() - c.x())))
        dx = d.transformOriginPoint().x() - c.x()
        dy = d.transformOriginPoint().y() - c.y()
        return inangle + 2 * c.rotation(), sqrt(dx * dx + dy * dy)


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


class MultiViewPanel(Panel):

    panelName = 'Multi analysis'
    ui = 'nicos_mlz/puma/gui/panels/multiview.ui'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource(self.ui))

        self.widgetLayout.removeWidget(self.widget)
        self.widget = MultiAnalyzerWidget(self)
        self.widgetLayout.addWidget(self.widget)

        self.widget.setClient(client)
