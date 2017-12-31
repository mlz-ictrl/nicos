#  -*- coding: utf-8 -*-
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

"""
This module contains ESS specific Base classes for EPICS.
"""

from nicos import session
from nicos.core import Param
from nicos.core.errors import ConfigurationError
from nicos.devices.epics import EpicsDevice, EpicsReadable, \
    EpicsStringReadable, EpicsMoveable, EpicsAnalogMoveable, \
    EpicsDigitalMoveable, EpicsWindowTimeoutDevice


class EpicsDeviceEss(EpicsDevice):
    """ Base class for EPICS Device to be used in the ESS instrument devices.
    The ESS device has functionality to write and read PVs from Kafka topics.
    """

    parameters = {
        'devicepvtopic': Param(
            'Default topic for device where PVs are to be forwarded',
            type=str),
        'devicepvschema': Param('Default flatbuffers coding schema for device',
                               type=str),
        'pvdetails': Param(
            'Dict of specific PV and tuple of (topic, schema) if is different',
            type=dict),
    }

    def doPreinit(self, mode):
        EpicsDevice.doPreinit(self, mode)

        pv_details = {}
        # Get topics for each PV
        for pvparam in self._get_pv_parameters():
            topic = self.devicepvtopic if self.devicepvtopic else ''
            schema = self.devicepvschema if self.devicepvschema else ''
            pv = self._get_pv_name(pvparam)
            if self.pvdetails and pv in self.pvdetails:
                topic, schema = self.pvdetails[pv]
            pv_details[pv] = (topic, schema)

        # Configure the forwarder if the KafkaForwarder is available
        # Get the forwarded topic and schema for the PV
        try:
            forwarder = session.getDevice('KafkaForwarder')
            if forwarder is not None:
                forwarder.add(pv_details)
        except ConfigurationError:
            pass


class EpicsReadableEss(EpicsDeviceEss, EpicsReadable):
    pass


class EpicsStringReadableEss(EpicsDeviceEss, EpicsStringReadable):
    pass


class EpicsMoveableEss(EpicsDeviceEss, EpicsMoveable):
    pass


class EpicsAnalogMoveableEss(EpicsDeviceEss, EpicsAnalogMoveable):
    pass


class EpicsDigitalMoveableEss(EpicsDeviceEss, EpicsDigitalMoveable):
    pass


class EpicsWindowTimeoutDeviceEss(EpicsDeviceEss, EpicsWindowTimeoutDevice):
    pass
