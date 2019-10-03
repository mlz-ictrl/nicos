#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI main window."""

from __future__ import absolute_import, division, print_function

import os

from nicos.clients.gui.mainwindow import MainWindow as DefaultMainWindow
from nicos.guisupport.qt import QAction, QApplication, QFileDialog, \
    QKeySequence, QLabel, QMenu, QPixmap, QPoint, QSizePolicy, Qt, QWidget, \
    pyqtSlot

from nicos_ess.gui import uipath


def decolor_logo(pixmap, color):
    retpix = QPixmap(pixmap.size())
    retpix.fill(color)
    retpix.setMask(pixmap.createMaskFromColor(Qt.transparent))
    return retpix


class Spacer(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class MainWindow(DefaultMainWindow):
    """
    Options:

    * ``ess_gui`` (default False) -- Use the GUI setup defined during the
      ESS-UX workshop.
    """

    ui = '%s/main.ui' % uipath

    def __init__(self, log, gui_conf, viewonly=False, tunnel=''):
        DefaultMainWindow.__init__(self, log, gui_conf, viewonly, tunnel)
        self.addLogo()
        self.addInstrument()
        self.addExperiment()

        # Cheesburger menu
        dropdown = QMenu('')
        dropdown.addAction(self.actionConnect)
        dropdown.addAction(self.actionViewOnly)
        dropdown.addAction(self.actionPreferences)
        dropdown.addAction(self.actionExpert)
        dropdown.addSeparator()
        dropdown.addAction(self.actionExit)
        self.actionUser.setMenu(dropdown)
        self.actionUser.setIconVisibleInMenu(True)
        self.dropdown = dropdown
        reload_action = QAction("Reload QSS", self,
                                triggered=self.reloadQSS,
                                shortcut=QKeySequence.Refresh)
        select_action = QAction("Select QSS", self, triggered=self.selectQSS)
        dropdown.addAction(reload_action)
        dropdown.addAction(select_action)

    # addStatusBar(self)

    def addLogo(self):
        logoLabel = QLabel()
        pxr = decolor_logo(QPixmap("resources/logo-icon.png"), Qt.white)
        logoLabel.setPixmap(pxr.scaledToHeight(self.toolBarMain.height(),
                                               Qt.SmoothTransformation))
        self.toolBarMain.insertWidget(self.toolBarMain.actions()[0], logoLabel)

        nicosLabel = QLabel()
        pxr = decolor_logo(QPixmap("resources/nicos-logo-high.png"), Qt.white)
        nicosLabel.setPixmap(pxr.scaledToHeight(self.toolBarMain.height(),
                                                Qt.SmoothTransformation))
        self.toolBarMain.insertWidget(self.toolBarMain.actions()[1],
                                      nicosLabel)

    def addInstrument(self):
        textLabel = QLabel('Instrument:')
        textLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        textLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        instrumentLabel = QLabel('Unknown')
        instrumentLabel.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Preferred)
        self.toolBarMain.addWidget(textLabel)
        self.toolBarMain.addWidget(instrumentLabel)

        instrument = os.getenv('INSTRUMENT')
        if instrument:
            instrument = instrument.split('.')[-1]
            logo = decolor_logo(QPixmap('resources/%s-logo.png' % instrument),
                                Qt.white)
            if logo.isNull():
                instrumentLabel.setText(instrument.upper())
                return
            instrumentLabel.setPixmap(logo.scaledToHeight(
                self.toolBarMain.height(), Qt.SmoothTransformation))

    def addExperiment(self):
        textLabel = QLabel('Experiment:')
        textLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        textLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        experimentLabel = QLabel('Unknown')
        experimentLabel.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Preferred)
        self.toolBarMain.addWidget(textLabel)
        self.toolBarMain.addWidget(experimentLabel)

        # if INSTRUMENT is defined add the logo/name of the instrument
        experiment = os.getenv('EXPERIMENT')
        if experiment:
            experimentLabel.setText(experiment)

    def reloadQSS(self):
        self.setQSS('nicos_demo/demo/guiconfig-ess.qss')

    def selectQSS(self):
        stylefile = QFileDialog.getOpenFileName(self,
                                                filter="Qt Stylesheet Files ("
                                                "*.qss)")[0]
        if stylefile:
            self.setQSS(stylefile)

    def setQSS(self, stylefile):
        with open(stylefile, 'r') as fd:
            try:
                QApplication.instance().setStyleSheet(fd.read())
            except Exception as e:
                print(e)

    @pyqtSlot()
    def on_actionUser_triggered(self):
        w = self.toolBarRight.widgetForAction(self.actionUser)
        self.dropdown.popup(w.mapToGlobal(QPoint(0, w.height())))

    @pyqtSlot()
    def on_actionEmergencyStop_triggered(self):
        self.client.tell_action('emergency')
