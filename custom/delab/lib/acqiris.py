#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""CARESS Detector class for NICOS."""

import sys
from omniORB import CORBA
import CosNaming

from nicos.delab import CARESS # pylint: disable=F0401,E0611

sys.modules['CARESS'] = sys.modules['nicos.delab.CARESS']
import omniORB
omniORB.updateModule('CARESS')

from nicos.core import Param, Override, Value, status, oneof, SIMULATION
from nicos.devices.generic.detector import Channel as BaseChannel
from nicos.core.errors import CommunicationError, ConfigurationError, \
    NicosError, UsageError, ProgrammingError
from nicos.utils import readFileCounter, updateFileCounter
from nicos.pycompat import integer_types


COUNTER_ID  = 100
TIMER_ID    = 101

LOADMASTER  = 14
LOADSLAVE   = 15
RESETMODULE = 16
SPECIALLOAD = 18

NOT_ACTIVE  = 1
ACTIVE      = 2
DONE        = 3
LOADED      = 4

OFF_LINE    = 0
ON_LINE     = 1


class Channel(BaseChannel):
    """The Acqiris detector device.

    The Acqiris detector server is a CORBA based CARESS device server.
    """

    _orb = None

    parameters = {
        'nameserver' : Param('Computer name running the CORBA name service',
                             type=str, mandatory=True,
                             # default='deldaq50.del.frm2',
                            ),
        'counterfile' : Param('File name storing the runnumber',
                              type=str, default='runid.txt', mandatory=True,
                             ),
        'runnumber' : Param('Run number',
                            type=int, settable=True,
                           ),
        'objname' : Param('Name of the CORBA object',
                          type=str, mandatory=True,
                          # default='acqirishzb',
                         ),
    }

    parameter_overrides = {
        'mode' : Override(type=oneof('normal', 'preselection'),
                          default='preselection',
                          settable=True,
                         ),
    }

    def _initORB(self, args):
        if not self._orb:
            self._orb = CORBA.ORB_init(args, CORBA.ORB_ID)

    def _initObject(self, c_id):
        if not self._orb:
            raise ProgrammingError(self, 'Programmer forgot to call _initORB')

        obj = self._orb.resolve_initial_references('NameService')
        rootContext = obj._narrow(CosNaming.NamingContext)

        if not rootContext:
            raise CommunicationError(self, 'Failed to narrow the root naming'
                                     ' context')
        try:
            obj = rootContext.resolve([CosNaming.NameComponent(
                                        self.objname, 'caress_object'),])
        except CosNaming.NamingContext.NotFound as ex:
            raise ConfigurationError(self, 'Name not found: %s' % (ex,))

        self._caressObject = obj._narrow(CARESS.CORBADevice)
        if not self._caressObject:
            raise ConfigurationError(self, 'Object is not a CARESS::CORBADevice')

        self._cid = c_id

        is_status = self._caressObject.is_status_module(self._cid)
        self.log.debug('Status module: %r' % (is_status,))

        is_readable = self._caressObject.is_readable_module(self._cid)
        self.log.debug('Readable module: %r' % (is_readable,))

        is_drivable = self._caressObject.is_drivable_module(self._cid)
        self.log.debug('Driveble module: %r' % (is_drivable,))

        is_counting = self._caressObject.is_counting_module(self._cid)
        self.log.debug('Counting module: %r' % (is_counting,))

        needs_reference = self._caressObject.needs_reference_module(self._cid)
        self.log.debug('Needs reference module: %r' % (needs_reference,))

        if not is_readable or not is_counting:
            raise ConfigurationError(self, 'Object is not a readable counting'
                                     ' module')
        try:
            result = self._caressObject.get_attribute(self._cid,
                                                      'detector_channels')
            self.log.debug('Get attribute "detector_channels": %r' % (result,))
        except CARESS.ErrorDescription as ex:
            self.log.info('Attribute "detector_channels" not found: %s' % (ex,))

        try:
            result = self._caressObject.get_attribute(self._cid,
                                                      'detector_pixelwidth')
            self.log.debug('Get attribute "detector_pixelwidth": %r' % (result,))
        except CARESS.ErrorDescription as ex:
            self.log.info('Attribute "detector_pixelwidth" not found: %s' % (ex,))

        self._initialized = False

    def _init(self, mode):
        result = self._caressObject.init_module(0, self._cid, mode)
        self.log.debug('Init module: %r' % (result,))
        if result != (CARESS.OK, ON_LINE):
            raise NicosError(self, 'Could not initialize module!')
        self._initialized = True

    def doInit(self, mode):
        if mode == SIMULATION:
            self._caressObject = None
            return
        self._initORB(['-ORBInitRef', 'NameService=corbaname::%s' %
                       (self.nameserver, ),])

    def doShutdown(self):
        if self._caressObject:
            result = self._caressObject.release_module(0, self._cid)
            if result != CARESS.OK:
                raise NicosError(self, 'Could not release device')

    def doSetPreset(self, **preset):
        self.log.debug('preset is : %r' % preset)
        if 'n' in preset:
            self._presetValue = preset['n']
        elif 't' in preset:
            self._presetValue = preset['t']
        else:
            raise UsageError('preset must be "n" or "t"')

    def doStart(self, **preset):
        self._reset()
        self.log.debug('preset is : %r' % preset)

        if not self.ismaster:
            return
        if preset:
            self.doSetPreset(**preset)

        if isinstance(self.preselection, (float, )):
            value = CARESS.Value(l=int(self.preselection))
        elif isinstance(self.preselection, integer_types):
            value = CARESS.Value(l=self.preselection)
        self.log.debug('preselection : %r' % (value,))
        result = self._caressObject.load_module(LOADMASTER, self._cid, value)
        if result != (CARESS.OK, LOADED):
            raise NicosError(self, 'Could not set the preset value')
        # Implementation of the acqiris hardware driver says that the kind 0
        # starts the detector
        result = self._caressObject.start_module(0, self._cid, self.runnumber,
                                                 0)
        if result != (CARESS.OK, ACTIVE):
            raise NicosError(self, 'Could not start the device')
        if self.ismaster:
            self.runnumber += 1

    def doPause(self):
        # Implementation of the acqiris hardware driver says that the kind 0
        # only pauses the detector
        if self.ismaster:
            result = self._caressObject.stop_module(0, self._cid)
            if result != (CARESS.OK, DONE):
                raise NicosError(self, 'Could not pause the module')

    def doResume(self):
        if not self.ismaster:
            return
        # Implementation of the acqiris hardware driver says that the kind 1
        # resumes the detector
        result = self._caressObject.start_module(1, self._cid, self.runnumber,
                                                 0)
        if result[0] != CARESS.OK:
            raise NicosError(self, 'Could not resume the device')

    def doStop(self):
        # Implementation of the acqiris hardware driver says that the kind 1
        # stops the detector
        if not self.isCompleted():
            result = self._caressObject.stop_module(1, self._cid)
            if result != (CARESS.OK, DONE):
                raise NicosError(self, 'Could not stop the module')

    def _reset(self):
        result = self._caressObject.load_module(RESETMODULE, self._cid,
                                                CARESS.Value(l=0))
        self.log.debug('Reset module: %r' % (result,))
        if result != (CARESS.OK, LOADED):
            raise NicosError(self, 'Could not reset module')

    def doReset(self):
        self._reset()

    def _read(self):
        result = self._caressObject.read_module(1, self._cid)
        self.log.debug('read_module: %r' % (result,))
        if result[0] != CARESS.OK:
            raise CommunicationError(self, 'Could not read the CARESS module')
        return result[1:]

    def doRead(self, maxage=0):
        result = self._read()
        return result[1]._v

    def doStatus(self, maxage=0):
        state = self._read()[0]
        if state == DONE:
            return status.OK, 'preselection reached'
        elif state == LOADED:
            return status.OK, 'idle or paused'
        elif state == ACTIVE:
            return status.BUSY, ''

    def doIsCompleted(self):
        return self.doStatus()[0] != ACTIVE

    def doReadRunnumber(self):
        return readFileCounter(self.counterfile)

    def doWriteRunnumber(self, value):
        updateFileCounter(self.counterfile, value)


class Timer(Channel):

    def doInit(self, mode):
        if mode == SIMULATION:
            return

        Channel.doInit(self, mode)
        self._initObject(TIMER_ID)
        self._init('timer')

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._presetValue = preset['t']
        else:
            raise UsageError('preset must be "t"')

    def valueInfo(self):
        return Value(self.name, unit='s', type='time', fmtstr='%.3f'),

    def doReadUnit(self):
        return 's'

    def presetInfo(self):
        return ('t')


class Counter(Channel):

    parameters = {
        'config' : Param('Channel and trigger configuration',
                         type=str, mandatory=True,
                        ),
    }

    def doInit(self, mode):
        if mode == SIMULATION:
            return

        Channel.doInit(self, mode)
        self._initObject(COUNTER_ID)
        self._init('event')

        if len(self.config) == 0:
            with open('./acqiris.conf') as content_file:
                content = content_file.read()
                self.config = content

        result = self._caressObject.loadblock_module(SPECIALLOAD, self._cid,
                                                     1, len(self.config),
                                                     CARESS.Value(s=self.config))
        self.log.debug('Load block module: %r' % (result,))
        if result != (CARESS.OK, LOADED):
            raise ConfigurationError(self, 'Could not load block module')

    def doSetPreset(self, **preset):
        if 'n' in preset:
            self._presetValue = preset['n']
        else:
            raise UsageError('preset must be "n"')

    def valueInfo(self):
        return Value(self.name, unit='cts', errors='sqrt', type='counter',
                     fmtstr='%d'),

    def doReadUnit(self):
        return 'cts'

    def presetInfo(self):
        return ('n')
