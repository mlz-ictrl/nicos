# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from nicos.core import Attach, Moveable, Param
from nicos.core.errors import InvalidValueError
from nicos.devices.generic.detector import Detector, PassiveChannel

from nicos_mlz.jcns.devices.shutter import CLOSED, OPEN


class MariaDetector(Detector):

    attached_devices = {
        "shutter": Attach("Shutter to open before exposure", Moveable),
        "lives": Attach("Live channels", PassiveChannel,
                        multiple=True, optional=True)
    }

    parameters = {
        "ctrl_shutter": Param("Open shutter automatically before "
                              "exposure?", type=bool, settable=True,
                              mandatory=False, default=True),
    }

    def doStart(self):
        # open shutter before exposure
        if self.ctrl_shutter:
            self._attached_shutter.maw(OPEN)
        Detector.doStart(self)

    def doFinish(self):
        Detector.doFinish(self)
        if self.ctrl_shutter and self._attached_shutter.read() == CLOSED:
            raise InvalidValueError(self, 'shutter not open after exposure, '
                                    'check safety system')

    def _getWaiters(self):
        adevs = dict(self._adevs)
        if not self.ctrl_shutter:
            adevs.pop("shutter")
        return adevs

    def _presetiter(self):
        for i, dev in enumerate(self._attached_lives):
            if i == 0:
                yield ("live", dev)
            yield ("live%d" % (i + 1), dev)
        for itm in Detector._presetiter(self):
            yield itm

    def doSetPreset(self, **preset):
        Detector.doSetPreset(self, **preset)
        preset = self._getPreset(preset)
        if not preset:
            return

        for dev in self._attached_lives:
            dev.islive = False

        for name in preset:
            if name in self._presetkeys and self._presetkeys[name] and \
                    name.startswith("live"):
                dev = self._presetkeys[name]
                dev.ismaster = True
                dev.islive = True
        self.log.debug("   presets: %s", preset)
        self.log.debug("presetkeys: %s", self._presetkeys)
        self.log.debug("   masters: %s", self._masters)
        self.log.debug("    slaves: %s", self._slaves)
