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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""DigitalOutput with timeout for CCR gas valve."""

__version__ = "$Revision$"

from threading import Timer

from nicos.core import Param
from nicos.taco import NamedDigitalOutput


class GasValve(NamedDigitalOutput):
    parameters = {
        'timeout':  Param('Timeout for closing valve', settable=True,
                          type=float, unit='s', default=600),
    }

    def doInit(self, mode):
        NamedDigitalOutput.doInit(self, mode)
        self._timer = None

    def doStart(self, target):
        NamedDigitalOutput.doStart(self, target)
        if self._timer is not None:
            try:
                self._timer.cancel()
            except Exception:
                pass
        self._timer = Timer(self.timeout, self._timeout_elapsed)
        self._timer.setDaemon(True)
        self._timer.start()

    def _timeout_elapsed(self):
        if self.doRead() == 'on':
            self.log.warning('switching off gas valve after timeout')
            self.move('off')
        self._timer = None
