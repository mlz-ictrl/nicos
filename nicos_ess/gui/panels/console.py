#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI virtual console panel component."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels.console import \
    ConsolePanel as DefaultConsolePanel
from nicos.clients.gui.utils import enumerateWithProgress
from nicos.guisupport.qt import QTextCursor
from nicos.utils import chunks


class ConsolePanel(DefaultConsolePanel):
    """Provides a console-like interface.

    The commands can be entered and the output from the NICOS daemon is
    displayed.

    Options:

    * ``hasinput`` (default True) -- if set to False, the input box is hidden
      and the console is just an output view.
    * ``hasmenu`` (default True) -- if set to False, the console does not
      provide its menu (containing actions for the output view such as Save
      or Print).
    * ``fulltime`` (default False) -- if set to True, the console shows the
      full (date + time) timestamp for every line, instead of only for errors
      and warnings.
    * ``watermark`` (default empty) -- the path to an image file that should
      be used as a watermark in the console window.
    * ``reverse_scrolling`` (default False) -- show the messages in reverse
      order, i.e. scrolling top to bottom
    """

    panelName = 'Console'
    ui = 'panels/console.ui'

    def __init__(self, parent, client, options):
        DefaultConsolePanel.__init__(self, parent, client, options)
        if 'reverse_scrolling' in options and options['reverse_scrolling']:
            self.outView.enableReverseScrolling(True)

    def on_client_initstatus(self, state):
        # Same as DefaultConsolePanel.on_client_initstatus but reverse the
        # list if reverse_scrolling is enable
        if self.outView.text_curson_position == QTextCursor.End:
            DefaultConsolePanel.on_client_initstatus(self, state)
        else:
            self.on_client_mode(state['mode'])
            self.outView.clear()
            messages = list(reversed(self.client.ask('getmessages', '10000',
                                                default=[])))
            total = len(messages) // 2500 + 1
            for _, batch in enumerateWithProgress(chunks(messages, 2500),
                                                  text='Synchronizing...',
                                                  parent=self, total=total):
                self.outView.addMessages(batch)
