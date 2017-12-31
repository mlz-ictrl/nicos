#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

"""GUI support utilities."""

from contextlib import contextmanager

from nicos.guisupport.qt import Qt, QApplication, QPalette, QValidator, \
    QDoubleValidator


def setBackgroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    palette.setColor(QPalette.Base, color)
    widget.setBackgroundRole(QPalette.Window)
    widget.setPalette(palette)


def setForegroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.WindowText, color)
    palette.setColor(QPalette.Text, color)
    widget.setForegroundRole(QPalette.WindowText)
    widget.setPalette(palette)


def setBothColors(widget, colors):
    palette = widget.palette()
    palette.setColor(QPalette.WindowText, colors[0])
    palette.setColor(QPalette.Window, colors[1])
    palette.setColor(QPalette.Base, colors[1])
    widget.setBackgroundRole(QPalette.Window)
    widget.setForegroundRole(QPalette.WindowText)
    widget.setPalette(palette)


class DoubleValidator(QDoubleValidator):

    def validate(self, string, pos):
        if ',' in string:
            return QValidator.Invalid, string, pos
        return QDoubleValidator.validate(self, string, pos)


@contextmanager
def waitCursor():
    """Context manager creating an hour glass style cursor for longer-running
    blocking tasks inside GUI code.  Example::

        with waitCursor():
            # process takes some time
            pass
    """
    try:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        yield
    finally:
        QApplication.restoreOverrideCursor()
