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

"""Qt version of instrument monitor."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import threading
from cgi import escape
from time import time as currenttime, sleep

from PyQt4.QtCore import QSize, QEvent, Qt, SIGNAL
from PyQt4.QtGui import QFrame, QLabel, QPalette, QMainWindow, QVBoxLayout, \
     QColor, QFont, QFontMetrics, QSizePolicy, QHBoxLayout, QApplication, \
     QCursor, QStackedWidget

from nicos.status import statuses
from nicos.monitor import Monitor as BaseMonitor


class MonitorWindow(QMainWindow):
    def keyPressEvent(self, event):
        if event.text() == 'q':
            self.close()
        return QMainWindow.keyPressEvent(self, event)

class SensitiveLabel(QLabel):
    """A label that calls back when entered/left by the mouse."""
    def __init__(self, text, parent, enter, leave):
        QLabel.__init__(self, text, parent)
        self._enter = enter
        self._leave = leave
    def enterEvent(self, event):
        self._enter(self, event)
    def leaveEvent(self, event):
        self._leave(self, event)

class BlockBox(QFrame):
    """Provide the equivalent of a Tk LabelFrame: a group box that has a
    definite frame around it.
    """
    def __init__(self, parent, text, font):
        QFrame.__init__(self, parent)
        self._label = QLabel(' ' + text + ' ', parent)
        self._label.setAutoFillBackground(True)
        self._label.setFont(font)
        self._label.resize(self._label.sizeHint())
        self._label.show()
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.connect(self, SIGNAL('enableDisplay'), self.enableDisplay)
    def moveEvent(self, event):
        self._repos()
        return QFrame.moveEvent(self, event)
    def resizeEvent(self, event):
        self._repos()
        return QFrame.resizeEvent(self, event)
    def _repos(self):
        mps = self.pos()
        msz = self.size()
        lsz = self._label.size()
        self._label.move(mps.x() + 0.5*(msz.width() - lsz.width()),
                         mps.y() - 0.5*lsz.height())
    def enableDisplay(self, layout, isvis):
        QFrame.setVisible(self, isvis)
        self._label.setVisible(isvis)
        if not isvis:
            layout.removeWidget(self)
        else:
            layout.insertWidget(1, self)

def nicedelta(t):
    if t < 60:
        return '%d seconds' % int(t)
    elif t < 3600:
        return '%.1f minutes' % (t / 60.)
    else:
        return '%.1f hours' % (t / 3600.)


class Monitor(BaseMonitor):
    """Qt specific implementation of instrument monitor."""

    def mainLoop(self):
        self._qtapp.exec_()

    def closeGui(self):
        self._master.close()

    def initColors(self):
        self._bgcolor = QColor('gray')
        self._black = QColor('black')
        self._yellow = QColor('yellow')
        self._green = QColor('#00ff00')
        self._red = QColor('red')
        self._gray = QColor('gray')
        self._white = QColor('white')

    def initGui(self):
        self._qtapp = QApplication(['qtapp', '-style', 'windows'])
        self._master = master = MonitorWindow()
        master.show()

        if self._geometry == 'fullscreen':
            master.showFullScreen()
            QCursor.setPos(master.geometry().bottomRight())
        elif isinstance(self._geometry, tuple):
            master.setGeometry(*self._geometry)

        master.setWindowTitle(self.title)
        self._bgcolor = master.palette().color(QPalette.Window)

        timefont  = QFont(self.font, self._fontsizebig + self._fontsize)
        blockfont = QFont(self.font, self._fontsizebig)
        labelfont = QFont(self.font, self._fontsize)
        stbarfont = QFont(self.font, int(self._fontsize * 0.8))
        valuefont = QFont(self.valuefont or self.font, self._fontsize)

        onechar = QFontMetrics(valuefont).width('0')
        blheight = QFontMetrics(blockfont).height()
        tiheight = QFontMetrics(timefont).height()

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterframe = QFrame(master)
        masterlayout = QVBoxLayout()
        self._timelabel = QLabel('', master)
        self._timelabel.setFont(timefont)
        self.setForeColor(self._timelabel, self._gray)
        self._timelabel.setAutoFillBackground(True)
        self._timelabel.setAlignment(Qt.AlignHCenter)
        self._timelabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        masterlayout.addWidget(self._timelabel)
        masterlayout.addSpacing(0.2 * tiheight)

        self._stacker = QStackedWidget(masterframe)
        masterlayout.addWidget(self._stacker)
        displayframe = QFrame(self._stacker)
        self._stacker.addWidget(displayframe)

        def _create_field(groupframe, field):
            fieldlayout = QVBoxLayout()
            # now put describing label and view label into subframe
            l = QLabel(' ' + escape(field['name']) + ' ', groupframe)
            l.setFont(labelfont)
            l.setAlignment(Qt.AlignHCenter)
            l.setAutoFillBackground(True)
            l.setTextFormat(Qt.RichText)
            field['namelabel'] = l
            fieldlayout.addWidget(l)

            l = SensitiveLabel('----', groupframe,
                               self._label_entered, self._label_left)
            if field['istext']:
                l.setFont(labelfont)
            else:
                l.setFont(valuefont)
                l.setAlignment(Qt.AlignHCenter)
            l.setFrameShape(QFrame.Panel)
            l.setFrameShadow(QFrame.Sunken)
            l.setAutoFillBackground(True)
            l.setLineWidth(2)
            l.setMinimumSize(QSize(onechar * (field['width'] + .5), 0))
            l.setProperty('assignedField', field)
            field['valuelabel'] = l

            tmplayout = QHBoxLayout()
            tmplayout.addStretch()
            tmplayout.addWidget(l)
            tmplayout.addStretch()
            fieldlayout.addLayout(tmplayout)

            self.updateKeymap(field)
            return fieldlayout

        # now iterate through the layout and create the widgets to display it
        displaylayout = QVBoxLayout()
        displaylayout.setSpacing(20)
        for superrow in self._layout:
            boxlayout = QHBoxLayout()
            boxlayout.setSpacing(20)
            boxlayout.setContentsMargins(10, 10, 10, 10)
            for column in superrow:
                columnlayout = QVBoxLayout()
                columnlayout.setSpacing(blheight * 0.8)
                for block in column:
                    blocklayout_outer = QHBoxLayout()
                    blocklayout_outer.addStretch()
                    blocklayout = QVBoxLayout()
                    blocklayout.addSpacing(0.5 * blheight)
                    blockbox = BlockBox(displayframe, block[0]['name'],
                                        blockfont)
                    block[0]['labelframe'] = blockbox
                    for row in block[1]:
                        if row is None:
                            blocklayout.addSpacing(12)
                        else:
                            rowlayout = QHBoxLayout()
                            rowlayout.addStretch()
                            rowlayout.addSpacing(self._padding)
                            for field in row:
                                fieldframe = _create_field(blockbox, field)
                                rowlayout.addLayout(fieldframe)
                                rowlayout.addSpacing(self._padding)
                            rowlayout.addStretch()
                            blocklayout.addLayout(rowlayout)
                    if block[0]['only']:
                        self._onlymap.setdefault(block[0]['only'], []).\
                            append((blocklayout_outer, blockbox))
                    blocklayout.addSpacing(0.3 * blheight)
                    blockbox.setLayout(blocklayout)
                    blocklayout_outer.addWidget(blockbox)
                    blocklayout_outer.addStretch()
                    columnlayout.addLayout(blocklayout_outer)
                    columnlayout.addStretch()
                columnlayout.addStretch()
                boxlayout.addLayout(columnlayout)
            displaylayout.addLayout(boxlayout)
        displayframe.setLayout(displaylayout)

        self._warnpanel = QFrame(self._stacker)
        self._stacker.addWidget(self._warnpanel)
        master.connect(self._warnpanel, SIGNAL('setindex'),
                       self._stacker.setCurrentIndex)

        warningslayout = QVBoxLayout()
        lbl = QLabel('Warnings', self._warnpanel)
        lbl.setAlignment(Qt.AlignHCenter)
        lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        lbl.setFont(timefont)
        warningslayout.addWidget(lbl)
        self._warnlabel = QLabel('', self._warnpanel)
        self._warnlabel.setFont(blockfont)
        warningslayout.addWidget(self._warnlabel)
        warningslayout.addStretch()
        self._warnpanel.setLayout(warningslayout)

        masterframe.setLayout(masterlayout)
        master.setCentralWidget(masterframe)

        def resizeToMinimum():
            master.resize(master.sizeHint())
            if self._geometry == 'fullscreen':
                master.showFullScreen()
        master.connect(master, SIGNAL('resizeToMinimum'), resizeToMinimum)

        # initialize status bar
        self._statuslabel = QLabel()
        self._statuslabel.setFont(stbarfont)
        master.statusBar().addWidget(self._statuslabel)
        self._statustimer = None

    setLabelText = QLabel.setText

    def setLabelUnitText(self, label, text, unit):
        label.setText(escape(text) +
                      ' <font color="#888888">%s</font> ' % escape(unit))

    def setForeColor(self, label, fore):
        pal = label.palette()
        pal.setColor(QPalette.WindowText, fore)
        label.setPalette(pal)

    def setBackColor(self, label, back):
        pal = label.palette()
        pal.setColor(QPalette.Window, back)
        label.setPalette(pal)

    def setBothColors(self, label, fore, back):
        pal = label.palette()
        pal.setColor(QPalette.WindowText, fore)
        pal.setColor(QPalette.Window, back)
        label.setPalette(pal)

    def switchWarnPanel(self, off=False):
        if self._stacker.currentIndex() == 1 or off:
            self._warnpanel.emit(SIGNAL('setindex'), 0)
        else:
            self._warnpanel.emit(SIGNAL('setindex'), 1)

    def reconfigureBoxes(self):
        for setup, boxes in self._onlymap.iteritems():
            for layout, blockbox in boxes:
                blockbox.emit(SIGNAL('enableDisplay'),
                              layout, setup in self._setups)
        # HACK: master.sizeHint() is only correct a certain time *after* the
        # layout change (I've not found out what event to generate or intercept
        # to do this in a more sane way).
        def emitresize():
            sleep(1)
            self._master.emit(SIGNAL('resizeToMinimum'))
        threading.Thread(target=emitresize).start()

    # special feature: mouse-over status bar text

    def _label_entered(self, widget, event):
        field = widget.property('assignedField').toPyObject()
        statustext = '%s = %s' % (field['name'], field['valuelabel'].text())
        if field['unit']:
            statustext += ' %s' % field['unit']
        if field['status']:
            try:
                const, msg = field['status']
            except ValueError:
                const, msg = field['status'], ''
            statustext += ', status is %s: %s' % (statuses.get(const, '?'), msg)
        if field['time']:
            statustext += ', updated %s ago' % (
                nicedelta(currenttime() - field['time']))
        if field['ttl']:
            exp = field['time'] + field['ttl']
            cur = currenttime()
            if cur < exp:
                statustext += ', valid for %s' % nicedelta(exp - cur)
            else:
                statustext += ', expired %s ago' % nicedelta(cur - exp)
        self._statuslabel.setText(statustext)
        self._statustimer = threading.Timer(1, lambda:
                                            self._label_entered(widget, event))
        self._statustimer.start()

    def _label_left(self, widget, event):
        self._statuslabel.setText('')
        if self._statustimer:
            self._statustimer.cancel()
            self._statustimer = None
