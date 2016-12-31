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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Dialog for exporting data."""

from PyQt4.QtGui import QFileDialog, QLabel, QComboBox


class DataExportDialog(QFileDialog):

    def __init__(self, viewplot, curvenames, *args):
        QFileDialog.__init__(self, viewplot, *args)
        self.setConfirmOverwrite(True)
        self.setAcceptMode(QFileDialog.AcceptSave)
        layout = self.layout()
        layout.addWidget(QLabel('Curve:', self), 4, 0)
        self.curveCombo = QComboBox(self)
        self.curveCombo.addItems(curvenames)
        layout.addWidget(self.curveCombo, 4, 1)
        layout.addWidget(QLabel('Time format:', self), 5, 0)
        self.formatCombo = QComboBox(self)
        self.formatCombo.addItems(['Seconds since first datapoint',
                                   'UNIX timestamp',
                                   'Text timestamp (YYYY-MM-dd.HH:MM:SS)'])
        layout.addWidget(self.formatCombo, 5, 1)
