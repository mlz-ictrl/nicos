#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
# *****************************************************************************

"""NICOS live 2D data plot window."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.gui.utils import loadUi, DlgUtils
from nicos.gui.cascadewidget import CascadeWidget, TmpImage


class LiveWindow(QMainWindow, DlgUtils):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'Live data')
        loadUi(self, 'live.ui')

        self.widget = CascadeWidget(self)
        self.setCentralWidget(self.widget)

        self.connect(self.actionLogScale, SIGNAL("toggled(bool)"),
                     self.widget, SLOT("SetLog10(bool)"))

    def setData(self, data):
        self.widget.LoadPadMem(data, 128*128*4)

    @qtsig('')
    def on_actionWriteXml_triggered(self):
        filename = str(QFileDialog.getSaveFileName(
            self, self.tr('Select file name'), '',
            self.tr('XML files (*.xml)')))
        if filename == '':
            return
        if not filename.endswith('.xml'):
            filename += '.xml'
        pad = self.widget.GetPad()
        if pad is None:
            return
        tmpimg = TmpImage()
        tmpimg.ConvertPAD(pad)
        tmpimg.WriteXML(filename)

    @qtsig('')
    def on_actionSetAsROI_triggered(self):
        zoom = self.widget.GetPlot().GetZoomer().zoomRect()
        self.parent().run_script('None', 'psd.roi = (%s, %s, %s, %s)' %
                                 (int(zoom.left()), int(zoom.top()),
                                  int(zoom.right()), int(zoom.bottom())))

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.widget.GetPlot().GetZoomer().zoom(0)

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.widget.GetPlot().print_(printer)
        self.statusBar.showMessage('Plot successfully printed to %s.' %
                                   str(printer.printerName()))
