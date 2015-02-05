#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from PyQt4.QtGui import QPalette


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


def extractKeyAndIndex(spec):
    """Extract a key and possibly subindex from a cache key specification
    given by the user.  This takes into account the following changes:

    * '/' can be replaced by '.'
    * If it is not in the form 'dev/key', '/value' is automatically
      appended
    * Subitems can be specified with '[i]'
    """
    key = spec.lower().replace('.', '/')
    index = -1
    if '[' in spec and spec.endswith(']'):
        try:
            key, index = key.split('[', 1)
            key = key.strip()
            index = int(index.rstrip(']'))
        except ValueError:
            index = -1
    if '/' not in key:
        key += '/value'
    return key, index
