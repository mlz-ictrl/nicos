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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Qt compatibility layer.
"""

# pylint: disable=wildcard-import, unused-import, unused-wildcard-import

import os
import sys

NICOS_QT = os.environ.get('NICOS_QT')

if NICOS_QT == '6':
    # pylint: disable=import-error

    from PyQt6 import uic
    from PyQt6.QtCore import *
    from PyQt6.QtCore import QObject
    from PyQt6.QtDesigner import *
    from PyQt6.QtGui import *
    from PyQt6.QtPrintSupport import *
    from PyQt6.QtWidgets import *

    import nicos.guisupport.gui_rc_qt6

    try:
        from PyQt6 import QtWebEngineCore, QtWebEngineWidgets
        from PyQt6.QtWebEngineCore import QWebEnginePage
        from PyQt6.QtWebEngineWidgets import QWebEngineView
    except (ImportError, RuntimeError):
        QWebEnginePage = QWebEngineView = None

    try:
        from PyQt6 import sip
    except ImportError:
        import sip

    try:
        from PyQt6 import QtDBus
    except (ImportError, RuntimeError):
        QtDBus = None

    try:
        from PyQt6.Qsci import QsciLexerPython, QsciPrinter, QsciScintilla
    except (ImportError, RuntimeError):
        QsciScintilla = QsciLexerPython = QsciPrinter = None

    # add missing enum mapping for QAction shortcut context
    from PyQt6.uic.enum_map import EnumMap
    EnumMap['Qt::WidgetShortcut'] = 'Qt::ShortcutContext::WidgetShortcut'
    EnumMap['Qt::WidgetWithChildrenShortcut'] = 'Qt::ShortcutContext::WidgetWithChildrenShortcut'
    EnumMap['Qt::WindowShortcut'] = 'Qt::ShortcutContext::WindowShortcut'
    EnumMap['Qt::ApplicationShortcut'] = 'Qt::ShortcutContext::ApplicationShortcut'

else:
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
        from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
    except (ImportError, RuntimeError):
        QWebEnginePage = QWebEngineView = None

    try:
        from PyQt5 import QtDBus
    except (ImportError, RuntimeError):
        QtDBus = None

    try:
        from PyQt5.Qsci import QsciLexerPython, QsciPrinter, QsciScintilla
    except (ImportError, RuntimeError):
        QsciScintilla = QsciLexerPython = QsciPrinter = None


QT_VER = int(QT_VERSION_STR.split('.', maxsplit=1)[0])

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
