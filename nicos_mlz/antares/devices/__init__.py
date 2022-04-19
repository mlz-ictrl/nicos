#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import Attach
from nicos.devices.generic import Pulse, VirtualTimer

from nicos_mlz.antares.devices.collimator import CollimatorLoverD, \
    GeometricBlur
from nicos_mlz.antares.devices.detector import AndorHFRCamera, \
    AntaresIkonLCCD, AntaresNeo, Sharpness
from nicos_mlz.antares.devices.experiment import Experiment
from nicos_mlz.antares.devices.monochromator import Monochromator
from nicos_mlz.antares.devices.partialdio import PartialDigitalInput, \
    PartialDigitalOutput
from nicos_mlz.antares.devices.selector import SelectorTilt


class TriggerTimer(VirtualTimer):
    """NICOS pulse device."""

    attached_devices = {
        'trigger': Attach('Pulser device', Pulse),
    }

    def doStart(self):
        self._attached_trigger.move(self._attached_trigger.onvalue)
        VirtualTimer.doStart(self)
