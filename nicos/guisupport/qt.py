#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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

"""Qt 4/5 compatibility layer.

At the moment, only Qt 4 is fully tested.  Therefore, to use Qt 5, the
environment variable NICOS_QT=5 has to be set to select this version.
"""

# pylint: disable=wildcard-import, unused-import, unused-wildcard-import
# PyQt4.QtCore re-exports the original bin, hex and oct builtins
# pylint: disable=redefined-builtin

# this one is temporary until build machines have Qt5 installed:
# pylint: disable=import-error

import os

if os.environ.get('NICOS_QT') == '5':
    import sip
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import QObject
    from PyQt5.QtCore import *
    from PyQt5.QtPrintSupport import *
    from PyQt5.QtDesigner import *
    from PyQt5 import uic

    try:
        from PyQt5 import QtWebEngineWidgets
    except (ImportError, RuntimeError):
        QWebView = QWebPage = None
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

    import nicos.guisupport.gui_rc_qt5

    class QPyNullVariant(object):
        pass

    propertyMetaclass = type(QObject)

else:
    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

    from PyQt4.QtGui import *
    from PyQt4.QtCore import pyqtWrapperType
    from PyQt4.QtCore import *
    from PyQt4.QtDesigner import *
    from PyQt4 import uic

    try:
        from PyQt4 import QtWebKit
    except (ImportError, RuntimeError):
        QWebView = QWebPage = None
    else:
        QWebView = QtWebKit.QWebView
        QWebPage = QtWebKit.QWebPage

    try:
        from PyQt4 import QtDBus
    except (ImportError, RuntimeError):
        QtDBus = None

    try:
        from PyQt4.Qsci import QsciScintilla, QsciLexerPython, QsciPrinter
    except (ImportError, RuntimeError):
        QsciScintilla = QsciLexerPython = QsciPrinter = None

    import nicos.guisupport.gui_rc_qt4

    try:
        from PyQt4.QtCore import QPyNullVariant  # pylint: disable=E0611
    except ImportError:
        class QPyNullVariant(object):
            pass

    propertyMetaclass = pyqtWrapperType
