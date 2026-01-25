# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI widget to display the author list animated."""

import nicos.authors
from nicos.guisupport.qt import QAbstractAnimation, QEasingCurve, \
    QFontMetrics, QPauseAnimation, QPropertyAnimation, \
    QSequentialAnimationGroup, Qt, QTextBrowser, pyqtSlot


class AuthorsList(QTextBrowser):
    """Display the NICOS authors list animated."""

    def __init__(self, parent=None):
        QTextBrowser.__init__(self, parent)
        self.setText(nicos.authors.authors_list)

        fm = QFontMetrics(self.currentFont())
        fontSize = fm.height()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.vsb = self.verticalScrollBar()
        self.vsb.setMinimum(0)
        self.vsb.setMaximum(
            fontSize * len(nicos.authors.authors_list.split('\n')))

        self.anim = QSequentialAnimationGroup()
        self.anim.addAnimation(QPauseAnimation(1000))

        linAnim = QPropertyAnimation(self.vsb, b'value')
        linAnim.setDuration(10 * self.vsb.maximum())
        linAnim.setStartValue(self.vsb.minimum())
        linAnim.setEndValue(self.vsb.maximum())
        linAnim.setEasingCurve(QEasingCurve.Type.Linear)

        self.anim.addAnimation(linAnim)
        self.anim.setLoopCount(1)

        self.vsb.sliderPressed.connect(self.anim.stop)

    @pyqtSlot()
    def animate(self):
        self.anim.start()

    def wheelEvent(self, event):
        if self.anim.state() == QAbstractAnimation.State.Running:
            self.anim.stop()
        QTextBrowser.wheelEvent(self, event)
