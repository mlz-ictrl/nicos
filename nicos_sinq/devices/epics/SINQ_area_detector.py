#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from nicos_ess.devices.epics.area_detector import EpicsAreaDetector


class AndorAreaDetector(EpicsAreaDetector):
    """
    This class adds the special fields for the Andor cameras as used at SINQ
    to the base EpicsAreaDetector. Only the subset actually used at SINQ is
    added.
    """
    _device_rw = {
        'acquire_time': 'AcquireTime',
        'acquire_period': 'AcquirePeriod',
        'shutter_close_delay': 'ShutterCloseDelay',
        'shutter_open_delay': 'ShutterOpenDelay',
        'temperature': 'Temperature',
    }
    _device_ro = {
        'temperature_actual': 'TemperatureActual',
    }

    _device_srw = {
        'trigger_mode': 'TriggerMode',
        'cooler': 'AndorCooler',
        'shutter_mode': 'ShutterMode',
        'adc_speed': 'AndorADCSpeed',
        'readout_mode': 'AndorReadOutMode',
        'vs_period': 'AndorVSPeriod'
    }
