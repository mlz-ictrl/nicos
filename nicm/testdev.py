#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Virtual NICOS test devices
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   $Author$
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

"""
Virtual devices for testing.
"""

from nicm import nicos
from nicm.device import Device, Moveable
from nicm.motor import Motor
from nicm.coder import Coder
from nicm.commands import printdebug


class VirtualMotor(Motor):
    parameters = {
        'initval': (0, True, 'Initial value for the virtual device.'),
    }

    def doInit(self):
        self._val = self.getPar('initval')

    def doStart(self, pos):
        self.printdebug('moving to %s' % pos)
        self._val = pos

    def doRead(self):
        return self._val


class VirtualCoder(Coder):

    def doRead(self):
        return 0
