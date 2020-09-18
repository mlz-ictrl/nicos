#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

"""Qt compatibility layer.
"""

# pylint: disable=wildcard-import, unused-import, unused-wildcard-import

import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtCore import QObject
from PyQt5.QtDesigner import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtWidgets import *

import nicos.guisupport.gui_rc_qt5

try:
    from PyQt5 import sip
except ImportError:
    import sip

try:
    from PyQt5 import QtWebEngineWidgets
except (ImportError, RuntimeError):
    try:
        from PyQt5 import QtWebKitWidgets
    except (ImportError, RuntimeError):
        QWebView = QWebPage = None
    else:
        QWebView = QtWebKitWidgets.QWebView
        QWebPage = QtWebKitWidgets.QWebPage
else:
    QWebView = QtWebEngineWidgets.QWebEngineView
    QWebPage = QtWebEngineWidgets.QWebEnginePage

try:
    from PyQt5 import QtDBus
except (ImportError, RuntimeError):
    QtDBus = None

try:
    from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciPrinter
except (ImportError, RuntimeError):
    QsciScintilla = QsciLexerPython = QsciPrinter = None


class QPyNullVariant:
    pass

propertyMetaclass = type(QObject)


QT_VER = int(QT_VERSION_STR.split('.')[0])

if 'linux' in sys.platform:
    import ctypes
    import ctypes.util
    # preload opengl library for usage e.g. in QtWebkit
    # otherwise on various linux systems the opengl shader program
    # cannot be created which results in black/white window content.
    # this is a well-known issue, see:
    # https://github.com/qutebrowser/qutebrowser/issues/3106
    # https://bugs.launchpad.net/ubuntu/+source/python-qt4/+bug/941826
    libGL = ctypes.util.find_library('GL')
    if libGL:
        ctypes.CDLL(libGL, mode=ctypes.RTLD_GLOBAL)
