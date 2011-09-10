#  -*- coding: utf-8 -*-
# *****************************************************************************
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
# Module authors:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Gtk version of instrument monitor."""

__version__ = "$Revision$"

from cgi import escape

gtk = __import__('gtk')
import pango

from nicos.monitor import Monitor as BaseMonitor


class Monitor(BaseMonitor):
    """Gtk specific implementation of instrument monitor."""

    def mainLoop(self):
        gtk.gdk.threads_init()
        gtk.main()

    def closeGui(self):
        self._master.destroy()

    def initColors(self):
        self._bgcolor = gtk.gdk.color_parse('gray')
        self._black = gtk.gdk.color_parse('black')
        self._yellow = gtk.gdk.color_parse('yellow')
        self._green = gtk.gdk.color_parse('#00ff00')
        self._red = gtk.gdk.color_parse('red')
        self._gray = gtk.gdk.color_parse('gray')
        self._white = gtk.gdk.color_parse('white')

    def initGui(self):
        gtk.rc_parse_string('style "mystyle" { engine "pixmap" {} }\n'
                            'class "GtkWidget" style "mystyle"')

        self.setLabelText = gtk.Label.set_text

        self._master = master = gtk.Window(gtk.WINDOW_TOPLEVEL)
        master.show()

        master.connect('destroy', gtk.main_quit)
        def key(obj, event):
            if event.keyval == ord('q'):
                master.destroy()
        master.connect('key-release-event', key)

        if self._geometry == 'fullscreen':
            master.fullscreen()
        elif isinstance(self._geometry, tuple):
            master.move(self._geometry[0], self._geometry[1])
            master.resize(self._geometry[2], self._geometry[3])

        master.set_title(self.title)
        master.set_border_width(self._padding)
        self._bgcolor = master.get_style().bg[0]

        def font(name, size):
            return pango.FontDescription('%s %s' % (name, size))
        timefont  = font(self.font, self._fontsizebig + self._fontsize)
        blockfont = font(self.font, self._fontsizebig)
        labelfont = font(self.font, self._fontsize)
        valuefont = font(self.valuefont or self.font, self._fontsize)

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterframe = gtk.VBox()
        master.add(masterframe)
        timebox = gtk.EventBox()
        self._timelabel = gtk.Label('')
        self._timelabel.modify_font(timefont)
        self.setForeColor(self._timelabel, self._gray)
        self._timelabel.set_justify(gtk.JUSTIFY_CENTER)
        self._timelabel._box = timebox
        timebox.add(self._timelabel)
        masterframe.pack_start(timebox, False)

        self._stacker = gtk.Notebook()
        self._stacker.set_show_tabs(False)
        self._stacker.set_show_border(False)
        masterframe.pack_start(self._stacker)

        def _create_field(groupframe, field):
            fieldlayout = gtk.VBox()
            # now put describing label and view label into subframe
            lb = gtk.EventBox()
            l = gtk.Label(' ' + field['name'] + ' ')
            l.modify_font(labelfont)
            l.set_justify(gtk.JUSTIFY_CENTER)
            l._box = lb
            lb.add(l)
            fieldlayout.add(lb)
            field['namelabel'] = l
            if field['unit']:
                self.setLabelUnitText(l, field['name'], field['unit'])

            lb = gtk.EventBox()
            lf = gtk.Frame()
            lf.set_shadow_type(gtk.SHADOW_IN)
            l = gtk.Label('----')
            if field['istext']:
                l.modify_font(labelfont)
                l.set_justify(gtk.JUSTIFY_LEFT)
            else:
                l.modify_font(valuefont)
                l.set_justify(gtk.JUSTIFY_CENTER)
            l.set_width_chars(field['width'] + 1)
            l._box = lb
            field['valuelabel'] = l
            lf.add(l)
            lb.add(lf)

            tmplayout = gtk.HBox()
            tmplayout.pack_start(gtk.Label())
            tmplayout.pack_start(lb, False)
            tmplayout.pack_start(gtk.Label())
            fieldlayout.pack_start(tmplayout)

            self.updateKeymap(field)
            return fieldlayout

        displayframe = gtk.VBox()
        self._stacker.append_page(displayframe)

        # now iterate through the layout and create the widgets to display it
        for superrow in self._layout:
            boxlayout = gtk.HBox()
            for column in superrow:
                columnlayout = gtk.VBox()
                columnlayout.set_spacing(self._padding*2)
                for block in column:
                    blocklayout_outer = gtk.HBox()
                    blocklayout_outer.add(gtk.Label())
                    blockbox = gtk.Frame(block[0]['name'])
                    blockbox.get_label_widget().modify_font(blockfont)
                    blockbox.set_label_align(0.5, 0.5)
                    blockbox.set_shadow_type(gtk.SHADOW_OUT)
                    block[0]['labelframe'] = blockbox
                    blocklayout = gtk.VBox()
                    for row in block[1]:
                        if row is None:
                            blocklayout.pack_start(gtk.HSeparator(), False)
                        else:
                            rowlayout = gtk.HBox()
                            rowlayout.set_spacing(self._padding)
                            rowlayout.add(gtk.Label())
                            for field in row:
                                fieldframe = _create_field(blockbox, field)
                                rowlayout.pack_start(fieldframe)
                            rowlayout.add(gtk.Label())
                            blocklayout.pack_start(rowlayout, False,
                                                   padding=self._padding/2)
                    if block[0]['only']:
                        self._onlymap.setdefault(block[0]['only'], []).\
                            append((blocklayout_outer, blockbox))
                    blockbox.add(blocklayout)
                    blocklayout_outer.pack_start(blockbox, False)
                    blocklayout_outer.add(gtk.Label())
                    columnlayout.pack_start(blocklayout_outer, False)
                boxlayout.pack_start(columnlayout, padding=2*self._padding)
            displayframe.pack_start(boxlayout, padding=self._padding)

        self._warnpanel = gtk.VBox()
        self._warnpanel.set_spacing(20)

        lbl = gtk.Label('Warnings')
        lbl.set_justify(gtk.JUSTIFY_CENTER)
        lbl.modify_font(timefont)
        self._warnpanel.pack_start(lbl, False)
        self._warnlabel = gtk.Label('')
        self._warnlabel.set_alignment(0., 0.)
        self._warnlabel.modify_font(blockfont)
        self._warnpanel.pack_start(self._warnlabel)

        self._stacker.append_page(self._warnpanel)

        master.show_all()

    def setLabelUnitText(self, label, text, unit):
        label.set_markup(escape(text) + ' <span foreground="#888888">%s'
                         '</span> ' % escape(unit))

    def setForeColor(self, label, fore):
        label.modify_fg(gtk.STATE_NORMAL, fore)

    def setBackColor(self, label, back):
        label._box.modify_bg(gtk.STATE_NORMAL, back)

    def setBothColors(self, label, fore, back):
        label.modify_fg(gtk.STATE_NORMAL, fore)
        label._box.modify_bg(gtk.STATE_NORMAL, back)

    def switchWarnPanel(self, off=False):
        if self._stacker.get_current_page() == 1 or off:
            self._stacker.set_current_page(0)
        else:
            self._stacker.set_current_page(1)

    def reconfigureBoxes(self):
        for setup, boxes in self._onlymap.iteritems():
            for layout, blockbox in boxes:
                if setup in self._setups:
                    blockbox.show()
                else:
                    blockbox.hide()
