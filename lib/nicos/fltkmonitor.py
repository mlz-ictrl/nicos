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

#from PyQt4.QtCore import QSize, QPoint, Qt
#from PyQt4.QtGui import QFrame, QLabel, QPalette, QMainWindow, QVBoxLayout, \
 #    QColor, QFont, QFontMetrics, QSizePolicy, QHBoxLayout, QApplication, \
#     QCursor
from fltk import *

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

#~ class MonitorWindow(QMainWindow):
    #~ def keyPressEvent(self, event):
        #~ if event.text() == 'q':
            #~ self.close()
        #~ return QMainWindow.keyPressEvent(self, event)

#~ class SensitiveLabel(QLabel):
    #~ """A label that calls back when entered/left by the mouse."""
    #~ def __init__(self, text, parent, enter, leave):
        #~ QLabel.__init__(self, text, parent)
        #~ self._enter = enter
        #~ self._leave = leave
    #~ def enterEvent(self, event):
        #~ self._enter(self, event)
    #~ def leaveEvent(self, event):
        #~ self._leave(self, event)

#~ class BlockBox(QFrame):
    #~ """Provide the equivalent of a Tk LabelFrame: a group box that has a
    #~ definite frame around it.
    #~ """
    #~ def __init__(self, parent, text, font):
        #~ QFrame.__init__(self, parent)
        #~ self._label = QLabel(' ' + text + ' ', parent)
        #~ self._label.setAutoFillBackground(True)
        #~ self._label.setFont(font)
        #~ self._label.resize(self._label.sizeHint())
        #~ self._label.show()
        #~ self.setFrameShape(QFrame.Panel)
        #~ self.setFrameShadow(QFrame.Raised)
        #~ self.setLineWidth(2)
    #~ def moveEvent(self, event):
        #~ self._repos()
        #~ return QFrame.moveEvent(self, event)
    #~ def resizeEvent(self, event):
        #~ self._repos()
        #~ return QFrame.resizeEvent(self, event)
    #~ def _repos(self):
        #~ mps = self.pos()
        #~ msz = self.size()
        #~ lsz = self._label.size()
        #~ self._label.move(mps.x() + 0.5*(msz.width() - lsz.width()),
                         #~ mps.y() - 0.5*lsz.height())
    #~ #def setVisible(self, isvis):
    #~ #    QFrame.setVisible(self, isvis)
    #~ #    self._label.setVisible(isvis)

#~ def set_forecolor(label, fore):
    #~ pal = label.palette()
    #~ pal.setColor(QPalette.WindowText, fore)
    #~ label.setPalette(pal)

#~ def set_backcolor(label, back):
    #~ pal = label.palette()
    #~ pal.setColor(QPalette.Window, back)
    #~ label.setPalette(pal)

#~ def set_fore_backcolor(label, fore, back):
    #~ pal = label.palette()
    #~ pal.setColor(QPalette.WindowText, fore)
    #~ pal.setColor(QPalette.Window, back)
    #~ label.setPalette(pal)


class Monitor(BaseCacheClient):

    # server and prefix parameters come from BaseCacheClient
    parameters = {
        # XXX add more configurables: timeouts ...
        'title':     Param('Title of status window', type=str,
                           default='Status'),
        'layout':    Param('Status monitor layout', type=listof(list),
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
        self.printinfo('Fltk monitor starting up, creating main window')

        self._fontsize = options.fontsize or self.fontsize
        self._padding  = options.padding or self.padding
        self._geometry = options.geometry or self.geometry

        window = Fl_Window(0, 0, 1024, 800)
        self.ui_init(window)
        window.end()

        self._selecttimeout = 0.2
        self._watch = set()
        # now start the worker thread
        self._worker.start()

        self.printinfo('starting main loop')
        # start main loop and wait for termination
        window.show()
        try:
            while not self._stoprequest:
                Fl.check()
                sleep(0.1)
        except KeyboardInterrupt:
            pass
        self._stoprequest = True

    def wait(self):
        self.printinfo('monitor quitting')
        self._worker.join()
        self.printinfo('done')

    def quit(self, *ignored):
        #self._master.close()
        self._stoprequest = True

    def ui_init(self, master):
        self._master = master
        #~ if self._geometry:
            #~ if self._geometry == 'fullscreen':
                #~ master.showMaximized()
                #~ QCursor.setPos(master.geometry().bottomRight())
                #~ #QCursor.setPos(
                #~ #    master.mapToGlobal(QPoint(sz.width(), sz.height())))
            #~ else:
                #~ try:
                    #~ w, h, x, y = map(int, re.match('(\d+)x(\d+)+(\d+)+(\d+)',
                                                   #~ self._geometry).groups())
                #~ except Exception:
                    #~ self.printwarning('invalid geometry %s' % self._geometry)
                #~ else:
                    #~ master.setGeometry(x, y, w, h)
        fontsize = self._fontsize
        fontsizebig = int(self._fontsize * 1.2)

        self._black = fl_rgb_color(0,0,0)
        self._yellow = fl_rgb_color(255,255,0)
        self._green = fl_rgb_color(0,255,0)
        self._red = fl_rgb_color(255,0,0)
        self._gray = fl_rgb_color(128,128,128)
        self._white = fl_rgb_color(255,255,255)
        self._bgcolor = self._gray#master.palette().color(QPalette.Window)

        master.label(self.title)

        #self._timefont  = QFont(self.font, fontsizebig + fontsize)
        #self._blockfont = QFont(self.font, fontsizebig)
        #self._labelfont = QFont(self.font, fontsize)
        #self._stbarfont = QFont(self.font, int(fontsize * 0.8))
        #self._valuefont = QFont(self.valuefont or self.font, fontsize)

        self._onechar = 5 ##QFontMetrics(self._valuefont).width('0')
        self._blheight = 20 ##QFontMetrics(self._blockfont).height()
        self._tiheight = 20 ##QFontMetrics(self._timefont).height()

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

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterlayout = Fl_Pack(0, 0, 1024, 800)
        self._timelabel = Fl_Box(0, 0, 0, 35, self.title)
        self._timelabel.labelsize(28)
        #masterlayout.add(self._timelabel)
        
        
        #master.add(masterlayout)
        #masterframe = QFrame(master)
        #masterlayout = QVBoxLayout()
        #self._timelabel = QLabel('', master)
        #self._timelabel.setFont(self._timefont)
        #set_forecolor(self._timelabel, self._gray) 
        #self._timelabel.setAlignment(Qt.AlignHCenter)
        #self._timelabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        #masterlayout.addWidget(self._timelabel)
        #masterlayout.addSpacing(0.5*self._tiheight)

        def _create_field(groupframe, field):
            fieldlayout = Fl_Pack(0, 0, 100, 10)
            fieldlayout.spacing(5)
            # now put describing label and view label into subframe
            l = Fl_Box(0, 0, 0, 20, ' ' + field['name'] + ' ')
            #l.setFont(self._labelfont)
            l.align(FL_ALIGN_CENTER)
            field['namelabel'] = l

            l = Fl_Box(0, 0, 0, 30,  '----')
            l.labelcolor(self._white)
            l.color2(self._black)
            if field['istext']:
                #l.setFont(self._labelfont)
                l.align(FL_ALIGN_LEFT)
            else:
                l.labelfont(FL_COURIER)
                l.align(FL_ALIGN_CENTER)
            l.box(FL_THIN_DOWN_FRAME)
            #l.setMinimumSize(QSize(self._onechar * (field['width'] + .5), 0))
            #l.setProperty('assignedField', field)
            field['valuelabel'] = l

            #tmplayout = QHBoxLayout()
            #tmplayout.addStretch()
            #tmplayout.addWidget(l)
            #tmplayout.addStretch()
            #fieldlayout.addLayout(tmplayout)

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
            fieldlayout.end()

        # now iterate through the layout and create the widgets to display it
        for superrow in self._layout:
            boxlayout = Fl_Pack(0, 0, 100, 100)
            boxlayout.type(FL_HORIZONTAL)
            boxlayout.spacing(20)
            #boxlayout.setContentsMargins(10, 10, 10, 10)
            for column in superrow:
                columnlayout = Fl_Pack(0, 0, 100, 100)
                columnlayout.spacing(self._blheight)
                for block in column:
                    blocklayout_outer = Fl_Pack(0, 0, 500,500)
                    blocklayout_outer.type(FL_HORIZONTAL)
                    Fl_Box(0, 0, 10, 0).box(FL_SHADOW_BOX)
                    #blocklayout_outer.addStretch()
                    blockbox = Fl_Pack(0, 0, 5000, 1000)#, block[0]['name'])
                    blockbox.align(FL_ALIGN_CENTER)
                    #blockbox.labelsize(20)
                    block[0]['labelframe'] = blockbox
                    for row in block[1]:
                        if row is None:
                            #blocklayout.addSpacing(12)
                            pass
                        else:
                            rowlayout = Fl_Pack(0, 0, 500, 70)
                            rowlayout.type(FL_HORIZONTAL)
                            rowlayout.spacing(self._padding)
                            #rowlayout.addStretch()
                            for field in row:
                                _create_field(blockbox, field)
                            #rowlayout.addStretch()
                            rowlayout.box(FL_UP_FRAME)
                            rowlayout.end()
                    ##if block[0]['only']:
                     ##   self._onlymap.setdefault(block[0]['only'], []).\
                     ##       append((blocklayout_outer, blockbox))
                    #blockbox.resizable(rowlayout)
                    blockbox.box(FL_UP_FRAME)
                    blockbox.end()
                    #blocklayout_outer.addStretch()
                    blocklayout_outer.box(FL_SHADOW_FRAME)
                    blocklayout_outer.end()
                    #columnlayout.addLayout(blocklayout_outer)
                    #columnlayout.addStretch()
                #columnlayout.addStretch()
                columnlayout.end()
            boxlayout.end()

        masterlayout.end()

    # called between connection attempts
    def _wait_retry(self):
        s = 'Disconnected (%s)' % strftime('%d.%m.%Y %H:%M:%S')
        self._timelabel.label(s)
        #self._master.setWindowTitle(s)
        sleep(1)

    # called while waiting for data
    def _wait_data(self):
        # update window title and caption with current time
        s = '%s (%s)' % (self.title, strftime('%d.%m.%Y %H:%M:%S'))
        self._timelabel.label(s)
        #self._master.setWindowTitle(s)

        # adjust the colors of status displays
        newwatch = set()
        for field in self._watch:
            vlabel, status = field['valuelabel'], field['status']
            value = field['value']
            if value is None:
                # no value assigned
                vlabel.labelcolor(self._black)
                vlabel.color(self._bgcolor)
                continue

            # set name label background color: determined by the value limits

            if field['min'] is not None and value < field['min']:
                field['namelabel'].color(self._red)
            elif field['max'] is not None and value > field['max']:
                field['namelabel'].color(self._red)
            else:
                field['namelabel'].color(self._bgcolor)

            # set the foreground color: determined by the status

            valueage = currenttime() - field['changetime']
            if not status:
                # no status yet, determine on time alone
                if valueage < 3:
                    vlabel.labelcolor(self._yellow)
                    newwatch.add(field)
                else:
                    vlabel.labelcolor(self._green)
            else:
                # if we have a status
                try:
                    const = status[0]
                except ValueError:
                    const = status
                if const == OK:
                    vlabel.labelcolor(self._green)
                elif const in (BUSY, PAUSED):
                    vlabel.labelcolor(self._yellow)
                elif const in (ERROR, NOTREACHED):
                    vlabel.labelcolor(self._red)
                else:
                    vlabel.labelcolor(self._white)

            # set the background color: determined by the value's age

            age = currenttime() - field['time']
            if field['ttl']:
                # allow for a bit of overlap between expiration of ttl and
                # actual value age
                if age > field['ttl'] * 1.5:
                    vlabel.color(self._gray)
                else:
                    vlabel.color(self._black)
                    newwatch.add(field)
            else:
                vlabel.color(self._black)
        self._watch = newwatch
        #self.printdebug('newwatch has %s items' % len(newwatch))

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

        #~ if key == self._prefix + '/system/mastersetup':
            #~ setups = set(value)
            #~ # reconfigure displayed blocks
            #~ for setup in self._onlymap:
                #~ for layout, blockbox in self._onlymap[setup]:
                    #~ if setup in setups:
                        #~ blockbox.setVisible(True)
                        #~ layout.insertWidget(1, blockbox)
                    #~ else:
                        #~ blockbox.setVisible(False)
                        #~ layout.removeWidget(blockbox)
            #~ self.printinfo('reconfigured display for setups %s' % setups)

        # now check if we need to update something
        fields = self._keymap.get(key, [])
        for field in fields:
            self._watch.add(field)
            if key == field['key']:
                if value is None:
                    field['value'] = None
                    field['time'] = 0
                    field['ttl'] = 0
                    field['valuelabel'].label('----')
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
                    field['valuelabel'].label(text[:field['maxlen']])
            elif key == field['statuskey']:
                field['status'] = value
                field['changetime'] = time
            elif key == field['unitkey']:
                field['unit'] = value
                if value:
                    field['namelabel'].label(
                        ' ' + escape(field['name']) +
                        ' %s ' % escape(value))
            elif key == field['formatkey']:
                field['format'] = value
                if field['value'] is not None:
                    try:
                        field['valuelabel'].label(field['format'] %
                                                    field['value'])
                    except Exception:
                        field['valuelabel'].label(str(field['value']))
