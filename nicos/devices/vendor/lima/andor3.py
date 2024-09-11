# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos.core import HasLimits, HasPrecision, Moveable, Param, floatrange, \
    oneof, status
from nicos.devices.tango import PyTangoDevice

from .generic import GenericLimaCCD
from .optional import LimaCooler


class Andor3LimaCCD(GenericLimaCCD):
    """
    This device class is an extension to the GenericLimaCCD that adds the
    hardware specific functionality for all Andor SDK3 based cameras.
    """

    READOUTRATES = [280, 200, 100, 10]  # Values from sdk manual
    ELSHUTTERMODES = ['rolling', 'global']  # Values from sdk manual

    parameters = {
        'readoutrate':   Param('Rate of pixel readout from sensor',
                               type=oneof(*READOUTRATES),
                               unit='MHz', settable=True, volatile=True,
                               category='general'),
        'elshuttermode': Param('On-sensor electronic shuttering mode',
                               type=oneof(*ELSHUTTERMODES),
                               settable=True, volatile=True,
                               category='general'),
        'framerate':     Param('Rate at which frames are delivered to the use',
                               type=float, unit='Hz', settable=False,
                               volatile=True, category='general'),
        'adc_gain':     Param('ADC Gain which can be apply to the preamplifier',
                              type=oneof('B11_HI-GAIN', 'B11_LOW_GAIN',
                                         'B16_LH_GAIN'),
                              settable=True, userparam=True,
                              volatile=True, category='instrument'),
        'fanspeed':     Param('Fan speed setting',
                              type=oneof('OFF', 'ON'), settable=True,
                              userparam=True, volatile=True,
                              category='instrument'),
        'max_frame_rate_transfer': Param('Maximum sustainable transfer rate '
                                         'of the interface for the current '
                                         'shutter mode and ROI',
                                         type=floatrange(0), settable=False,
                                         userparam=True, volatile=True,
                                         unit='B/s', fmtstr='%f',
                                         category='instrument'),
        'readout_time':     Param('Time to read out data from the sensor',
                                  type=float, settable=False, unit='s',
                                  userparam=True, volatile=True,
                                  category='instrument'),
        'overlap':          Param('Enable/disable overlap mode',
                                  type=oneof('OFF', 'ON'), settable=True,
                                  userparam=True, volatile=True,
                                  mandatory=False, category='instrument'),
        'spurious_noise_filter': Param('Enable/Disable spurious noise filter',
                                       type=oneof('OFF', 'ON'), settable=True,
                                       userparam=True, volatile=True,
                                       mandatory=False, category='instrument'),
        'serialnumber':     Param('Camera serial number',
                                  type=str, settable=False, userparam=True,
                                  volatile=True, category='instrument'),
        'trigger_inverted': Param('trigger signal inverted',
                                  type=oneof('YES', 'NO'), settable=True,
                                  userparam=True, volatile=True,
                                  category='instrument'),
        'gate_inverted':    Param('gate signal inverted',
                                  type=oneof('YES', 'NO'), settable=True,
                                  userparam=True, volatile=True,
                                  category='instrument'),
        'output_signal':    Param('Output signal selection',
                                  type=oneof('FIREROW1', 'FIREROWN', 'FIREANY',
                                             'FIREALL'),
                                  settable=True, userparam=True, volatile=True,
                                  category='instrument'),
    }

    def doInfo(self):
        for p in ('readoutrate', 'elshuttermode', 'framerate'):
            self._pollParam(p)
        return []

    def doReadReadoutrate(self):
        return int(self._hwDev._dev.adc_rate[:-4])

    def doWriteReadoutrate(self, value):
        self._hwDev._dev.adc_rate = f'{value}_MHZ'

    def doReadElshuttermode(self):
        return self._hwDev._dev.electronic_shutter_mode.lower()

    def doWriteElshuttermode(self, value):
        self._hwDev._dev.electronic_shutter_mode = value.upper()

    def doReadFramerate(self):
        return self._hwDev._dev.frame_rate

    def _specialInit(self):
        # set some dummy roi to avoid strange lima rotation behaviour
        # (not at 0, 0 to avoid possible problems with strides)
        self._dev.image_roi = (8, 8, 8, 8)
        # ensure NO rotation
        self._dev.image_rotation = 'NONE'
        # set full detector size as roi
        self._dev.image_roi = (0, 0, 0, 0)

    def doReadAdc_Gain(self):
        return self._hwDev._dev.adc_gain

    def doWriteAdc_Gain(self, value):
        self._hwDev._dev.adc_gain = value

    def doReadFanspeed(self):
        return self._hwDev._dev.fan_speed

    def doWriteFanspeed(self, value):
        self._hwDev._dev.fan_speed = value

    def doReadOverlap(self):
        return self._hwDev._dev.overlap

    def doWriteOverlap(self, value):
        self._hwDev._dev.overlap = value

    def doReadSerialnumber(self):
        return self._hwDev._dev.serial_number

    def doReadSpurious_Noise_Filter(self):
        return self._hwDev._dev.spurious_noise_filter

    def doWriteSpurious_Noise_Filter(self, value):
        self._hwDev._dev.spurious_noise_filter = value

    def doReadTrigger_Inverted(self):
        return self._hwDev._dev.trigger_inverted

    def doWriteTrigger_Inverted(self, value):
        self._hwDev._dev.trigger_inverted = value

    def doReadGate_Inverted(self):
        return self._hwDev._dev.gate_inverted

    def doWriteGate_Inverted(self, value):
        self._hwDev._dev.gate_inverted = value

    def doReadReadout_Time(self):
        return self._hwDev._dev.readout_time

    def doReadOutput_Signal(self):
        return self._hwDev._dev.output_signal

    def doWriteOutput_Signal(self, value):
        self._hwDev._dev.output_signal = value

    def doReadMax_Frame_Rate_Transfer(self):
        return self._hwDev._dev.max_frame_rate_transfer


class Andor3TemperatureController(PyTangoDevice, HasLimits, HasPrecision,
                                  LimaCooler, Moveable):
    """
    This devices provides access to the cooling feature of Andor3 cameras.
    """

    COOLER_STATUS_MAP = {
        'Fault': status.ERROR,
        'Drift': status.ERROR,
        'Cooler Off': status.OK,
        'Stabilised': status.OK,
        'Cooling': status.BUSY,
        'Not Stabilised': status.BUSY,
    }

    parameters = {
        'cooler': Param('Start/stop the cooler',
                        type=oneof('OFF', 'ON'), settable=True, userparam=True,
                        volatile=True, category='instrument'),
    }

    def doRead(self, maxage=0):
        return self._dev.temperature

    def doStatus(self, maxage=0):
        coolerState = self._dev.cooling_status
        nicosState = self.COOLER_STATUS_MAP.get(coolerState, status.UNKNOWN)

        return (nicosState, coolerState)

    def doStart(self, target):
        self._dev.temperature_sp = target
        self.cooleron = True

    def doVersion(self):
        return [(self.tangodevice,
                 f'tango {self._dev.get_tango_lib_version() / 100:.02f}')]

    def doReadCooler(self):
        return self._dev.cooler

    def doWriteCooler(self, value):
        self._dev.cooler = value
