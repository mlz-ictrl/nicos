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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from time import time as currenttime
import ntpath

from nicos import session
from nicos.core import Attach, DeviceMixinBase, Param, status
from nicos.core.errors import CommunicationError, InvalidValueError, NicosError
from nicos.core.params import floatrange, intrange, none_or, oneof, tupleof
from nicos.core.utils import waitForCompletion
from nicos.devices.generic import Switcher
from nicos.devices.generic.detector import ActiveChannel, ImageChannelMixin
from nicos.devices.tango import PyTangoDevice
from nicos.devices.vendor.lima import Andor2LimaCCD, Andor3LimaCCD


class UsesFastshutter(DeviceMixinBase):
    """
    Adds the ability to open a fast shutter before the
    acquisition.

    The given shutter devices MUST BE of type <nicos.devices.generic.Switcher>
    and MUST HAVE the values 'open' and 'closed'.  This state is enforced to
    avoid setups that configure almighty monster-detectors.
    """

    attached_devices = {
        'fastshutter': Attach('Fast shutter switcher device', Switcher),
    }

    parameters = {
        'openfastshutter': Param('Open fast shutter before the acquisition. '
                                 'Caution: It has to be closed manually',
                                 type=bool, settable=True, default=True),
    }

    def openFastshutter(self):
        # open fastshutter automatically if desired
        if self.openfastshutter:
            # reset fast shutter if in error state (the shutter sometimes goes
            # into error state because it couldn't be opened, but it works
            # again after reset on the next try
            fastshutter = self._attached_fastshutter
            if fastshutter.status(0)[0] == status.ERROR:
                self.log.warning('resetting fast shutter before opening: it is'
                                 ' in error state')
                fastshutter.reset()
            waitForCompletion(fastshutter)
            fastshutter.maw('open')


class AntaresIkonLCCD(UsesFastshutter, Andor2LimaCCD):
    """
    Extension to Andor2LimaCCD; Adds the ability to open a fast shutter before
    the acquisition.
    """

    def doStart(self, **preset):
        # open fastshutter automatically if desired
        if self.shuttermode in ['always_open', 'auto']:
            self.openFastshutter()

        Andor2LimaCCD.doStart(self, **preset)


class AntaresNeo(UsesFastshutter, Andor3LimaCCD):
    """
    Extension to Andor3LimaCCD; Adds the ability to open a fast shutter before
    the acquisition.
    """
    def doStart(self, **preset):
        self.openFastshutter()
        Andor3LimaCCD.doStart(self, **preset)


def absolute_win_path(val=ntpath.join('C:', ntpath.sep)):
    """Check for an absolute windows file path."""
    val = str(val)
    if ntpath.isabs(val) and ntpath.splitdrive(val)[0]:
        return val
    raise ValueError('%r is not a valid absolute path (should start with drive'
                     ' name like C:)' % val)


class AndorHFRCamera(PyTangoDevice, UsesFastshutter, ImageChannelMixin,
                     ActiveChannel):
    """Camera communicating with Andor Basic script."""

    TRIGGER_MODES = {
        'internal': 0,
        'external': 1,
        'external start': 6,
        'external exposure': 7,
        'external exposure FVB': 9,
    }

    SHUTTER_MODES = {
        'rolling': 0,
        'global': 1,
    }

    parameters = {
        'bin': Param('Binning (x,y)',
                     type=tupleof(intrange(1, 64), intrange(1, 64)),
                     settable=True, default=(1, 1), category='general'),
        'triggermode': Param('Triggering signal definition',
                             type=oneof(*TRIGGER_MODES),
                             settable=True, default='internal',
                             category='general'),
        'shuttermode': Param('Shutter mode setting',
                             type=oneof(*SHUTTER_MODES),
                             settable=True, default='rolling',
                             category='general'),
        'spooldirectory': Param('Path to spool the images on the remote '
                                'machine',
                                type=absolute_win_path, category='general'),
        'extratime': Param('Extra sleeping time to sync with Andors Basic',
                           type=floatrange(0), default=3, settable=True),
        '_started': Param('Cached counting start flag',
                          type=none_or(float), default=None, settable=True,
                          userparam=False),
    }

    def doPreinit(self, mode):
        PyTangoDevice.doPreinit(self, mode)
        self.log.info('Checking if camera script is ready!')
        try:
            msg = self._dev.communicate('ready?')
            if msg.strip() != 'ready!':
                raise CommunicationError(self, 'Camera script gave wrong '
                                         'answer - please check!')
        except NicosError:
            self.log.warning('Camera is not responding - please start '
                             'tomography script on camera first!')
            raise

    def doReset(self):
        self.log.info('Checking if camera script is ready!')
        try:
            msg = self._dev.communicate('ready?')
            if msg.strip() != 'ready!':
                raise CommunicationError(self, 'Camera script gave wrong '
                                         'answer - please check!')
        except NicosError:
            self.log.warning('Camera is not responding - please start '
                             'tomography script on camera first!')
            raise

    def doInit(self, mode):
        self._started = None

    def valueInfo(self):
        # no readresult by default
        return ()

    def doStart(self):
        self.bin = self.bin
        self.shuttermode = self.shuttermode
        self.triggermode = self.triggermode
        self.doWriteSpooldirectory(self.spooldirectory)
        kct = float(self._query_value('GetKineticCycleTime'))
        self.log.info('kct: %s', kct)
        self._counttime = self._knumber * kct + 3
        self.log.info('measure time = %s s', self._counttime)
        self.openFastshutter()
        self._write_command('count')
        self._started = currenttime()
        self.log.debug('started: %s', self._started)

    def doSetPreset(self, **presets):
        for preset, val in presets.items():
            self._write_presets(preset, val)
        self._write_presets('spoolfile', presets.get(
            'spoolfile', session.experiment.sample.samplename))

    def presetInfo(self):
        return ['exptime', 'number', 'cycletime', 'spoolfile']

    def doStatus(self, maxage=0):
        if self._started:
            if (self._started + self._counttime) > currenttime():
                return status.BUSY, 'counting'
        return status.OK, 'idle'

    def doStop(self):
        self._started = None
        self.status(0)
        self._attached_fastshutter.maw('closed')

    def doFinish(self):
        self._started = None
        # self._attached_fastshutter.maw('closed')

    def doWriteTriggermode(self, value):
        self._write_command('SetTriggerMode %d' % self.TRIGGER_MODES[value])

    def doWriteShuttermode(self, value):
        self._write_command('SetShutterMode %d' % self.SHUTTER_MODES[value])

    def doWriteSpooldirectory(self, value):
        self._write_command('SetSpoolDirectory %s' % value)

    def doWriteBin(self, value):
        self._write_command('SetHBin %d' % value[0])
        self._write_command('SetVBin %d' % value[1])

    def _write_command(self, command):
        ret = self._dev.communicate(command)
        if not ret.startswith('ACK'):
            if ret.startswith('ERR'):
                raise InvalidValueError(self, 'Command: %s is invalid ' %
                                        command)
            raise InvalidValueError(self, 'Command: %s has invalid '
                                    'parameters' % command)

    def _query_value(self, request):
        return self._dev.communicate(request)

    def _write_presets(self, preset, value):
        if preset == 'exptime':
            self._write_command('SetExposureTime %f' % value)
        elif preset == 'number':
            self._write_command('SetKineticNumber %d' % value)
            self._knumber = int(value)
        elif preset == 'cycletime':
            self._write_command('SetKineticCycleTime %f' % value)
        elif preset == 'spoolfile':
            self._write_command('SetSpoolFileName %s' % value)
