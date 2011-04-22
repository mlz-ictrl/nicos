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

"""Fltk version of instrument monitor."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import sleep

from fltk import Fl, Fl_Window, Fl_Box, Fl_Pack, fl_rgb_color, \
     FL_HORIZONTAL, FL_COURIER, FL_HELVETICA, FL_ALIGN_CENTER, FL_ALIGN_LEFT, \
     FL_FLAT_BOX, FL_THIN_DOWN_BOX, FL_UP_FRAME, FL_SHADOW_FRAME

from nicos.monitor import Monitor as BaseMonitor


class Monitor(BaseMonitor):
    """Fltk specific implementation of instrument monitor."""

    def mainLoop(self):
        while self._master.visible():
            Fl.check()
            sleep(0.1)

    def closeGui(self):
        self._master.hide()
        pass

    def initColors(self):
        self._black = fl_rgb_color(0,0,0)
        self._yellow = fl_rgb_color(255,255,0)
        self._green = fl_rgb_color(0,255,0)
        self._red = fl_rgb_color(255,0,0)
        self._gray = fl_rgb_color(128,128,128)
        self._white = fl_rgb_color(255,255,255)
        self._bgcolor = self._gray

    def initGui(self):
        master = self._master = Fl_Window(0, 0, 1024, 800)

        if self._geometry == 'fullscreen':
            master.fullscreen()
        elif isinstance(self._geometry, tuple):
            master.resize(*self._geometry)

        master.label(self.title)

        self._bgcolor = master.color()

        ##QFontMetrics(self._valuefont).width('0')
        onechar = self._fontsize
        ##QFontMetrics(self._blockfont).height()
        ##QFontMetrics(self._timefont).height()
        tiheight = self._fontsizebig + self._fontsize + 20

        labelfont = FL_HELVETICA
        valuefont = FL_COURIER
        blockfont = FL_HELVETICA
        timefont = FL_HELVETICA+1

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterlayout = Fl_Pack(0, 0, master.w(), master.h())
        self._timelabel = Fl_Box(0, 0, 0, tiheight, self.title)
        self._timelabel.labelfont(timefont)
        self._timelabel.labelsize(self._fontsizebig + self._fontsize)
        self._timelabel.box(FL_FLAT_BOX)

        def _create_field(groupframe, field):
            fieldlayout = Fl_Pack(0, 0, field['width']*onechar, 1)
            fieldlayout.spacing(5)
            # now put describing label and view label into subframe
            l = Fl_Box(0, 0, 0, self._fontsize+5, ' ' + field['name'] + ' ')

            l.labelfont(labelfont)
            l.align(FL_ALIGN_CENTER)
            l.labelsize(self._fontsize)
            l.box(FL_FLAT_BOX)
            field['namelabel'] = l

            l = Fl_Box(0, 0, 0, self._fontsize+10,  '----')
            l.labelcolor(self._white)
            l.labelsize(self._fontsize)
            l.box(FL_THIN_DOWN_BOX)
            l.color(self._black)
            if field['istext']:
                l.align(FL_ALIGN_LEFT)
            else:
                l.labelfont(valuefont)
                l.align(FL_ALIGN_CENTER)
            field['valuelabel'] = l
            fieldlayout.end()

            # store reference from key to field for updates
            self.updateKeymap(field)
            return fieldlayout

        # now iterate through the layout and create the widgets to display it
        for superrow in self._layout:
            boxlayout = Fl_Pack(0, 0, 100, 100)
            boxlayout.type(FL_HORIZONTAL)
            boxlayout.spacing(20)
            #boxlayout.setContentsMargins(10, 10, 10, 10)
            for column in superrow:
                columnlayout = Fl_Pack(0, 0, 100, 100)
                columnlayout.spacing(20)
                for block in column:
                    blocklayout_outer = Fl_Pack(0, 0, 500,500)
                    blocklayout_outer.type(FL_HORIZONTAL)
                    Fl_Box(0, 0, 10, 0).box(FL_SHADOW_FRAME)
                    #blocklayout_outer.addStretch()
                    blockbox = Fl_Pack(0, 0, 1000, 1)#, block[0]['name'])
                    blockbox.align(FL_ALIGN_CENTER)
                    blockbox.labelfont(blockfont)
                    blockbox.labelsize(self._fontsizebig)
                    block[0]['labelframe'] = blockbox
                    for row in block[1]:
                        if row is None:
                            #blocklayout.addSpacing(12)
                            pass
                        else:
                            rowlayout = Fl_Pack(0, 0, 1, 2*self._fontsize+25)
                            rowlayout.type(FL_HORIZONTAL)
                            rowlayout.spacing(self._padding)
                            for field in row:
                                _create_field(blockbox, field)
                            rowlayout.box(FL_UP_FRAME)
                            rowlayout.end()
                    #print rowlayout.w()
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

        self._warnlabel = Fl_Box(0,0,0,0)

        masterlayout.end()
        master.end()
        master.show()

    setLabelText = Fl_Box.label

    def setLabelUnitText(self, label, text, unit):
        label.label(text + ' (%s)' % unit)

    def setForeColor(self, label, fore):
        label.labelcolor(fore)

    def setBackColor(self, label, back):
        label.color(back)

    def setBothColors(self, label, fore, back):
        label.labelcolor(fore)
        label.color(back)

    def switchWarnPanel(self, off=False):
        pass

    def reconfigureBoxes(self):
        pass
