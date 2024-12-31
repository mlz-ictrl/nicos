# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""GUI support utilities."""

import re
from contextlib import contextmanager
from os import path

import gr

from nicos.guisupport.qt import QApplication, QCursor, QDoubleValidator, \
    QFileDialog, QFont, QLocale, QPalette, Qt, QValidator


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
    file_path, selectedfilter = QFileDialog.getSaveFileName(
        None, 'Save as...', default_file, filter=save_types,
        initialFilter=default_file_type)
    if not file_path:
        return "" if not old_file_path else old_file_path

    file_ext = path.splitext(file_path)[1]
    if not file_ext:
        file_ext = re.search(
            r'\((.+?)\)', selectedfilter).group(1).replace('*', '').split()[0]
        file_path += file_ext
    if file_ext.lower()[1:] in gr_file_types:
        widget.save(file_path)
    else:
        raise TypeError("Unsupported file format {}".format(file_ext))

    return file_path


def setBackgroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, color)
    palette.setColor(QPalette.ColorRole.Base, color)
    widget.setBackgroundRole(QPalette.ColorRole.Window)
    widget.setPalette(palette)


def setForegroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.WindowText, color)
    palette.setColor(QPalette.ColorRole.Text, color)
    widget.setForegroundRole(QPalette.ColorRole.WindowText)
    widget.setPalette(palette)


def setBothColors(widget, colors):
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.WindowText, colors[0])
    palette.setColor(QPalette.ColorRole.Window, colors[1])
    palette.setColor(QPalette.ColorRole.Base, colors[1])
    widget.setBackgroundRole(QPalette.ColorRole.Window)
    widget.setForegroundRole(QPalette.ColorRole.WindowText)
    widget.setPalette(palette)


def scaledFont(font, scale):
    new = QFont(font)
    new.setPointSizeF(font.pointSizeF() * scale)
    return new


class DoubleValidator(QDoubleValidator):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLocale(QLocale('C'))

    def validate(self, string, pos):
        if ',' in string:
            return QValidator.State.Invalid, string, pos
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
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        yield
    finally:
        QApplication.restoreOverrideCursor()
