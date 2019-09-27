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

from nicos.guisupport.qt import QColor

from .crystal import Crystal
from .halo import Halo
from .table import TableBase


class MonoTable(TableBase):
    """Class to display the monochromator including shielding and crystal."""

    _color = QColor('#6666ff')

    def __init__(self, x, y, size=40, parent=None, scene=None):
        TableBase.__init__(self, x, y, size, parent, scene)
        self._halowidth = max(size / 10, 10)
        self._halo = Halo(x, y, size, self._halowidth, self, scene)
        self._crystal = Crystal(0, 0, size / 2, self, scene)

    def rect(self):
        return self._halo.rect()
