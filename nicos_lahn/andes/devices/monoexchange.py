# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Leonardo J. Ibáñez <leonardoibanez@cnea.gob.ar>
#
# *****************************************************************************

"""Monochromator Exchange."""

from nicos.core import Moveable, Readable, UsageError, multiWait, status, \
    usermethod
from nicos.core.params import Attach, Override
from nicos.devices.generic import Switcher


class MonoBlock(Readable):
    """The MonoBlock is a device that allows the monochromator crystal
    to be moved in 3 directions: translation, inclination and curvature."""

    parameter_overrides = {
        'unit': Override(mandatory=False),
    }

    attached_devices = {
        'tran': Attach('Translation', Moveable),
        'incl': Attach('Inclination', Moveable),
        'curv': Attach('Curvature', Moveable),
    }

    @property
    def tran(self):
        return self._attached_tran.read(0)

    @property
    def incl(self):
        return self._attached_incl.read(0)

    @property
    def curv(self):
        return self._attached_curv.read(0)

    def doRead(self, maxage=0):
        return [self.tran, self.incl, self.curv]


class Exchange(Switcher):
    """The Exchange is a device that maps switch monochromator crystals onto
    discrete values and allows to automatically adjust the focus."""

    parameter_overrides = {
        'fallback': Override(default='unknown'),
    }

    attached_devices = {
        'mb': Attach('Device for each crystal', MonoBlock, multiple=True),
    }

    _monoblock = None

    def _setHwConn(self, value):
        if self.status()[0] == status.OK:
            i = list(self.mapping.keys()).index(value)
            self._monoblock = self._attached_mb[i]

    def doInit(self, mode):
        Switcher.doInit(self, mode)
        self._setHwConn(Switcher._mapReadValue(self, Switcher._readRaw(self)))

    def doStart(self, target):
        Switcher._startRaw(self, self.mapping[target])
        self._setHwConn(target)

    @usermethod
    def setFocus(self, **keywords):  # beta_version
        """
        syntax: setFocus(device1=value, ...).
        """
        if not keywords:
            raise UsageError(self,
                             'at least one device and position must be given.')

        if self.status()[0] == status.OK:
            for dev, value in keywords.items():
                if dev not in self._monoblock._adevs:
                    raise UsageError(
                        self, 'device "%s" not defined. Posible devices '
                        'are: %s' % (dev, ', '.join(["'%s'" % x for x in
                                                     self._monoblock._adevs])))
                self._monoblock._adevs[dev].move(value)
            multiWait([self._monoblock._adevs[k] for k in keywords])
