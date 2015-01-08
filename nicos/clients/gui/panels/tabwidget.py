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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI enhanced TabWidget."""

from PyQt4.QtGui import QTabWidget, QMainWindow, QMouseEvent, QPixmap, \
     QTabBar, QDrag, QApplication, QCursor
from PyQt4.QtCore import Qt, SIGNAL, QPoint, QMimeData, QEvent


class TearOffTabBar(QTabBar):

    def __init__(self, parent=None):
        QTabBar.__init__(self, parent)
        self.setAcceptDrops(True)
        self.setElideMode(Qt.ElideRight)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectLeftTab)
        self.setMovable(False)
        self._dragInitiated = False
        self._dragDroppedPos = QPoint()
        self._dragStartPos = QPoint()
        self.tabIdx = []

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragStartPos = event.pos()
        self._dragInitiated = False
        self._dragDroppedPos = QPoint()
        QTabBar.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self._dragStartPos.isNull() and \
            (event.pos() - self._dragStartPos).manhattanLength() \
            < QApplication.startDragDistance():
            self._dragInitiated = True
        if (event.buttons() == Qt.LeftButton) and self._dragInitiated and \
            not self.geometry().contains(event.pos()):
            finishMoveEvent = QMouseEvent(QEvent.MouseMove, event.pos(),
                                          Qt.NoButton, Qt.NoButton, Qt.NoModifier)
            QTabBar.mouseMoveEvent(self, finishMoveEvent)

            drag = QDrag(self)
            mimedata = QMimeData()
            mimedata.setData('action', 'application/tab-detach')
            drag.setMimeData(mimedata)

            pixmap = QPixmap.grabWidget(self.parentWidget().currentWidget()) \
                            .scaled(640, 480, Qt.KeepAspectRatio)
            drag.setPixmap(pixmap)
            drag.setDragCursor(QPixmap(), Qt.LinkAction)

            dragged = drag.exec_(Qt.MoveAction)
            if dragged == Qt.IgnoreAction:
                # moved outside of tab widget
                event.accept()
                self.emit(SIGNAL('on_detach_tab'),
                          self.tabAt(self._dragStartPos), QCursor.pos())
            elif dragged == Qt.MoveAction:
                # moved inside of tab widget
                if not self._dragDroppedPos.isNull():
                    event.accept()
                    self.emit(SIGNAL('on_move_tab'), self.tabAt(
                        self._dragStartPos), self.tabAt(self._dragDroppedPos))
                    self._dragDroppedPos = QPoint()
        else:
            QTabBar.mouseMoveEvent(self, event)

    def dragEnterEvent(self, event):
        mimedata = event.mimeData()
        formats = mimedata.formats()
        if 'action' in formats and \
            mimedata.data('action') == 'application/tab-detach':
            event.acceptProposedAction()
        QTabBar.dragEnterEvent(self, event)

    def dropEvent(self, event):
        self._dragDroppedPos = event.pos()
        event.acceptProposedAction()
        QTabBar.dropEvent(self, event)

    # def dragMoveEvent(self, event):
    #     mimedata = event.mimeData()
    #     formats = mimedata.formats()
    #     if 'action' in formats and \
    #         mimedata.data('action') == 'application/tab-detach':
    #         self._dragMovedPos = event.pos()
    #         event.acceptProposedAction()
    #     QTabBar.dragMoveEvent(self, event)


def topLevelWidget(w):
    widget = w
    while True:
        parent = widget.parent()
        if not parent:
            break
        else:
            widget = parent
    return widget

def firstWindow(w):
    widget = w
    while True:
        parent = widget.parent()
        if not parent:
            widget = None
            break
        else:
            widget = parent
            if widget.isWindow():
                break
    return widget


class TearOffTabWidget(QTabWidget):

    def __init__(self, menuwindow, parent=None):
        QTabWidget.__init__(self, parent)
        self.menuwindow = menuwindow
        self.tabBar = TearOffTabBar(self)
        self.setTabBar(self.tabBar)
        self.setMovable(False)
        self.previousTabIdx = 0
        self.connect(self.tabBar, SIGNAL('on_detach_tab'), self.detachTab)
        self.connect(self.tabBar, SIGNAL('on_move_tab'), self.moveTab)
        self.connect(self, SIGNAL('currentChanged(int)'), self.tabChangedTab)

    def moveTab(self, fromInd, toInd):
        w = self.widget(fromInd)
        text = self.tabText(fromInd)
        self.removeTab(fromInd)
        self.insertTab(toInd, w, text)
        self.setCurrentIndex(toInd)

    def detachTab(self, index, point):
        # print '({0}, {1})'.format(point.x(), point.y())
        detachWindow = DetachedWindow(self.parentWidget())
        detachWindow.setWindowModality(Qt.NonModal)
        detachWindow.tabIdx = self.tabBar.tabIdx[index]
        del self.tabBar.tabIdx[index]

        self.connect(detachWindow, SIGNAL('on_close'), self.attachTab)
        detachWindow.setWindowTitle(self.tabText(index))

        tearOffWidget = self.widget(index)
        tearOffWidget.setParent(detachWindow)

        if self.count() < 0:
            self.setCurrentIndex(0)

        for p in tearOffWidget.panels:
            if hasattr(p, 'menuToolsActions'):
                topLevelWindow = topLevelWidget(p)

                if hasattr(topLevelWindow, 'menuTools'):
                    for action in p.menuToolsActions:
                        topLevelWindow.menuTools.removeAction(action)

        for p in tearOffWidget.panels:
            for action in p.actions:
                action.setVisible(False)

            for menu in p.getMenus():
                action = detachWindow.menuBar().addMenu(menu)
                action.setVisible(True)

            for toolbar in p.getToolbars():
                toolbar.hide()
                topLevelWindow = topLevelWidget(p)
                topLevelWindow.removeToolBar(toolbar)

                detachWindow.addToolBar(toolbar)
                toolbar.show()

        detachWindow.setWidget(tearOffWidget)
        detachWindow.resize(tearOffWidget.size())
        detachWindow.move(point)
        detachWindow.show()

    def attachTab(self, parent):
        detachWindow = parent
        tearOffWidget = detachWindow.centralWidget()
        tearOffWidget.setParent(self)

        for p in tearOffWidget.panels:
            if hasattr(p, 'menuToolsActions'):
                topLevelWindow = topLevelWidget(self)

                if hasattr(topLevelWindow, 'menuTools'):
                    for action in p.menuToolsActions:
                        topLevelWindow.menuTools.removeAction(action)

        newIndex = -1
        for i in range(self.tabBar.count()):
            if self.tabBar.tabIdx[i] > detachWindow.tabIdx:
                newIndex = i
                break

        if newIndex == -1:
            newIndex = self.tabBar.count()

        self.tabBar.tabIdx.insert(newIndex, detachWindow.tabIdx)

        newIndex = self.insertTab(newIndex, tearOffWidget, detachWindow.windowTitle())

        if newIndex != -1:
            self.setCurrentIndex(newIndex)

        self.disconnect(detachWindow, SIGNAL('on_close'), self.attachTab)


    def tabChangedTab(self, index):
        for i in range(self.count()):
            for p in self.widget(i).panels:
                for toolbar in p.getToolbars():
                    self.menuwindow.removeToolBar(toolbar)
                for action in p.actions:
                    action.setVisible(False)

        if self.previousTabIdx < self.count():
            if self.widget(self.previousTabIdx):
                for p in self.widget(self.previousTabIdx).panels:
                    if hasattr(p, 'menuToolsActions'):
                        topLevelWindow = topLevelWidget(p)

                        if hasattr(topLevelWindow, 'menuTools'):
                            for action in p.menuToolsActions:
                                topLevelWindow.menuTools.removeAction(action)

        if self.widget(index):
            for p in self.widget(index).panels:
                p.getMenus()

                if hasattr(p, 'menuToolsActions'):
                    topLevelWindow = topLevelWidget(p)

                    if hasattr(topLevelWindow, 'menuTools'):
                        for action in p.menuToolsActions:
                            topLevelWindow.menuTools.addAction(action)

                for toolbar in p.getToolbars():
                    if hasattr(self.menuwindow, 'toolBarWindows'):
                        self.menuwindow.insertToolBar(self.menuwindow.toolBarWindows, toolbar)
                    else:
                        self.menuwindow.addToolBar(toolbar)
                    toolbar.show()

                for menu in p.actions:
                    menu.setVisible(True)

        self.previousTabIdx = index


class DetachedWindow(QMainWindow):

    def __init__(self, parent):
        self.tabIdx = -1
        QMainWindow.__init__(self, parent)

    def setWidget(self, widget):
        self.setCentralWidget(widget)
        widget.show()

    def closeEvent(self, event):
        self.emit(SIGNAL('on_close'), self)
