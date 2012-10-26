#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Tkinter version of instrument monitor."""

__version__ = "$Revision$"

from Tkinter import Tk, Frame, Label, LabelFrame, StringVar, \
     SUNKEN, RAISED, X, BOTH, LEFT, TOP

from nicos.monitor import Monitor as BaseMonitor

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


class Monitor(BaseMonitor):
    """Tkinter specific implementation of instrument monitor."""

    def mainLoop(self):
        self._master.mainloop()

    def closeGui(self):
        self._master.quit()
        self._master.destroy()

    def initColors(self):
        self._bgcolor = 'gray'
        self._black = 'black'
        self._yellow = 'yellow'
        self._green = '#00ff00'
        self._red = 'red'
        self._gray = 'gray'
        self._white = 'white'

    def initGui(self):
        self._master = master = Tk()
        master.protocol('WM_DELETE_WINDOW', self.quit)
        master.bind('q', self.quit)
        if self._geometry:
            if isinstance(self._geometry, tuple):
                master.geometry('%sx%s+%s+%s' % self._geometry)
            else:
                pass
        if not self.resizable:
            master.resizable(False, False)

        self._bgcolor = master.config('bg')[-1]

        master.title(self.title)

        timefont  = (self.font, self._fontsizebig + self._fontsize)
        blockfont = (self.font, self._fontsizebig)
        labelfont = (self.font, self._fontsize)
        valuefont = (self.valuefont or self.font, self._fontsize)

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to dsiplay blocks.
        # first the timeframe:
        timeframe = Frame(master)
        timeframe.pack(side=TOP, pady=0, ipady=0)
        timestring = StringVar()
        l = Label(timeframe, text='', font=timefont, fg='darkgrey',
                  textvariable=timestring)
        l.grid(row=1)
        l._var = timestring
        self._timelabel = l

        # create the masterframe
        masterframe = Frame(master)
        masterframe.pack(side=TOP, pady=0, fill=X, expand=1)

        def _create_field(subframe, field):
            fieldframe = Frame(subframe)
            # right of previous field or on the leftmost position
            fieldframe.pack(side=LEFT)
            # now put describing label and view label into subframe
            s = StringVar(value=field['name'])
            l = Label(fieldframe, text='', font=labelfont,
                      width=field['width'] + 2, textvariable=s)
            l.grid(row=0)
            l._var = s
            if field['unit']:
                self.setLabelUnitText(l, field['name'], field['unit'])

            # store references to Tk object for later modification
            field['namelabel'] = l

            s = StringVar(value='----')
            l = Label(fieldframe, text='', pady=2, font=valuefont,
                      width=field['width'], relief=SUNKEN, textvariable=s,
                      bg=self._bgcolor, fg='black')
            l.grid(row=1)
            l._field = field
            l._var = s

            field['valuelabel'] = l

            # deactivate all plots
            field['plot'] = None

            self.updateKeymap(field)

        # now iterate through the layout and create the widgets to display it
        for superrow in self._layout:
            superrowframe = Frame(masterframe)
            superrowframe.pack(side=TOP, pady=self._padding)
            for column in superrow:
                columnframe = Frame(superrowframe)
                columnframe.pack(side=LEFT, padx=self._padding, fill=BOTH,
                                 expand=1)
                for block in column:
                    labelframe = LabelFrame(columnframe, labelanchor='n',
                                            relief=RAISED, text=block[0]['name'],
                                            font=blockfont)
                    labelframe.pack(ipadx=self._padding, ipady=self._padding,
                                    pady=self._padding, side=TOP)
                    block[0]['labelframe'] = labelframe
                    for row in block[1]:
                        subframe = Frame(labelframe)
                        if row is None:
                            subframe.pack(side=TOP, ipady=self._padding*2)
                        else:
                            subframe.pack(side=TOP)
                            for field in row:
                                _create_field(subframe, field)

        # warnings label
        s = StringVar()
        self._warnlabel = Label(master, textvariable=s)
        self._warnlabel._var = s

    def setLabelText(self, label, text):
        label._var.set(text)

    def setLabelUnitText(self, label, text, unit, fixed=''):
        if unit.strip():
            label._var.set(text + ' (%s)%s' % (unit, fixed))
        else:
            label._var.set(text)

    def setForeColor(self, label, color):
        label.config(fg=color)

    def setBackColor(self, label, color):
        label.config(bg=color)

    def setBothColors(self, label, fore, back):
        label.config(fg=fore, bg=back)

    def switchWarnPanel(self, off=False):
        pass

    def reconfigureBoxes(self):
        pass
