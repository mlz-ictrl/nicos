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

import gc
import os
import time
import select
import socket
import threading

from Tkinter import Tk, Frame, Label, LabelFrame, StringVar, \
     SUNKEN, RAISED, X, BOTH, LEFT, TOP
import tkFont

from nicm.device import Device
from nicm.utils import listof


FONTLIST = 'Luxi Sans,FreeSans,Utopia,Helvetica,Verdana,' \
           'Nimbus Sans L, Bitstream Vera Sans'.split(',')

class Monitor(Device):

    parameters = {
        # XXX add more configurables: geometry, fonts, font sizes, timeouts ...
        'title': (str, 'Status', False, 'Title of status window.'),
        'cache': (str, '', True, 'host:port address of cache server.'),
        'layout': (listof(list), None, True, 'Status monitor layout.'),
    }

    def start(self):
        self._stoprequest = False

        self.printinfo('monitor starting up, creating main window')
        gc.set_threshold(100, 10, 3)  # XXX needed?
        root = Tk()
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.tk_init(root)

        self._watch = []
        # now start updatethread
        self._updatethread = threading.Thread(target=self._update_thread)
        self._updatethread.setDaemon(True)
        self._updatethread.start()

        self.printinfo('starting main loop')
        # start main loop and wait for termination
        root.mainloop()
        self._stoprequest = True

    def tk_init(self, master):
        self._master = master
        #if socket.gethostname() == 'pandadiag.panda.frm2':
        #    master.geometry('1920x1200+0+0')
        #    master.resizable(False,False)
        #    fontsize = 24
        #    fontsizebig = 28
        #    self._padding = 8
        #else:
        fontsize = 12
        fontsizebig = 14
        self._padding = 2

        master.title(self.title)
        self._fonts = tkFont.families(master)
        font = 'Luxi Sans'
        for f in FONTLIST:
            if f in self._fonts:
                font = f
                break

        self._timefont  = (font, fontsizebig + fontsize)
        self._blockfont = (font, fontsizebig)
        self._labelfont = (font, fontsize)
        self._valuefont = (font, fontsize)

        self._layout = []
        for columndesc in self.layout:
            blocks = []
            for blockdesc in columndesc:
                rows = []
                for rowdesc in blockdesc['rows']:
                    fields = []
                    for fielddesc in rowdesc:
                        field = {
                            'timestamp': 0, 'status': '', 'block': None,
                            'width': 10, 'name': '', 'format': '%s',
                            'key': '', 'namelabel': None, 'valuelabel': None,
                            'valuevar': None, 'defaultvalue': None
                        }
                        field.update(fielddesc)
                        fields.append(field)
                    rows.append(fields)
                block = [{'name': blockdesc['name'],
                          'visible': True, 'labelframe': None}] + rows
                blocks.append(block)
            self._layout.append(blocks)
        #print self._layout

        # maps keys to field-dicts defined in self.layout (see above)
        self._keymap = {}

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to dsiplay blocks.
        # first the timeframe:
        timeframe = Frame(master)
        timeframe.pack(side=TOP, pady=0, ipady=0)
        self._timestring = StringVar()
        self._timestring.set('%s (%s)' % (self.title,
                                          time.strftime('%d.%m.%Y  %H:%M:%S')))
        l = Label(timeframe, text='',
                  font=self._timefont,
                  textvariable=self._timestring,
                  fg='darkgrey')
        l.grid(row=1)
        self._timelabel = l

        # now the masterframe
        masterframe = Frame(master)
        masterframe.pack(side=TOP, pady=0, fill=X, expand=1)

        # now iterate through the layout, make necessary changes and create widgets
        for column in self._layout:
            columnframe = Frame(masterframe)
            columnframe.pack(side=LEFT, padx=self._padding, fill=BOTH, expand=1)
            for block in column:
                labelframe = LabelFrame(columnframe, labelanchor='n',
                                        relief=RAISED, text=block[0]['name'],
                                        font=self._blockfont)
                labelframe.pack(ipadx=self._padding, ipady=self._padding,
                                pady=self._padding, side=TOP)
                block[0]['labelframe'] = labelframe
                for row in block[1:]:
                    subframe = Frame(labelframe)
                    # blow previous row or on topmost position
                    subframe.pack(side=TOP)
                    for field in row:
                        fieldframe = Frame(subframe)
                        # right of previous field or on the leftmost position
                        fieldframe.pack(side=LEFT)
                        # store reference to common block, used for
                        # hiding/unhiding of unused blocks
                        field['block'] = block
                        # now put describing label and view label into subframe
                        if field['name']:
                            l = Label(fieldframe, text=field['name'],
                                      font=self._labelfont,
                                      width=field['width'] + 2)
                            l.grid(row=0)
                            field['namelabel'] = l

                            s = StringVar()
                            if field['defaultvalue']:
                                s.set(field['defaultvalue'])
                            else:
                                s.set('----')
                            field['valuevar'] = s
                            l = Label(fieldframe, text='', font=self._valuefont,
                                      width=field['width'], relief=SUNKEN,
                                      textvariable=s, fg='black', pady=2)
                            l.grid(row=1)
                            field['valuelabel'] = l

                            k = field['key']
                            # store reference from key to field for updates
                            self._keymap.setdefault(k, []).append(field)
                            # replace rightmost non-slash-string with status
                            # XXX
                            k = k[:k.rfind('/')+1] + 'status'
                            self._keymap.setdefault(k, []).append(field)
                        else:
                            # disabled field
                            l = Label(fieldframe, text='', font=self._labelfont,
                                      width=field['width'] + 2)
                            l.grid(row=0)
                            field['namelabel'] = l
                            l = Label(fieldframe, text='', font=self._valuefont,
                                      width=field['width'])
                            l.grid(row=1)
                            field['valuelabel'] = l

    def _update_thread(self):
        data = newdata = ''
        sock = None

        while not self._stoprequest:
            if newdata is None or newdata == '':
                # first round or network problem, close socket, if still open
                if sock:
                    try: sock.shutdown(socket.SHUT_RDWR)
                    except: pass
                    try: sock.close()
                    except: pass
                    sock = None
                # open new socket and connect
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # connect to server
                try:
                    host, port = self.cache.split(':')
                    port = int(port)
                except ValueError:
                    host = self.cache
                    port = 14869
                try:
                    sock.connect((host, port))
                    # send request for all keys and updates....
                    q = '@?\r\n@!\r\n'
                    while q:
                        sent = sock.send(q)
                        q = q[sent:]
                    # prepare for getting a response
                    data = ''
                except: # something went wrong (connect or send)
                    try: sock.shutdown(socket.SHUT_RDWR)
                    except: pass
                    try: sock.close()
                    except: pass
                    sock = None   # mark as not connected
                    time.sleep(5)
                    newdata = ''

            if not sock:
                s = 'Unconnected (%s)' % time.strftime('%d.%m.%Y  %H:%M:%S')
                self._timestring.set(s)
                self._master.title(s)
                time.sleep(1)
                continue

            # read data until at least one line is complete...
            # also limit line length (just in case)
            while data.find('\n') * data.find('\r') == 1 and \
                      not self._stoprequest and len(data) < 65536 and sock:

                # update primary status with time
                s = '%s (%s)' % (self.title, time.strftime('%d.%m.%Y  %H:%M:%S'))
                self._timestring.set(s)
                self._master.title(s)

                # updates colors
                currenttime = time.time()
                # try to read some data, use a timeout of 0.1 sec
                p = select.select([sock], [], [sock], 0.1)
                if sock in p[0]:
                    # got some data
                    newdata = sock.recv(8192)
                    if not newdata:
                        # no new data from blocking read -> abort
                        break
                    data += newdata
                # now adjust colors
                newwatch = []
                for field in self._watch:
                    age = time.time() - field['timestamp']
                    if not field['status']:
                        # no status yet, determine on time alone
                        if age < 3:
                            field['valuelabel'].config(fg='yellow')
                            newwatch.append(field)
                        else:
                            field['valuelabel'].config(fg='green')
                    # if we have a status
                    elif field['status'] == 'idle':
                        field['valuelabel'].config(fg='green')
                    elif field['status'] in ['busy', 'moving',
                                             'switching', 'working']:
                        field['valuelabel'].config(fg='yellow')
                    elif field['status'] in ['error', 'unknown']:
                        field['valuelabel'].config(fg='red')
                    else:
                        field['valuelabel'].config(fg='white')
                    if field['valuevar'].get() == '----':
                        # no value (yet)
                        field['valuelabel'].config(bg='#dddddd', fg='#000000')
                    elif field['timestamp'] < 0:
                        field['valuelabel'].config(bg='#000000')
                    else:
                        if age < 3600:
                            field['valuelabel'].config(bg='#000000')
                        elif age < 3600*6:
                            field['valuelabel'].config(bg='#111111')
                        elif age < 3600*24:
                            field['valuelabel'].config(bg='#222222')
                        elif age < 3600*24*7:
                            field['valuelabel'].config(bg='#444444')
                        elif age < 3600*24*30:
                            field['valuelabel'].config(bg='#666666')
                        else:
                            field['valuelabel'].config(bg='#dddddd', fg='black')
                self._watch = newwatch
            # end of while loop
            if self._stoprequest:
                try: sock.shutdown(socket.SHUT_RDWR)
                except: pass
                try: sock.close()
                except: pass
                sock = None
                return
            # now evaluate the response
            if len(data) > 65535:
                newdata = ''
            if not data or not newdata:
                continue

            line = data.splitlines()[0]           # only use first line/result
            data = data[len(line):]               # remove line from data
            data = data.rstrip('\r\n')

            p = line.find('=')    # splits response into key,separator, value
            if p != -1:   # ignore malformed lines
                # extract key and value
                value = line[p+1:].strip()
                key = line[:p].lower().strip()
                # check for timestamp
                p = key.find('@')
                if p > -1:
                    # extract timing information
                    try: currenttime = float(key[:p])
                    except: currenttime = 0.0     # catch conversion errors
                    if currenttime < 0:
                        # conversion error, or values with a remaining time to
                        # live....-> use current time
                        currenttime = time.time()
                    # remove timing from remaining key
                    key = key[p+1:].strip()     # as key we don't use the timestamp!
                # now check if we need to update something
                fields = self._keymap.get(key, [])
                for field in fields:        # key is there
                    self._watch.append(field)
                    if key[-6:] != 'status':      # value-update, not status-update
                        if value == '':
                            field['timestamp'] = 0.0
                            field['valuevar'].set('----') # default value
                        else:
                            field['timestamp'] = currenttime
                            try:
                                field['valuevar'].set(field['format'] % value)
                            except:
                                try:
                                    field['valuevar'].set(field['format'] %
                                                          float(value))
                                except:
                                    field['valuevar'].set(value)

                    else:      # status-update
                        if 0 < field['timestamp'] < currenttime:
                            # don't change if old value is negative or new value
                            # is less
                            field['timestamp'] = currenttime
                        field['status'] = value

                # now switch on/off blocks
                if self._watch:  # only check of something changed
                    for column in self._layout:
                        refresh = False
                        for block in column:
                            valid_data = False
                            for row in block[1:]:
                                for field in row:
                                    if field['valuevar'] and \
                                           field['valuevar'].get() != '----':
                                        valid_data=True
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
                                        ipadx=self._padding,
                                        ipady=self._padding,
                                        pady=self._padding, side=TOP)

    def quit(self):
        self.printinfo('monitor quitting')
        self._stoprequest = True
        self._master.quit()
        self._master.destroy()
        self.printinfo('wait for thread to finish')
        self._updatethread.join()
        self.printinfo('done')
