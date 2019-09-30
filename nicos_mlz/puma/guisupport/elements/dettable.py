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
"""Classes to display the PUMA multi detector devices."""

from __future__ import absolute_import, division, print_function

from nicos.guisupport.elements import Detector
from nicos.guisupport.elements.halo import Halo
from nicos.guisupport.qt import QColor, QGraphicsPathItem, QPainterPath, \
    QPen, QPointF, QPolygonF


class DetectorTable(Detector):
    """Class to display the detector inside the multi detector housing."""

    _halowidth = 6

    def __init__(self, size, radius, parent=None, scene=None):
        Detector.__init__(self, size, radius, parent, scene)
        self._halo = Halo(0, 0, size, self._halowidth, self, scene)


class DetectorGuide(QGraphicsPathItem):

    def __init__(self, parent=None, scene=None):
        QGraphicsPathItem.__init__(self, parent)
        self.setPath(self.shape())
        if not parent and scene:
            scene.addItem(self)
        self.setPen(QPen(QColor('darkblue')))

    def shape(self):
        path = QPainterPath()
        y0, y1, _l = 12, 2, 250
        path.addPolygon(QPolygonF([QPointF(0, -y0), QPointF(0, y0),
                                   QPointF(_l, y0), QPointF(_l, -y1)]))
        path.closeSubpath()
        return path
