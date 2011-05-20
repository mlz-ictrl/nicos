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

from __future__ import with_statement

"""Class for Stanford Research SR850 lock-in amplifier."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from math import hypot, atan2

from IO import StringIO

from nicos.taco import TacoDevice
from nicos.device import Measurable, Param, Value
from nicos.errors import CommunicationError


class Amplifier(Measurable, TacoDevice):

    taco_class = StringIO

    def doInit(self):
        if self._mode == 'simulation':
            return
        reply = self._taco_guard(self._dev.communicate, '*IDN?')
        if not reply.startswith('Stanford_Research_Systems,SR850,s/n'):
            raise CommunicationError('wrong identification: %r' % reply)

    def valueInfo(self):
        return Value('X', unit='V'), Value('Y', unit='V'), \
               Value('R', unit='V'), Value('Theta', unit='deg')

    def doStart(self, **preset):
        pass

    def doIsCompleted(self):
        return True

    def doRead(self):
        out = []
        X = float(self._taco_guard(self._dev.communicate, 'OUTP? 1'))
        Y = float(self._taco_guard(self._dev.communicate, 'OUTP? 2'))
        R = hypot(X, Y)
        Theta = atan2(Y, X)
        return (X, Y, R, Theta)
