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
from nicm.status import OK, BUSY, ERROR, PAUSED, NOTREACHED
from nicm.cache.client import BaseCacheClient
from nicm.cache.utils import OP_TELL

def nicedelta(t):
    if t < 60:
        return '%d seconds' % int(t)
    elif t < 3600:
        return '%.1f minutes' % (t / 60.)
    else:
        return '%.1f hours' % (t / 3600.)


class Monitor(BaseCacheClient):

    # server and prefix parameters come from BaseCacheClient
    parameters = {
        # XXX add more configurables: timeouts ...
        'title': (str, 'Status', False, 'Title of status window.'),
        'layout': (listof(list), None, True, 'Status monitor layout.'),
        'font': (str, 'Luxi Sans', False, 'Font name for the window.'),
        'valuefont': (str, '', False, 'Font name for the value displays.'),
        'fontsize': (int, 12, False, 'Basic font size.'),
        'padding': (int, 2, False, 'Padding for the display fields.'),
        'geometry': (str, '', False, 'Geometry for status window.'),
        'resizable': (bool, True, False, 'Whether the window is resizable.'),
    }

    def start(self):
        self.printinfo('monitor starting up, creating main window')
        root = Tk()
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.tk_init(root)

        self._selecttimeout = 0.1
        self._watch = []
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
                        field = {
                            # display properties
                            'name': '', 'key': '', 'width': 10, 'unit': '',
                            'format': '%s',
                            # current values
                            'timestamp': 0, 'status': '',
                        }
                        field.update(fielddesc)
                        field['key'] = prefix + field['key']
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

                s = StringVar(value='----')
                l = Label(fieldframe, text='', pady=2, font=self._valuefont,
                          width=field['width'], relief=SUNKEN, textvariable=s,
                          bg='#dddddd', fg='#000000')
                l.grid(row=1)
                l.bind('<Enter>', self._label_entered)
                l.bind('<Leave>', self._label_left)
                l._field = field

                # store references to Tk objects for later modification
                field['valuevar'] = s
                field['valuelabel'] = l

                # store reference from key to field for updates
                key = field['key']
                self._keymap.setdefault(key, []).append(field)
                # replace rightmost non-slash-string with status XXX
                statuskey = key[:key.rfind('/')+1] + 'status'
                self._keymap.setdefault(statuskey, []).append(field)
            else:
                # disabled field
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
        if field['timestamp']:
            statustext += ', value updated %s ago' % (
                nicedelta(currenttime() - field['timestamp']))
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
        newwatch = []
        for field in self._watch:
            vlabel, status = field['valuelabel'], field['status']
            age = currenttime() - field['timestamp']
            if not status:
                # no status yet, determine on time alone
                if age < 3:
                    vlabel.config(fg='yellow')
                    newwatch.append(field)
                else:
                    vlabel.config(fg='green')
            # if we have a status
            elif status == OK:
                vlabel.config(fg='green')
            elif status in (BUSY, PAUSED):
                vlabel.config(fg='yellow')
            elif status in (ERROR, NOTREACHED):
                vlabel.config(fg='red')
            else:
                vlabel.config(fg='white')
            if field['valuevar'].get() == '----':
                # no value (yet)
                vlabel.config(bg='#dddddd', fg='#000000')
            elif field['timestamp'] < 0:
                vlabel.config(bg='#000000')
            else:
                if age < 3600:
                    vlabel.config(bg='#000000')
                elif age < 3600*6:
                    vlabel.config(bg='#111111')
                elif age < 3600*24:
                    vlabel.config(bg='#222222')
                elif age < 3600*24*7:
                    vlabel.config(bg='#444444')
                elif age < 3600*24*30:
                    vlabel.config(bg='#666666')
                else:
                    vlabel.config(bg='#dddddd', fg='black')
        self._watch = newwatch

    # called to handle an incoming protocol message
    def _handle_msg(self, time, ttl, tsop, key, op, value):
        if op != OP_TELL:
            return
        try:
            time = float(time)
        except (ValueError, TypeError):
            time = currenttime()
        # now check if we need to update something
        fields = self._keymap.get(key, [])
        for field in fields:
            self._watch.append(field)
            if key[-6:] != 'status':      # value-update, not status-update
                if not value:
                    field['timestamp'] = 0.0
                    field['valuevar'].set('----') # default value
                else:
                    field['timestamp'] = time
                    try:
                        field['valuevar'].set(field['format'] % value)
                    except:
                        try:
                            field['valuevar'].set(field['format'] %
                                                  float(value))
                        except:
                            field['valuevar'].set(value)

            else:      # status-update
                if 0 < field['timestamp'] < time:
                    # don't change if old value is negative or new value is less
                    field['timestamp'] = time
                field['status'] = value

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
