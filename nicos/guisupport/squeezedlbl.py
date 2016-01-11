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

"""
A label that "squeezes" its text, inserting an ellipsis if necessary.
"""

from PyQt4.QtGui import QLabel
from PyQt4.QtCore import Qt

from nicos.pycompat import text_type


class SqueezedLabel(QLabel):
    """A label that elides text to fit its width."""

    def __init__(self, *args):
        self._fulltext = ''
        QLabel.__init__(self, *args)
        self._squeeze()

    def resizeEvent(self, event):
        self._squeeze()
        QLabel.resizeEvent(self, event)

    def setText(self, text):
        self._fulltext = text
        self._squeeze(text)

    def minimumSizeHint(self):
        sh = QLabel.minimumSizeHint(self)
        sh.setWidth(-1)
        return sh

    def _squeeze(self, text=None):
        if text is None:
            text = self._fulltext or self.text()
        fm = self.fontMetrics()
        labelwidth = self.size().width()
        squeezed = False
        new_lines = []
        for line in text.split('\n'):
            if fm.width(line) > labelwidth:
                squeezed = True
                new_lines.append(fm.elidedText(line, Qt.ElideRight, labelwidth))
            else:
                new_lines.append(line)
        if squeezed:
            QLabel.setText(self, '\n'.join(map(text_type, new_lines)))
            self.setToolTip(self._fulltext)
        else:
            QLabel.setText(self, self._fulltext)
            self.setToolTip('')
