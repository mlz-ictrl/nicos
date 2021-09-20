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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""GUI support utilities."""

from contextlib import contextmanager
from os import path

import gr

from nicos.guisupport.qt import QApplication, QDoubleValidator, QFileDialog, \
    QFont, QPalette, Qt, QValidator


def savePlot(widget, default_file_type, old_file_path=None):
    """Saves a plot in the specified file format.

    :param widget: graphics widget.
    :param default_file_type: default save file type.
    :param old_file_path: file path from a previous save operation.
    :return: returns file path,
             returns empty string or old file path when
             user cancels save.
    """
    gr_file_types = {**gr.PRINT_TYPE, **gr.GRAPHIC_TYPE}
    save_types = ";;".join(sorted(set(gr_file_types.values())))
    default_file = 'untitled'
    if old_file_path:
        default_file = path.splitext(old_file_path)[0]
    file_path, _ = QFileDialog.getSaveFileName(None, 'Save as...',
                                               default_file, filter=save_types,
                                               initialFilter=default_file_type)
    if not file_path:
        return "" if not old_file_path else old_file_path

    file_ext = path.splitext(file_path)[1]
    if file_ext.lower()[1:] in gr_file_types:
        widget.save(file_path)
    else:
        raise TypeError("Unsupported file format {}".format(file_ext))

    return file_path


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


def scaledFont(font, scale):
    new = QFont(font)
    new.setPointSizeF(font.pointSizeF() * scale)
    return new


class DoubleValidator(QDoubleValidator):

    def validate(self, string, pos):
        if ',' in string:
            return QValidator.Invalid, string, pos
        elif string.startswith('.'):
            return QDoubleValidator.validate(self, '0' + string, pos + 1)
        elif string.startswith('-.') or string.startswith('+.'):
            return QDoubleValidator.validate(
                self, '%s0%s' % (string[0], string[1:]), pos + 1)
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
