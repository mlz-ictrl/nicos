#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""
A remote debugger for the NICOS daemon.
"""

import sys
from pdb import Pdb

from nicos.pycompat import queue


class FakeStdin(queue.Queue):
    """A Queue that can pose as a stream with a readline() method."""
    def readline(self):
        return self.get()


class Rpdb(Pdb):  # pylint: disable=too-many-public-methods
    """Minimally modified Pdb to work with remote input."""

    # use self.stdin.read(), not readline
    use_rawinput = False

    def __init__(self, endcallback):
        Pdb.__init__(self)
        self._endcallback = endcallback
        # do not display any prompt
        self.prompt = ''
        # get input lines from our fake input stream
        self.stdin = FakeStdin()

    def set_trace(self, frame, limitframe):  # pylint: disable=W0221
        # Overridden to not set the trace function in frames below "limitframe"
        if frame is None:
            frame = sys._getframe().f_back
        self.reset()
        while frame is not limitframe:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        self.set_step()
        sys.settrace(self.trace_dispatch)
        # notify user
        self.stdout.write('remote debugging session started')

    def finished(self):
        # notify user
        self.stdout.write('remote debugging session finished')
        # call back to script thread
        self._endcallback()

    # these two methods end tracing, i.e. use sys.settrace(None), upon which we
    # want to a) notify the clients about and b) re-set our own trace function

    def set_continue(self):
        Pdb.set_continue(self)
        if not self.breaks:
            self.finished()

    def set_quit(self):
        Pdb.set_quit(self)
        self.finished()
