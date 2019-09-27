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
"""Classes to display the TAS instruments."""

from __future__ import absolute_import, division, print_function

from nicos.guisupport.qt import QBrush, QColor, QGraphicsLineItem, \
    QGraphicsRectItem, QPen, QPointF, QRectF

from .table import TableBase


class Sample(TableBase):
    """Display a sample on a table."""

    _pencolor = None

    def __init__(self, x, y, size=20, parent=None, scene=None):
        if parent:
            self._color = parent._color
        TableBase.__init__(self, x, y, size, parent, scene)
        if not self._pencolor:
            self._pencolor = QColor('#666666')
        self._pen = QPen(self._pencolor, 1)
        self._pen.setBrush(QBrush(self._pencolor))
        sz = size / 3
        self._polygon = QGraphicsRectItem(
            QRectF(-QPointF(sz, sz), QPointF(sz, sz)), self)
        self._polygon.setBrush(QBrush(self._pencolor))
        self._l1 = QGraphicsLineItem(-size, 0, size, 0, self)
        self._l1.setPen(self._pen)
        self._l2 = QGraphicsLineItem(0, -size, 0, size, self)
        self._l2.setPen(self._pen)
