#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2018-2021 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from nicos.devices.tango import StringIO as BaseStringIO


class StringIO(BaseStringIO):
    """StringIO which can be used in dry-run/simulation mode"""

    def communicate(self, value):
        if self._dev:
            return BaseStringIO.communicate(self, value)

    def flush(self):
        if self._dev:
            self._dev.Flush()

    def read(self, value):
        if self._dev:
            return BaseStringIO.read(self, value)

    def write(self, value):
        if self._dev:
            return BaseStringIO.write(self, value)

    def readLine(self):
        if self._dev:
            return BaseStringIO.readLine(self)

    def writeLine(self, value):
        if self._dev:
            return BaseStringIO.writeLine(self, value)

    def multiCommunicate(self, value):
        if self._dev:
            return BaseStringIO.multiCommunicate(self, value)

    @property
    def availablechars(self):
        if self._dev:
            return BaseStringIO.availablechars.__get__(self)

    @property
    def availablelines(self):
        if self._dev:
            return BaseStringIO.availablelines.__get__(self)
