# -*- coding: utf-8 -*-
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from nicos.clients.gui.panels.console import ConsolePanel
from nicos.clients.gui.panels.live import LiveDataPanel
from nicos.guisupport.qt import QButtonGroup, QColor, QHBoxLayout, QObject, \
    QPainter, QPushButton, QSizePolicy, QStackedWidget, QStatusBar, Qt, \
    QVBoxLayout, QWidget, pyqtSignal


def addStatusBar(mainwindow):
    mainwindow.statusBar = StatusBar(mainwindow)
    mainwindow.setStatusBar(mainwindow.statusBar)


class StatusBarOverlay(QWidget):
    def __init__(self, parent=None, statusbar=None):
        super().__init__(parent)

        self.statusbar = statusbar

        print(parent.__class__.__name__)

        layout = QVBoxLayout()

        line = QHBoxLayout()
        self.graphicsButton = QPushButton('Graphics')
        self.logButton = QPushButton('Log')
        self.toggleButton = QPushButton('Show')
        self.graphicsButton.setCheckable(True)
        self.logButton.setCheckable(True)
        self.toggleButton.setCheckable(True)

        self.buttonsBox = QButtonGroup()
        self.buttonsBox.addButton(self.graphicsButton)
        self.buttonsBox.addButton(self.logButton)

        line.addStretch()
        line.addWidget(self.graphicsButton)
        line.addWidget(self.logButton)
        line.addWidget(self.toggleButton)
        line.addStretch()

        line.setObjectName('ButtonsLayout')
        layout.addLayout(line)

        del line
        line = QHBoxLayout()

        layout.addLayout(line)
        self.setLayout(layout)
        self.toggleButton.clicked.connect(self.on_toggle)

        self.set_hidden()

    def set_hidden(self):
        self.toggleButton.setText('Show')
        for button in [self.graphicsButton, self.logButton]:
            button.setChecked(False)
            button.setDisabled(True)

    def set_visible(self):
        self.toggleButton.setText('Hide')
        self.graphicsButton.setChecked(True)
        self.graphicsButton.setDisabled(False)
        self.logButton.setDisabled(False)

    def on_toggle(self):
        if self.toggleButton.isChecked():
            self.set_visible()
            self.resize(self.window().width(), self.window().height())
        else:
            self.set_hidden()


class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = self.layout()

        self.graphicsButton = QPushButton('Graphics')
        self.logButton = QPushButton('Log')
        self.toggleButton = QPushButton('Show')
        self.graphicsButton.setCheckable(True)
        self.logButton.setCheckable(True)
        self.toggleButton.setCheckable(True)

        self.buttonsBox = QButtonGroup()
        self.buttonsBox.addButton(self.graphicsButton)
        self.buttonsBox.addButton(self.logButton)

        layout.addStretch(1)
        layout.addWidget(self.graphicsButton)
        layout.addWidget(self.logButton)
        layout.addWidget(self.toggleButton)
        layout.addStretch(1)

        self.overlay = TranslucentWidget(parent, self)
        self.overlay.hide()

        self.toggleButton.clicked.connect(self.on_toggle)
        self.graphicsButton.clicked.connect(self.overlay.setLiveViewWidget)
        self.logButton.clicked.connect(self.overlay.setLogWidget)

        self.set_hidden()

    def set_hidden(self):
        self.toggleButton.setText('Show')
        for button in [self.graphicsButton, self.logButton]:
            button.setChecked(False)
            button.setDisabled(True)

    def set_visible(self):
        self.toggleButton.setText('Hide')
        self.graphicsButton.setChecked(True)
        self.graphicsButton.setDisabled(False)
        self.logButton.setDisabled(False)

    def on_toggle(self):
        if self.toggleButton.isChecked():
            self.overlay.show()
            self.set_visible()
            self.resize(self.parent().width(), self.parent().height())
        else:
            self.overlay.hide()
            self.set_hidden()


class TranslucentWidgetSignals(QObject):
    # SIGNALS
    CLOSE = pyqtSignal()


class TranslucentWidget(QWidget):
    def __init__(self, parent=None, toolbar=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)
        self.graphic_widget = LiveDataPanel(parent, parent.client, {})
        self.graphic_widget.hide()
        self.log_widget = ConsolePanel(parent, parent.client, {})
        self.log_widget.hide()

        self.widgets = QStackedWidget(parent)
        self.widgets.addWidget(self.graphic_widget)
        self.widgets.addWidget(self.log_widget)

        layout.addWidget(self.widgets)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if toolbar:
            self.resize(parent.size() - toolbar.size())
        else:
            self.resize(parent.size())

        # make the window frameless
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.fillColor = QColor(30, 30, 30, 120)
        self.penColor = QColor("#333333")

        self.SIGNALS = TranslucentWidgetSignals()
        self.raise_()

    def paintEvent(self, event):
        # This method is, in practice, drawing the contents of
        # your window.

        # get current window size
        s = self.parent().size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(self.penColor)
        qp.setBrush(self.fillColor)
        qp.drawRect(0, 0, s.width(), s.height())

    def setLiveViewWidget(self):
        print(self.widgets.currentWidget().panelName)
        self.widgets.setCurrentIndex(0)

    def setLogWidget(self):
        print(self.widgets.currentWidget().panelName)
        self.widgets.setCurrentIndex(1)
