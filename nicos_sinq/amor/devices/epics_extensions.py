#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
This module contains SINQ specific EPICS developments.
"""

from nicos.core import Device, Param, pvname
from nicos.devices.epics import EpicsDevice


class EpicsAsynController(EpicsDevice, Device):
    """
    Device to directly control the devices connected to
    the asyn controller via EPICS.

    This device can issue commands to the asyn controller
    which in turn can operate the attached devices to the
    controller. The commands issued should adhere to the
    policies and syntax of the asyn controller.

    To do this via EPICS, two pvs can be provided:

    commandpv - PV that issues the command to be executed
                to the controller
    replypv - PV that stores in the reply generated from
              the execution of the command
    """

    parameters = {
        'commandpv': Param('PV to issue commands to the asyn controller',
                           type=pvname, mandatory=True, settable=False),
        'replypv': Param('PV that stores the reply generated from execution',
                         type=pvname, mandatory=False, settable=False),
    }

    def _get_pv_parameters(self):
        pvs = set(['commandpv'])

        if self.replypv:
            pvs.add('replypv')

        return pvs

    def execute(self, command):
        """
        Issue and execute the provided command
        Returns the reply if the replypv is set
        """
        # Send the command to the commandpv
        self._put_pv_blocking('commandpv', command)

        # If reply PV is set, return it's output
        return self._get_pv('replypv') if self.replypv else ''
