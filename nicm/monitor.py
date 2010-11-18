#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Base device classes for use in NICOS
#
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Base device classes for usage in NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import threading
from time import time as currenttime, sleep, strftime

from Tkinter import Tk, Frame, Label, LabelFrame, StringVar, \
     SUNKEN, RAISED, X, W, BOTH, LEFT, TOP, BOTTOM
import tkFont

from nicm.utils import listof
from nicm.status import OK, BUSY, ERROR, PAUSED, NOTREACHED, statuses
from nicm.device import Param
from nicm.cache.client import BaseCacheClient
from nicm.cache.utils import OP_TELL, cache_load

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
        'fontsize':  Param('Basic font size', type=int, default=12),
        'padding':   Param('Padding for the display fields', type=int,
                           default=2),
        'geometry':  Param('Geometry for status window', type=str),
        'resizable': Param('Whether the window is resizable', type=bool,
                           default=True),
    }

    def start(self):
        self.printinfo('monitor starting up, creating main window')
        root = Tk()
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.tk_init(root)

        self._selecttimeout = 0.2
        self._watch = set()
        # now start the worker thread
        self._worker.start()

        self.printinfo('starting main loop')
        # start main loop and wait for termination
        try:
            root.mainloop()
        except KeyboardInterrupt:
            pass
        self._stoprequest = True

    def quit(self):
        self.printinfo('monitor quitting')
        self._stoprequest = True
        self._master.quit()
        self._master.destroy()
        self.printinfo('wait for thread to finish')
        self._worker.join()
        self.printinfo('done')

    def tk_init(self, master):
        self._master = master
        if self.geometry:
            master.geometry(self.geometry)
        if not self.resizable:
            master.resizable(False, False)
        fontsize = self.fontsize
        fontsizebig = int(self.fontsize * 1.2)

        self._bgcolor = master.config('bg')[-1]

        master.title(self.title)
        self._fonts = tkFont.families(master)

        self._timefont  = (self.font, fontsizebig + fontsize)
        self._blockfont = (self.font, fontsizebig)
        self._labelfont = (self.font, fontsize)
        self._stbarfont = (self.font, int(fontsize * 0.8))
        self._valuefont = (self.valuefont or self.font, fontsize)

        # convert configured layout to internal structure
        prefix = self._prefix + '/'
        self._layout = []
        for columndesc in self.layout:
            blocks = []
            for blockdesc in columndesc:
                rows = []
                for rowdesc in blockdesc[1]:
                    fields = []
                    for fielddesc in rowdesc:
                        field = Field({
                            # display/init properties
                            'name': '', 'dev': '', 'width': 10, 'unit': '',
                            'format': '%s', 'min': None, 'max': None,
                            # current values
                            'value': None, 'time': 0, 'ttl': 0, 'status': None,
                            # key names
                            'key': '', 'statuskey': '', 'unitkey': '',
                            'formatkey': '',
                        })
                        field.update(fielddesc)
                        fields.append(field)
                    rows.append(fields)
                block = ({'name': blockdesc[0], 'visible': True,
                          'labelframe': None}, rows)
                blocks.append(block)
            self._layout.append(blocks)

        # maps keys to field-dicts defined in self.layout (see above)
        self._keymap = {}

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to dsiplay blocks.
        # first the timeframe:
        timeframe = Frame(master)
        timeframe.pack(side=TOP, pady=0, ipady=0)
        self._timestring = StringVar()
        l = Label(timeframe, text='', font=self._timefont, fg='darkgrey',
                  textvariable=self._timestring)
        l.grid(row=1)
        self._timelabel = l

        # create the masterframe
        masterframe = Frame(master)
        masterframe.pack(side=TOP, pady=0, fill=X, expand=1)

        def _create_field(subframe, field):
            fieldframe = Frame(subframe)
            # right of previous field or on the leftmost position
            fieldframe.pack(side=LEFT)
            # now put describing label and view label into subframe
            if field['name']:
                l = Label(fieldframe, text=field['name'], font=self._labelfont,
                          width=field['width'] + 2)
                l.grid(row=0)

                field['namelabel'] = l

                s = StringVar(value='----')
                l = Label(fieldframe, text='', pady=2, font=self._valuefont,
                          width=field['width'], relief=SUNKEN, textvariable=s,
                          bg=self._bgcolor, fg='black')
                l.grid(row=1)
                l.bind('<Enter>', self._label_entered)
                l.bind('<Leave>', self._label_left)
                l._field = field

                # store references to Tk objects for later modification
                field['valuevar'] = s
                field['valuelabel'] = l

                # store reference from key to field for updates
                def _ref(name, key):
                    field[name] = key
                    self._keymap.setdefault(key, []).append(field)
                if field['dev']:
                    _ref('key', prefix + field['dev'] + '/value')
                    _ref('statuskey', prefix + field['dev'] + '/status')
                    _ref('unitkey', prefix + field['dev'] + '/unit')
                    _ref('formatkey', prefix + field['dev'] + '/fmtstr')
                else:
                    _ref('key', prefix + field['key'])
                    if field['statuskey']:
                        _ref('statuskey', prefix + field['statuskey'])
                    if field['unitkey']:
                        _ref('unitkey', prefix + field['unitkey'])
                    if field['formatkey']:
                        _ref('formatkey', prefix + field['formatkey'])
            else:
                # invisible field
                l = Label(fieldframe, text='', font=self._labelfont,
                          width=field['width'] + 2)
                l.grid(row=0)
                l = Label(fieldframe, text='', font=self._valuefont,
                          width=field['width'])
                l.grid(row=1)
                field['valuelabel'] = l

        # now iterate through the layout and create the widgets to display it
        for column in self._layout:
            columnframe = Frame(masterframe)
            columnframe.pack(side=LEFT, padx=self.padding, fill=BOTH, expand=1)
            for block in column:
                labelframe = LabelFrame(columnframe, labelanchor='n',
                                        relief=RAISED, text=block[0]['name'],
                                        font=self._blockfont)
                labelframe.pack(ipadx=self.padding, ipady=self.padding,
                                pady=self.padding, side=TOP)
                block[0]['labelframe'] = labelframe
                for row in block[1]:
                    subframe = Frame(labelframe)
                    # blow previous row or on topmost position
                    subframe.pack(side=TOP)
                    for field in row:
                        _create_field(subframe, field)

        # initialize status bar
        self._status = StringVar()
        statusbar = Frame(master)
        statusbar.pack(side=BOTTOM, fill=X, expand=1)
        dist = Label(statusbar)
        dist.pack(side=TOP)
        label = Label(statusbar, relief=SUNKEN, anchor=W, font=self._stbarfont,
                      textvariable=self._status)
        label.pack(side=TOP, pady=0, fill=X)
        self._statustimer = None

    def _label_entered(self, event):
        field = event.widget._field
        statustext = '%s = %s' % (field['name'], field['valuevar'].get())
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
        self._status.set(statustext)
        self._statustimer = threading.Timer(1, lambda: self._label_entered(event))
        self._statustimer.start()

    def _label_left(self, event):
        self._status.set('')
        if self._statustimer:
            self._statustimer.cancel()
            self._statustimer = None

    # called between connection attempts
    def _wait_retry(self):
        s = 'Disconnected (%s)' % strftime('%d.%m.%Y %H:%M:%S')
        self._timestring.set(s)
        self._master.title(s)
        sleep(1)

    # called while waiting for data
    def _wait_data(self):
        # update window title and caption with current time
        s = '%s (%s)' % (self.title, strftime('%d.%m.%Y %H:%M:%S'))
        self._timestring.set(s)
        self._master.title(s)

        # adjust the colors of status displays
        newwatch = set()
        for field in self._watch:
            vlabel, status = field['valuelabel'], field['status']
            value = field['value']
            if value is None:
                # no value assigned
                vlabel.config(bg=self._bgcolor, fg='black')
                continue

            # set name label background color: determined by the value limits

            if field['min'] is not None and value < field['min']:
                field['namelabel'].config(bg='red')
            elif field['max'] is not None and value > field['max']:
                field['namelabel'].config(bg='red')
            else:
                field['namelabel'].config(bg=self._bgcolor)

            # set the foreground color: determined by the status

            age = currenttime() - field['time']
            if not status:
                # no status yet, determine on time alone
                if age < 3:
                    vlabel.config(fg='yellow')
                    newwatch.add(field)
                else:
                    vlabel.config(fg='green')
            else:
                # if we have a status
                try:
                    const = status[0]
                except ValueError:
                    const = status
                if const == OK:
                    vlabel.config(fg='green')
                elif const in (BUSY, PAUSED):
                    vlabel.config(fg='yellow')
                elif const in (ERROR, NOTREACHED):
                    vlabel.config(fg='red')
                else:
                    vlabel.config(fg='white')

            # set the background color: determined by the value's age

            if field['ttl']:
                if age > field['ttl']:
                    vlabel.config(bg='gray40')
                else:
                    vlabel.config(bg='black')
                    newwatch.add(field)
            elif age < 3600:
                vlabel.config(bg='black')
            elif age < 3600*6:
                vlabel.config(bg='gray7')
            elif age < 3600*24:
                vlabel.config(bg='gray13')
            elif age < 3600*24*7:
                vlabel.config(bg='gray27')
            elif age < 3600*24*30:
                vlabel.config(bg='gray40')
            else:
                vlabel.config(bg='gray87', fg='black')
        self._watch = newwatch

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

        # now check if we need to update something
        fields = self._keymap.get(key, [])
        for field in fields:
            self._watch.add(field)
            if key == field['key']:
                if not value:
                    field['value'] = None
                    field['time'] = 0
                    field['ttl'] = 0
                    field['valuevar'].set('----')
                else:
                    field['value'] = value
                    field['time'] = time
                    field['ttl'] = ttl
                    field['valuevar'].set(field['format'] % value)
            elif key == field['statuskey']:
                field['status'] = value
            elif key == field['unitkey']:
                field['unit'] = value
            elif key == field['formatkey']:
                field['format'] = value

        # show/hide blocks, but only if something changed
        if not self._watch:
            return
        for column in self._layout:
            refresh = False
            for block in column:
                valid_data = False
                for row in block[1]:
                    for field in row:
                        if field['valuevar'] and \
                               field['valuevar'].get() != '----':
                            valid_data = True
                if valid_data and not block[0]['visible']:
                    # we have data, but don't show it -> switch on
                    refresh = True
                    block[0]['visible'] = True
                elif not valid_data and block[0]['visible']:
                    # we have no data, but show it -> switch off
                    refresh = True
                    block[0]['visible'] = False
            if refresh:     # if we need to refresh this column
                for block in column:        # hide all
                    block[0]['labelframe'].pack_forget()
                for block in column:        # display needed
                    if block[0]['visible']:
                        block[0]['labelframe'].pack(
                            ipadx=self.padding, ipady=self.padding,
                            pady=self.padding, side=TOP)
