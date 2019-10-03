# -*- coding: utf-8 -*-
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
        super(StatusBarOverlay, self).__init__(parent)

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
        # self.buttonsBox.addButton(self.toggleButton)

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
        super(StatusBar, self).__init__(parent)
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
        super(TranslucentWidget, self).__init__(parent)

        # loadUi(self, 'overlay.ui', '%s/windows'%uipath)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.graphic_widget = LiveDataPanel(parent, parent.client, {})
        self.graphic_widget.hide()
        self.log_widget = ConsolePanel(parent, parent.client, {})
        self.log_widget.hide()

        self.widgets = QStackedWidget(parent)
        self.widgets.addWidget(self.graphic_widget)
        self.widgets.addWidget(self.log_widget)

        #
        #
        # for panel in parent.panels:
        #     try:
        #         print('%s - %s'%(panel.panelName, panel.__class__.__name__))
        #     except:
        #         pass
        #
        #     if not self.graphic_widget and panel.__class__.__name__ == \
        #             'LiveDataPanel':
        #         print(panel.panelName)
        #         self.graphic_widget = panel
        #         self.widgets.addWidget(self.graphic_widget)
        #     if not self.log_widget and panel.__class__.__name__ == \
        #             'ConsolePanel':
        #         print(panel.panelName)
        #         self.log_widget = panel
        #         self.widgets.addWidget(self.log_widget)

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

        # self.popup_fillColor = QColor(240, 240, 240, 255)
        # self.popup_penColor = QColor(200, 200, 200, 255)

        self.SIGNALS = TranslucentWidgetSignals()
        self.raise_()

    #
    # def resizeEvent(self, event):
    #     s = self.size()
    #     popup_width = 300
    #     popup_height = 120
    #     ow = int(s.width() / 2 - popup_width / 2)
    #     oh = int(s.height() / 2 - popup_height / 2)
    #     self.resize(self.window().size())

    # self.close_btn.move(ow + 265, oh + 5)

    def paintEvent(self, event):
        # This method is, in practice, drawing the contents of
        # your window.

        # get current window size
        s = self.parent().size()
        # print('rectangle: %r %r'%(event.rect().width(),
        #                          event.rect().height()))
        # print('size: %r %r'%(s.width(), s.height()))
        # print('region: %r %r'%(event.region().width(),
        #                          event.region().height()))
        # print(s)
        # print(self.parent().size())
        # print(self.window().size())
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

        # qp.drawRoundedRect(ow, oh, popup_width, popup_height, 5, 5)
    #
    #     font = QFont()
    #     font.setPixelSize(18)
    #     font.setBold(True)
    #     qp.setFont(font)
    #     qp.setPen(QColor(70, 70, 70))
    #     tolw, tolh = 80, -5
    #     qp.drawText(ow + int(popup_width / 2) - tolw,
    #                 oh + int(popup_height / 2) - tolh, "Yep, I'm a pop up.")
    #
    #     qp.end()

    # def _onclose(self):
    #     print("Close")
    #     self.SIGNALS.CLOSE.emit()
    #     self.hide()

# # class TranslucentWidget(QWidget):
# #     def __init__(self, parent=None):
# #         super(TranslucentWidget, self).__init__(parent)
# #
# #         # make the window frameless
# #         self.setWindowFlags(Qt.FramelessWindowHint)
# #         self.setAttribute(Qt.WA_TranslucentBackground)
# #
# #         self.fillColor = QColor(30, 30, 30, 120)
# #         self.penColor = QColor("#333333")
# #
# #         self.popup_fillColor = QColor(240, 240, 240, 255)
# #         self.popup_penColor = QColor(200, 200, 200, 255)
# #
# #         self.close_btn = QPushButton(self)
# #         self.close_btn.setText("x")
# #         font = QFont()
# #         font.setPixelSize(18)
# #         font.setBold(True)
# #         self.close_btn.setFont(font)
# #         self.close_btn.setStyleSheet("background-color: rgb(0, 0, 0, 0)")
# #         self.close_btn.setFixedSize(30, 30)
# #         self.close_btn.clicked.connect(self._onclose)
# #
# #         self.SIGNALS = TranslucentWidgetSignals()
# #         self.raise_()
# #
# #     def resizeEvent(self, event):
# #         s = self.size()
# #         popup_width = 300
# #         popup_height = 120
# #         ow = int(s.width() / 2 - popup_width / 2)
# #         oh = int(s.height() / 2 - popup_height / 2)
# #         self.close_btn.move(ow + 265, oh + 5)
# #
# #     def paintEvent(self, event):
# #         # This method is, in practice, drawing the contents of
# #         # your window.
# #
# #         # get current window size
# #         s = self.size()
# #         qp = QPainter()
# #         qp.begin(self)
# #         qp.setRenderHint(QPainter.Antialiasing, True)
# #         qp.setPen(self.penColor)
# #         qp.setBrush(self.fillColor)
# #         qp.drawRect(0, 0, s.width(), s.height())
# #
# #         # drawpopup
# #         qp.setPen(self.popup_penColor)
# #         qp.setBrush(self.popup_fillColor)
# #         popup_width = 300
# #         popup_height = 120
# #         ow = int(s.width()/2-popup_width/2)
# #         oh = int(s.height()/2-popup_height/2)
# #         qp.drawRoundedRect(ow, oh, popup_width, popup_height, 5, 5)
# #
# #         font = QFont()
# #         font.setPixelSize(18)
# #         font.setBold(True)
# #         qp.setFont(font)
# #         qp.setPen(QColor(70, 70, 70))
# #         tolw, tolh = 80, -5
# #         qp.drawText(ow + int(popup_width/2) - tolw, oh + int(popup_height/2) - tolh, "Yep, I'm a pop up.")
# #
# #         qp.end()
# #
# #     def _onclose(self):
# #         print("Close")
# #         self.SIGNALS.CLOSE.emit()
