#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""Commandlets for KWS-2."""

from nicos.guisupport.qt import QCheckBox

from nicos.clients.gui.cmdlets import register
from nicos_mlz.kws1.gui.cmdlets import MeasureTable as KWS1MeasureTable


class MeasureTable(KWS1MeasureTable):

    def __init__(self, parent, client):
        KWS1MeasureTable.__init__(self, parent, client)
        self.hvBox = QCheckBox('Shut down GE detector HV at the end', self)
        self.hvBox.setChecked(True)
        self.extendedFrame.layout().addWidget(self.hvBox)

    def generate(self, mode):
        res = KWS1MeasureTable.generate(self, mode)
        if self.hvBox.isChecked():
            res += "\nmaw(gedet_HV, 'off')"
        return res


register(MeasureTable)
