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

from fltk import Fl, Fl_Double_Window, Fl_Group, Fl_Widget, Fl_Box, \
     FL_COURIER, FL_HELVETICA, FL_FLAT_BOX, FL_UP_FRAME, FL_BOLD, FL_GRAY, \
     FL_ALIGN_TOP_LEFT, FL_DOWN_BOX, fl_rgb_color, fl_font, fl_measure

from nicos.monitor import Monitor as BaseMonitor


def measure(font, fontsize, text):
    fl_font(font, fontsize)
    return fl_measure(text)


class Fll_Layout(Fl_Group):
    stretch = 1

    def __init__(self, spacing=0, padx=0, pady=0):
        Fl_Group.__init__(self, 0, 0, 0, 0)
        self._childinfo = []
        self._minheight = self._minwidth = 0
        self._spacing = spacing
        self._padx = padx
        self._pady = pady
        self._stretchers = {0: 0, 1: 0, 2: 0}
        self._children = []
        self.current(None)

    def pack(self, child, stretch=None):
        self._children.append(child)
        if hasattr(child, 'preferredsize'):
            w, h = child.preferredsize()
        else:
            w, h = child.w(), child.h()
        if stretch is None:
            stretch = getattr(child, 'stretch', 0)
        self._stretchers[stretch] += 1
        self._childinfo.append([w, h, stretch, True])
        self.add(child)
        self._calc_minsize()

    def showchild(self, child, show):
        self._childinfo[self._children.index(child)][3] = show

    def updatelayout(self):
        for i, child in enumerate(self._children):
            if isinstance(child, Fll_Layout):
                child.updatelayout()
                self._childinfo[i][:2] = child.preferredsize()
        self._calc_minsize()

    def preferredsize(self):
        return self._minwidth, self._minheight

    def spacing(self, *args):
        if args:
            self._spacing, = args
        else:
            return self._spacing

    def padding(self, *args):
        if args:
            self._padx, self._pady = args
        else:
            return self._padx, self._pady


class Fll_Hbox(Fll_Layout):
    def _calc_minsize(self):
        self._minheight = max(info[1] for info in self._childinfo if info[3]) \
                          + 2 * self._pady
        self._minwidth = sum(info[0] for info in self._childinfo if info[3]) \
                         + self._spacing * (len(self._childinfo) - 1) \
                         + 2 * self._padx

    def resize(self, x, y, w, h):
        if (self.x(), self.y(), self.w(), self.h()) == (x, y, w, h):
            #print 'hbox same size', x, y, w, h
            return
        #print 'start resizing hbox to', (x, y, w, h)
        sp = self._spacing
        xc = x + self._padx
        yc = y + self._pady
        ch = h - 2 * self._pady
        fill = st = 0
        if w > self._minwidth:
            if self._stretchers[2]:
                fill = (w - self._minwidth) / self._stretchers[2]
                st = 2
            elif self._stretchers[1]:
                fill = (w - self._minwidth) / self._stretchers[1]
                st = 1
        for i in range(self.children()):
            child = self.child(i)
            cw, _, cs, vis = self._childinfo[i]
            if not vis:
                continue
            if cs == st:
                cw += fill
            child.resize(xc, yc, cw, ch)
            xc += cw + sp
        Fl_Widget.resize(self, x, y, w, h)
        #print 'end resizing hbox'


class Fll_Vbox(Fll_Layout):
    def _calc_minsize(self):
        self._minwidth = max(info[0] for info in self._childinfo if info[3]) \
                         + 2 * self._padx
        self._minheight = sum(info[1] for info in self._childinfo if info[3]) \
                          + self._spacing * (len(self._childinfo) - 1) \
                          + 2 * self._pady

    def resize(self, x, y, w, h):
        if (self.x(), self.y(), self.w(), self.h()) == (x, y, w, h):
            #print 'vbox same size', (x, y, w, h)
            return
        #if not isinstance(self, Sm_Field):
        #    print 'start resizing vbox to', (x, y, w, h)
        sp = self._spacing
        xc = x + self._padx
        yc = y + self._pady
        cw = w - 2 * self._padx
        fill = st = 0
        if h > self._minheight:
            if self._stretchers[2]:
                fill = (h - self._minheight) / self._stretchers[2]
                st = 2
            elif self._stretchers[1]:
                fill = (h - self._minheight) / self._stretchers[1]
                st = 1
        for i in range(self.children()):
            child = self.child(i)
            _, ch, cs, vis = self._childinfo[i]
            if not vis:
                continue
            if cs == st:
                ch += fill
            child.resize(xc, yc, cw, ch)
            yc += ch + sp
        Fl_Widget.resize(self, x, y, w, h)
        #if not isinstance(self, Sm_Field):
        #    print 'end resizing vbox'


class Fll_Switcher(Fll_Layout):
    _current = 0

    def _calc_minsize(self):
        self._minwidth = max(info[0] for info in self._childinfo if info[3]) \
                         + 2 * self._padx
        self._minheight = max(info[1] for info in self._childinfo if info[3]) \
                          + 2 * self._pady

    def resize(self, x, y, w, h):
        if (self.x(), self.y(), self.w(), self.h()) == (x, y, w, h):
            return
        for child in self._children:
            child.resize(x, y, w, h)
        Fl_Widget.resize(self, x, y, w, h)

    def switch(self, index=None):
        if index is None:
            return self._current
        for i, child in enumerate(self._children):
            if i == index:
                child.show()
            else:
                child.hide()
        self._current = index


class Fll_Stretch(Fl_Box):
    stretch = 2

    def __init__(self):
        Fl_Box.__init__(self, 0, 0, 0, 0)


class Fll_LayoutWindow(Fl_Double_Window):
    def end(self):
        Fl_Double_Window.end(self)
        if self.children() != 1:
            raise RuntimeError('LayoutWindow needs exactly one child')
        self._onlychild = self.child(0)

    def resize(self, x, y, w, h):
        if hasattr(self, '_onlychild'):
            self._onlychild.resize(0, 0, w, h)
        Fl_Double_Window.resize(self, x, y, w, h)

    def preferredsize(self):
        if hasattr(self._onlychild, 'preferredsize'):
            return self._onlychild.preferredsize()
        else:
            return self._onlychild.w(), self._onlychild.h()


class Sm_Field(Fll_Vbox):
    def __init__(self, name, width, fontsize, istext, padding=5):
        Fll_Vbox.__init__(self, padding, padding, 0)

        w, h = measure(0, fontsize, name + 'XX')
        width = max(w, width)
        nheight = h + 5

        self._name = name
        self._namelabel = Fl_Box(0, 0, width, nheight, self._name)
        self._namelabel.box(FL_FLAT_BOX)
        self._namelabel.labelsize(fontsize)
        self.pack(self._namelabel)

        w, h = measure(FL_COURIER, fontsize, '0')
        vheight = h + 10

        self._value = '----'
        self._valuelabel = Fl_Box(0, 0, width, vheight, self._value)
        self._valuelabel.box(FL_DOWN_BOX)
        self._valuelabel.color(FL_GRAY)
        if not istext:
            self._valuelabel.labelfont(FL_COURIER)
        self._valuelabel.labelsize(fontsize)
        self.pack(self._valuelabel)

    #def resize(self, x, y, w, h):
    #    print 'resizing', self._name, 'to', (x, y, w, h)
    #    Fll_Vbox.resize(self, x, y, w, h)


class Sm_Row(Fll_Hbox):
    def __init__(self, padding=5):
        Fll_Hbox.__init__(self, padding, padding, padding)
        self.pack(Fll_Stretch())

    def end(self):
        self.pack(Fll_Stretch())
        Fll_Hbox.end(self)


class Sm_Box(Fl_Group):
    def __init__(self, title, fontsize):
        Fl_Group.__init__(self, 0, 0, 0, 0)
        self._title = title
        self._rowbox = Fll_Vbox()
        self._rowbox.box(FL_UP_FRAME)
        self._rowbox.pack(Fl_Box(0, 0, 0, 10))

        w, h = measure(FL_BOLD, fontsize, title)
        self._titlebox = Fl_Box(0, 0, w + 10, h + 5, title)
        self._titlebox.labelsize(fontsize)
        self._titlebox.labelfont(FL_BOLD)
        self._titlebox.box(FL_FLAT_BOX)
        self._titlebox.color(self.color())
        self.add(self._titlebox)

        self._offset = int(h + 5) / 2

    def resize(self, x, y, w, h):
        tw = self._titlebox.w()
        self._titlebox.resize(x + w/2 - tw/2, y, tw, self._titlebox.h())
        self.child(0).resize(x, y + self._offset, w, h - self._offset)
        Fl_Widget.resize(self, x, y, w, h)

    def pack(self, row):
        self._rowbox.pack(row)

    def preferredsize(self):
        w, h = self.child(0).preferredsize()
        return w, h + self._offset * 2


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
        master = self._master = Fll_LayoutWindow(1024, 800)

        if self._geometry == 'fullscreen':
            master.fullscreen()
        elif isinstance(self._geometry, tuple):
            master.resize(*self._geometry)

        master.label(self.title)

        self._bgcolor = master.color()
        self._fontsizebig = int(self._fontsize * 1.3)

        onechar = measure(FL_COURIER, self._fontsize, '0')[0]
        tiheight = self._fontsizebig + self._fontsize + 20

        masterlayout = Fll_Vbox()
        self._timelabel = Fl_Box(0, 0, 0, tiheight, self.title)
        self._timelabel.labelfont(FL_HELVETICA+1)
        self._timelabel.labelsize(self._fontsizebig + self._fontsize)
        self._timelabel.box(FL_FLAT_BOX)
        masterlayout.pack(self._timelabel)

        def _create_field(field):
            fieldwidget = Sm_Field(' ' + field['name'] + ' ',
                                   field['width'] * onechar, self._fontsize,
                                   field['istext'])

            field['namelabel'] = fieldwidget._namelabel
            field['valuelabel'] = fieldwidget._valuelabel

            # store reference from key to field for updates
            self.updateKeymap(field)
            return fieldwidget

        displaylayout = Fll_Vbox()

        # now iterate through the layout and create the widgets to display it
        for superrow in self._layout:
            boxlayout = Fll_Hbox(20, 10, 10)
            for column in superrow:
                columnlayout = Fll_Vbox(20)
                for block in column:
                    blocklayout = Fll_Hbox()
                    blocklayout.pack(Fll_Stretch())
                    blockbox = Sm_Box(block[0]['name'], self._fontsizebig)
                    block[0]['labelframe'] = blockbox
                    for row in block[1]:
                        if row is None:
                            rowbox = Fl_Box(0, 0, 0, self._padding * 2)
                        else:
                            rowbox = Sm_Row(self._padding)
                            for field in row:
                                rowbox.pack(_create_field(field))
                            rowbox.end()
                        blockbox.pack(rowbox)
                    if block[0]['only']:
                        self._onlymap.setdefault(block[0]['only'], []).\
                            append((columnlayout, blocklayout, blockbox))
                    blocklayout.pack(blockbox)
                    blocklayout.pack(Fll_Stretch())
                    columnlayout.pack(blocklayout)
                columnlayout.pack(Fll_Stretch())
                boxlayout.pack(columnlayout)
            displaylayout.pack(boxlayout)

        self._switcher = Fll_Switcher()
        self._switcher.pack(displaylayout)

        warnpanel = Fll_Vbox(20, 30)
        w, h = measure(0, self._fontsizebig + self._fontsize, 'Warnings')
        warnheading = Fl_Box(0, 0, 0, h + 20, 'Warnings')
        warnheading.labelsize(self._fontsizebig + self._fontsize)
        warnpanel.pack(warnheading)
        self._warnlabel = Fl_Box(0, 0, 0, 0)
        self._warnlabel.labelsize(self._fontsizebig)
        self._warnlabel.align(FL_ALIGN_TOP_LEFT)
        warnpanel.pack(self._warnlabel, stretch=True)

        self._switcher.pack(warnpanel)
        self._switcher.switch(0)
        masterlayout.pack(self._switcher)

        master.add(masterlayout)
        master.end()
        pw, ph = master.preferredsize()
        master.size(pw, ph)
        master.size_range(pw, ph, 0, 0)
        master.show()

    setLabelText = Fl_Box.copy_label

    def setLabelUnitText(self, label, text, unit):
        label.copy_label(text + ' (%s)' % unit)

    def setForeColor(self, label, fore):
        label.labelcolor(fore)

    def setBackColor(self, label, back):
        label.color(back)

    def setBothColors(self, label, fore, back):
        label.labelcolor(fore)
        label.color(back)

    def switchWarnPanel(self, off=False):
        if self._switcher.switch() == 1 or off:
            self._switcher.switch(0)
        else:
            self._switcher.switch(1)

    def reconfigureBoxes(self):
        for setup, boxes in self._onlymap.iteritems():
            for collayout, layout, blockbox in boxes:
                collayout.showchild(layout, setup in self._setups)
                if setup in self._setups:
                    blockbox.show()
                else:
                    blockbox.hide()
        self._master._onlychild.updatelayout()
        pw, ph = self._master.preferredsize()
        self._master.size(pw, ph)
        self._master.size_range(pw, ph, 0, 0)
        if self._geometry == 'fullscreen':
            self._master.fullscreen()
