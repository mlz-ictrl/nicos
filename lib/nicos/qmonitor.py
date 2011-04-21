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

import re
import sys
import threading
from cgi import escape
from time import time as currenttime, sleep, strftime

from PyQt4.QtCore import QSize, QPoint, Qt, SIGNAL
from PyQt4.QtGui import QFrame, QLabel, QPalette, QMainWindow, QVBoxLayout, \
     QColor, QFont, QFontMetrics, QSizePolicy, QHBoxLayout, QApplication, \
     QCursor, QStackedWidget

from nicos.utils import listof
from nicos.status import OK, BUSY, ERROR, PAUSED, NOTREACHED, statuses
from nicos.device import Param
from nicos.cache.client import BaseCacheClient
from nicos.cache.utils import OP_TELL, cache_load

def nicedelta(t):
    if t < 60:
        return '%d seconds' % int(t)
    elif t < 3600:
        return '%.1f minutes' % (t / 60.)
    else:
        return '%.1f hours' % (t / 3600.)


class Field(dict):
    def __hash__(self):
        return id(self)

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

def set_forecolor(label, fore):
    pal = label.palette()
    pal.setColor(QPalette.WindowText, fore)
    label.setPalette(pal)

def set_backcolor(label, back):
    pal = label.palette()
    pal.setColor(QPalette.Window, back)
    label.setPalette(pal)

def set_fore_backcolor(label, fore, back):
    pal = label.palette()
    pal.setColor(QPalette.WindowText, fore)
    pal.setColor(QPalette.Window, back)
    label.setPalette(pal)


class Monitor(BaseCacheClient):

    # server and prefix parameters come from BaseCacheClient
    parameters = {
        # XXX add more configurables: timeouts ...
        'title':     Param('Title of status window', type=str,
                           default='Status'),
        'layout':    Param('Status monitor layout', type=listof(list),
                           mandatory=True),
        'warnings':  Param('List of warning conditions', type=listof(list),
                           mandatory=True),
        'font':      Param('Font name for the window', type=str,
                           default='Luxi Sans'),
        'valuefont': Param('Font name for the value displays', type=str),
        'fontsize':  Param('Basic font size', type=int, default=12,
                           settable=True),
        'padding':   Param('Padding for the display fields', type=int,
                           default=2, settable=True),
        'geometry':  Param('Geometry for status window', type=str,
                           settable=True),
        'resizable': Param('Whether the window is resizable', type=bool,
                           default=True),
    }

    def start(self, options):
        self.printinfo('Qt monitor starting up, creating main window')

        self._fontsize = options.fontsize or self.fontsize
        self._padding  = options.padding or self.padding
        self._geometry = options.geometry or self.geometry

        qapp = QApplication(['qapp', '-style', 'windows'])
        window = MonitorWindow()
        window.show()
        self.qt_init(window)

        self._selecttimeout = 0.2
        self._watch = set()
        # now start the worker thread
        self._worker.start()

        self.printinfo('starting main loop')
        # start main loop and wait for termination
        try:
            qapp.exec_()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True

    def wait(self):
        self.printinfo('monitor quitting')
        self._worker.join()
        self.printinfo('done')

    def quit(self, *ignored):
        self._master.close()
        self._stoprequest = True

    def qt_init(self, master):
        self._master = master
        if self._geometry:
            if self._geometry == 'fullscreen':
                master.showMaximized()
                QCursor.setPos(master.geometry().bottomRight())
            else:
                try:
                    w, h, x, y = map(int, re.match('(\d+)x(\d+)+(\d+)+(\d+)',
                                                   self._geometry).groups())
                except Exception:
                    self.printwarning('invalid geometry %s' % self._geometry)
                else:
                    master.setGeometry(x, y, w, h)
        fontsize = self._fontsize
        fontsizebig = int(self._fontsize * 1.2)

        self._bgcolor = master.palette().color(QPalette.Window)
        self._black = QColor('black')
        self._yellow = QColor('yellow')
        self._green = QColor('#00ff00')
        self._red = QColor('red')
        self._gray = QColor('gray')
        self._white = QColor('white')

        master.setWindowTitle(self.title)

        self._timefont  = QFont(self.font, fontsizebig + fontsize)
        self._blockfont = QFont(self.font, fontsizebig)
        self._labelfont = QFont(self.font, fontsize)
        self._stbarfont = QFont(self.font, int(fontsize * 0.8))
        self._valuefont = QFont(self.valuefont or self.font, fontsize)

        self._onechar = QFontMetrics(self._valuefont).width('0')
        self._blheight = QFontMetrics(self._blockfont).height()
        self._tiheight = QFontMetrics(self._timefont).height()

        field_defaults = {
            # display/init properties
            'name': '', 'dev': '', 'width': 8, 'istext': False, 'maxlen': None,
            'min': None, 'max': None, 'unit': '', 'format': '%s',
            # current values
            'value': None, 'time': 0, 'ttl': 0, 'status': None, 'changetime': 0,
            # key names
            'key': '', 'statuskey': '', 'unitkey': '', 'formatkey': '',
        }

        # convert configured layout to internal structure
        prefix = self._prefix + '/'
        self._layout = []
        for superrowdesc in self.layout:
            columns = []
            for columndesc in superrowdesc:
                blocks = []
                for blockdesc in columndesc:
                    rows = []
                    for rowdesc in blockdesc[1]:
                        if rowdesc == '---':
                            rows.append(None)
                            continue
                        fields = []
                        for fielddesc in rowdesc:
                            field = Field(field_defaults)
                            if isinstance(fielddesc, str):
                                fielddesc = {'dev': fielddesc}
                            field.update(fielddesc)
                            if not field['name']:
                                field['name'] = field['dev']
                            fields.append(field)
                        rows.append(fields)
                    block = ({'name': blockdesc[0], 'visible': True,
                              'labelframe': None, 'only': None}, rows)
                    if len(blockdesc) > 2:
                        block[0]['only'] = blockdesc[2]
                    blocks.append(block)
                columns.append(blocks)
            self._layout.append(columns)

        # maps keys to field-dicts defined in self.layout (see above)
        self._keymap = {}
        # maps "only" entries to block boxes to hide
        self._onlymap = {}
        # remembers loaded setups
        self._setups = set()

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterframe = QFrame(master)
        masterlayout = QVBoxLayout()
        self._timelabel = QLabel('', master)
        self._timelabel.setFont(self._timefont)
        set_forecolor(self._timelabel, self._gray)
        self._timelabel.setAutoFillBackground(True)
        self._timelabel.setAlignment(Qt.AlignHCenter)
        self._timelabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        masterlayout.addWidget(self._timelabel)
        masterlayout.addSpacing(0.5*self._tiheight)

        self._stacker = QStackedWidget(masterframe)
        masterlayout.addWidget(self._stacker)
        displayframe = QFrame(self._stacker)
        self._stacker.addWidget(displayframe)

        def _create_field(groupframe, field):
            fieldlayout = QVBoxLayout()
            # now put describing label and view label into subframe
            l = QLabel(' ' + escape(field['name']) + ' ', groupframe)
            l.setFont(self._labelfont)
            l.setAlignment(Qt.AlignHCenter)
            l.setAutoFillBackground(True)
            l.setTextFormat(Qt.RichText)
            field['namelabel'] = l
            fieldlayout.addWidget(l)

            l = SensitiveLabel('----', groupframe,
                               self._label_entered, self._label_left)
            if field['istext']:
                l.setFont(self._labelfont)
            else:
                l.setFont(self._valuefont)
                l.setAlignment(Qt.AlignHCenter)
            l.setFrameShape(QFrame.Panel)
            l.setFrameShadow(QFrame.Sunken)
            l.setAutoFillBackground(True)
            l.setLineWidth(2)
            l.setMinimumSize(QSize(self._onechar * (field['width'] + .5), 0))
            l.setProperty('assignedField', field)
            field['valuelabel'] = l

            tmplayout = QHBoxLayout()
            tmplayout.addStretch()
            tmplayout.addWidget(l)
            tmplayout.addStretch()
            fieldlayout.addLayout(tmplayout)

            # store reference from key to field for updates
            def _ref(name, key):
                field[name] = key
                self._keymap.setdefault(key, []).append(field)
            if field['dev']:
                _ref('key', prefix + field['dev'].lower() + '/value')
                _ref('statuskey', prefix + field['dev'].lower() + '/status')
                _ref('unitkey', prefix + field['dev'].lower() + '/unit')
                if field['format'] == '%s':  # explicit format has preference
                    _ref('formatkey', prefix + field['dev'].lower() + '/fmtstr')
            else:
                _ref('key', prefix + field['key'])
                if field['statuskey']:
                    _ref('statuskey', prefix + field['statuskey'])
                if field['unitkey']:
                    _ref('unitkey', prefix + field['unitkey'])
                if field['formatkey']:
                    _ref('formatkey', prefix + field['formatkey'])
            return fieldlayout

        # now iterate through the layout and create the widgets to display it
        displaylayout = QVBoxLayout()
        for superrow in self._layout:
            boxlayout = QHBoxLayout()
            boxlayout.setSpacing(20)
            boxlayout.setContentsMargins(10, 10, 10, 10)
            for column in superrow:
                columnlayout = QVBoxLayout()
                columnlayout.setSpacing(self._blheight)
                for block in column:
                    blocklayout_outer = QHBoxLayout()
                    blocklayout_outer.addStretch()
                    blocklayout = QVBoxLayout()
                    blocklayout.addSpacing(0.5*self._blheight)
                    blockbox = BlockBox(displayframe, block[0]['name'],
                                        self._blockfont)
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
                    blocklayout.addSpacing(0.3*self._blheight)
                    blockbox.setLayout(blocklayout)
                    blocklayout_outer.addWidget(blockbox)
                    blocklayout_outer.addStretch()
                    columnlayout.addLayout(blocklayout_outer)
                    columnlayout.addStretch()
                columnlayout.addStretch()
                boxlayout.addLayout(columnlayout)
            displaylayout.addLayout(boxlayout)

        displayframe.setLayout(displaylayout)
        masterframe.setLayout(masterlayout)

        # initialize status bar
        self._statuslabel = QLabel()
        self._statuslabel.setFont(self._stbarfont)
        master.statusBar().addWidget(self._statuslabel)
        self._statustimer = None

        # maps warning keys
        self._warnmap = {}
        # current warnings
        self._currwarnings = []
        self._haswarnings = {}
        # time when warnings were last shown/hidden?
        self._warningswitchtime = 0

        for warning in self.warnings:
            try:
                key, cond, desc, setup = warning
            except:
                key, cond, desc = warning
                setup = None
            self._warnmap[prefix + key] = \
                {'condition': cond, 'description': desc, 'setup': setup}

        self._warnpanel = QFrame(self._stacker)
        self._stacker.addWidget(self._warnpanel)
        master.connect(self._warnpanel, SIGNAL('setindex'),
                       self._stacker.setCurrentIndex)

        warningslayout = QVBoxLayout()
        lbl = QLabel('Warnings', self._warnpanel)
        lbl.setAlignment(Qt.AlignHCenter)
        lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        lbl.setFont(self._timefont)
        warningslayout.addWidget(lbl)
        self._warntext = QLabel('', self._warnpanel)
        self._warntext.setFont(self._blockfont)
        warningslayout.addWidget(self._warntext)
        warningslayout.addStretch()
        self._warnpanel.setLayout(warningslayout)

        master.setCentralWidget(masterframe)

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

    # called between connection attempts
    def _wait_retry(self):
        s = 'Disconnected (%s)' % strftime('%d.%m.%Y %H:%M:%S')
        self._timelabel.setText(s)
        #self._master.setWindowTitle(s)
        sleep(1)

    # called while waiting for data
    def _wait_data(self):
        # update window title and caption with current time
        s = '%s (%s)' % (self.title, strftime('%d.%m.%Y %H:%M:%S'))
        self._timelabel.setText(s)
        #self._master.setWindowTitle(s)

        # adjust the colors of status displays
        newwatch = set()
        for field in self._watch:
            vlabel, status = field['valuelabel'], field['status']
            value = field['value']
            if value is None:
                # no value assigned
                set_fore_backcolor(vlabel, QColor('black'), self._bgcolor)
                continue

            # set name label background color: determined by the value limits

            if field['min'] is not None and value < field['min']:
                set_backcolor(field['namelabel'], self._red)
            elif field['max'] is not None and value > field['max']:
                set_backcolor(field['namelabel'], self._red)
            else:
                set_backcolor(field['namelabel'], self._bgcolor)

            # set the foreground color: determined by the status

            valueage = currenttime() - field['changetime']
            if not status:
                # no status yet, determine on time alone
                if valueage < 3:
                    set_forecolor(vlabel, self._yellow)
                    newwatch.add(field)
                else:
                    set_forecolor(vlabel, self._green)
            else:
                # if we have a status
                try:
                    const = status[0]
                except ValueError:
                    const = status
                if const == OK:
                    set_forecolor(vlabel, self._green)
                elif const in (BUSY, PAUSED):
                    set_forecolor(vlabel, self._yellow)
                elif const in (ERROR, NOTREACHED):
                    set_forecolor(vlabel, self._red)
                else:
                    set_forecolor(vlabel, self._white)

            # set the background color: determined by the value's age

            age = currenttime() - field['time']
            if field['ttl']:
                # allow for a bit of overlap between expiration of ttl and
                # actual value age
                if age > field['ttl'] * 1.5:
                    set_backcolor(vlabel, self._gray)
                else:
                    set_backcolor(vlabel, self._black)
                    newwatch.add(field)
            else:
                set_backcolor(vlabel, self._black)
        self._watch = newwatch
        #self.printdebug('newwatch has %s items' % len(newwatch))

        # check if warnings need to be shown
        if self._currwarnings:
            if currenttime() > self._warningswitchtime + 10:
                if self._stacker.currentIndex() == 0:
                    self._warnpanel.emit(SIGNAL('setindex'), 1)
                else:
                    self._warnpanel.emit(SIGNAL('setindex'), 0)
                self._warningswitchtime = currenttime()

    # called to handle an incoming protocol message
    def _handle_msg(self, time, ttl, tsop, key, op, value):
        if op != OP_TELL:
            return
        try:
            time = float(time)
        except (ValueError, TypeError):
            time = currenttime()
        try:
            ttl = float(ttl)
        except (ValueError, TypeError):
            ttl = None
        try:
            value = cache_load(value)
        except ValueError:
            pass

        #self.printdebug('processing %s=%s' % (key, value))

        if key == self._prefix + '/system/mastersetup':
            self._setups = set(value)
            # reconfigure displayed blocks
            for setup in self._onlymap:
                for layout, blockbox in self._onlymap[setup]:
                    blockbox.emit(SIGNAL('enableDisplay'),
                                  layout, setup in self._setups)
            self.printinfo('reconfigured display for setups %s'
                           % ', '.join(self._setups))

        if key in self._warnmap:
            info = self._warnmap[key]
            try:
                condvalue = eval('__v__ ' + info['condition'],
                                 {'__v__': value})
            except Exception:
                self.printwarning('error evaluating %r warning condition'
                                  % key, exc=1)
            else:
                self._process_warnings(key, info, condvalue)

        # now check if we need to update something
        fields = self._keymap.get(key, [])
        for field in fields:
            self._watch.add(field)
            if key == field['key']:
                if value is None:
                    field['value'] = None
                    field['time'] = 0
                    field['ttl'] = 0
                    field['valuelabel'].setText('----')
                else:
                    oldvalue = field['value']
                    if oldvalue != value:
                        field['changetime'] = time
                    field['value'] = value
                    field['time'] = time
                    field['ttl'] = ttl
                    try:
                        text = field['format'] % value
                    except Exception:
                        text = str(value)
                    field['valuelabel'].setText(text[:field['maxlen']])
            elif key == field['statuskey']:
                field['status'] = value
                field['changetime'] = time
            elif key == field['unitkey']:
                field['unit'] = value
                if value:
                    field['namelabel'].setText(
                        ' ' + escape(field['name']) +
                        ' <font color="#888888">%s</font> ' % escape(value))
            elif key == field['formatkey']:
                field['format'] = value
                if field['value'] is not None:
                    try:
                        field['valuelabel'].setText(field['format'] %
                                                    field['value'])
                    except Exception:
                        field['valuelabel'].setText(str(field['value']))

    def _process_warnings(self, key, info, value):
        if info['setup']:
            value &= info['setup'] in self._setups
        if not value:
            if key not in self._haswarnings:
                return
            self._currwarnings.remove(self._haswarnings.pop(key))
        elif value:
            if key in self._haswarnings:
                return
            warning_desc = strftime('%Y-%m-%d %H:%M') + ' -- ' + \
                           info['description']
            self._currwarnings.append((key, warning_desc))
            self._haswarnings[key] = (key, warning_desc)
        if self._currwarnings:
            set_fore_backcolor(self._timelabel, self._black, self._red)
            self._warntext.setText('\n'.join(w[1] for w in self._currwarnings))
        else:
            set_fore_backcolor(self._timelabel, self._gray, self._bgcolor)
            self._warnpanel.emit(SIGNAL('setindex'), 0)
