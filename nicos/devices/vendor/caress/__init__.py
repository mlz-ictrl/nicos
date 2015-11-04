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

"""Devices via the CARESS device service."""

import sys
import subprocess

try:
    from omniORB import CORBA
    import CosNaming

    import CARESS  # pylint: disable=F0401,E0611,W0403
    import _GlobalIDL  # pylint: disable=F0401,E0611,W0403
    import omniORB

    sys.modules['CARESS'] = sys.modules['nicos.devices.vendor.caress.CARESS']
    sys.modules['ABSDEV'] = sys.modules['nicos.devices.vendor.caress._GlobalIDL']
    omniORB.updateModule('CARESS')
    omniORB.updateModule('ABSDEV')
except ImportError:
    omniORB = None

from nicos import session
from nicos.core import DeviceMixinBase, Param, Override, status, HasOffset, \
    Value, absolute_path, SIMULATION, POLLER
from nicos.devices.abstract import Motor as BaseMotor
from nicos.devices.generic.detector import ActiveChannel, TimerChannelMixin, \
    CounterChannelMixin

from nicos.core.errors import CommunicationError, ConfigurationError, \
    NicosError, ProgrammingError, InvalidValueError


CORBA_DEVICE = 500

LOADMASTER = 14
LOADSLAVE = 15
RESETMODULE = 16
SPECIALLOAD = 18

NOT_ACTIVE = 1
ACTIVE = 2
DONE = 3
LOADED = 4
ACTIVE1 = 5
COMBO_ACTIVE = 6

OFF_LINE = 0
ON_LINE = 1

INIT_NORMAL = 0
INIT_REINIT = 1
INIT_CONNECT = 4

READBLOCK_NORMAL = 0
READBLOCK_SINGLE = 1
READBLOCK_MULTI = 2

CARESS_MAPS = {}


class CARESSDevice(DeviceMixinBase):
    """The CARESS base device."""

    _orb = None

    parameters = {
        'config': Param('Device configuration/setup string',
                        type=str, mandatory=True,
                        ),
        'nameserver': Param('Computer name running the CORBA name service',
                            type=str, mandatory=True,
                            ),
        'objname': Param('Name of the CORBA object',
                         type=str, mandatory=True,
                         ),
        'caresspath': Param('Directory of the CARESS installation',
                            type=absolute_path,
                            default='/opt/caress/parameter', settable=False,
                            ),
        'toolpath': Param('Path to the dump_u1 program',
                          type=absolute_path, default='/opt/caress',
                          settable=False,
                          ),
    }

    def _initORB(self, args):
        if not self._orb:
            self._orb = CORBA.ORB_init(args, CORBA.ORB_ID)

    def _getCID(self, device):
        self.log.debug('Get CARESS device ID: %r' % (device,))
        answer = subprocess.Popen('cd %s && %s/dump_u1 -n %s' %
                                  (self.caresspath, self.toolpath, device, ),
                                  shell=True,
                                  stdout=subprocess.PIPE).stdout.read()
        if answer in ('', None):
            if device not in CARESS_MAPS:
                if not len(CARESS_MAPS):
                    CARESS_MAPS[device] = 4096
                else:
                    CARESS_MAPS[device] = 1 + max(CARESS_MAPS.values())
            res = CARESS_MAPS[device]
        else:
            res = int(answer.split('=')[1])
        self.log.debug('Get CARESS device ID: %r' % (res,))
        return res

    def _device_kind(self):
        return int(self.config.split(' ', 2)[1])

    def _initObject(self):
        if not self._orb:
            raise ProgrammingError(self, 'Programmer forgot to call _initORB')

        obj = self._orb.resolve_initial_references('NameService')
        rootContext = obj._narrow(CosNaming.NamingContext)

        if not rootContext:
            raise CommunicationError(self, 'Failed to narrow the root naming'
                                     ' context')
        if self._device_kind() == CORBA_DEVICE:
            try:
                obj = rootContext.resolve([CosNaming.NameComponent(
                                          self.objname, 'caress_object'), ])
            except CosNaming.NamingContext.NotFound as ex:
                raise ConfigurationError(self, 'Name not found: %s' % (ex,))
            self._caressObject = obj._narrow(CARESS.CORBADevice)
        else:
            try:
                self._caressObject = \
                    self._orb.string_to_object('corbaname::%s#%s.context/'
                                               'caress.context/'
                                               'server.context/absdev.object' %
                                               (self.nameserver, self.objname))
            except omniORB.CORBA.BAD_PARAM as ex:
                raise ConfigurationError(self, 'Name not found: %s' % (ex,))

        if CORBA.is_nil(self._caressObject):
            raise CommunicationError(self, 'Could not create a CARESS device')

        if hasattr(self._caressObject, 'init_module_orb'):
            self._caressObject.init_module = self._caressObject.init_module_orb

        self._cid = self._getCID(self.config.split(' ', 2)[0])

    def _init(self):
        if self._device_kind() == CORBA_DEVICE:
            res = self._caressObject.init_module(INIT_NORMAL, self._cid,
                                                 self.config)
        else:
            res = self._caressObject.init_module(INIT_CONNECT, self._cid,
                                                 self.config)
        self.log.debug('Init module (Connect): %r' % (res,))
        if res not in [(0, ON_LINE), (CARESS.OK, ON_LINE)]:
            res = self._caressObject.init_module(INIT_REINIT, self._cid,
                                                 self.config)
            self.log.debug('Init module (Re-Init): %r' % (res,))
            if res not in[(0, ON_LINE), (CARESS.OK, ON_LINE)]:
                self.log.error('Init module (Re-Init): %r' % (res,))
                raise NicosError(self, 'Could not initialize module!')
        self._initialized = True

    def doInit(self, mode):
        if not omniORB:
            raise ConfigurationError(self, 'There is no CORBA module found')
        self._initORB(['-ORBInitRef', 'NameService=corbaname::%s' %
                       (self.nameserver, ), ])
        self._initObject()
        if mode != SIMULATION:
            self._init()

    def doShutdown(self):
        self._initialized = False

    def _read(self):
        if hasattr(self._caressObject, 'read_module'):
            # result = self._caressObject.read_module(0x80000000, self._cid)
            result, status, val = self._caressObject.read_module(0, self._cid)
            if result != CARESS.OK:
                raise CommunicationError(self,
                                         'Could not read the CARESS module')
            return (status, val.l,)
        else:
            _ = ()
            result = self._caressObject.read_module_orb(0, self._cid, _)
            self.log.debug('read_module: %r' % (result,))
            if result[0] != 0:
                raise CommunicationError(self,
                                         'Could not read the CARESS module')
            if result[1][0].value() != self._cid:
                raise NicosError(self, 'Answer from wrong module!: %d %r' %
                                 (self._cid, result[1][0]))
            if result[1][1].value() == OFF_LINE:
                raise NicosError(self, 'Module is off line!')
            if result[1][2].value() < 1:
                raise InvalidValueError(self, 'No position in data')
            return result[1][1].value(), result[1][4].value()

    def doRead(self, maxage=0):
        return self._read()[1]

    def doStatus(self, maxage=0):
        state = self._read()[0]
        if state == OFF_LINE:
            return status.ERROR, 'device is offline'
        elif state in (ACTIVE, ACTIVE1, COMBO_ACTIVE):
            return status.BUSY, ''
        else:
            return status.OK, 'idle or paused'
        return status.OK, 'idle'


class Motor(HasOffset, CARESSDevice, BaseMotor):

    parameters = {
        'coderoffset': Param('Encoder offset',
                             type=float, default=0., unit='main',
                             settable=True, category='offsets', chatty=True,
                             ),
        '_started': Param('Indicator to signal motor is started',
                          type=bool, default=False, settable=False,
                          ),
    }

    parameter_overrides = {
        'precision': Override(default=0.01)
    }

    def doInit(self, mode):
        # BaseMotor.doInit(self, mode)
        CARESSDevice.doInit(self, mode)
        self._setROParam('_started', False)
        if session.sessiontype == POLLER or mode == SIMULATION:
            return

        is_readable = True
        if hasattr(self._caressObject, 'is_readable_module'):
            is_readable = self._caressObject.is_readable_module(self._cid)
        self.log.debug('Readable module: %r' % (is_readable,))

        if hasattr(self._caressObject, 'is_drivable_module'):
            is_drivable = self._caressObject.is_drivable_module(self._cid)
        else:
            is_drivable = self._device_kind() in [3, 7, 13, 14, 15, 23, 24, 25,
                                                  28, 29, 30, 31, 32, 33, 37,
                                                  39, 40, 41, 43, 44, 45, 49,
                                                  50, 51, 53, 54, 56, 62, 67,
                                                  68, 70, 71, 72, 73, 76, 100,
                                                  103, 105, 106, 107, 108, 110,
                                                  111, 112, 114, 115, 123, 124,
                                                  125, 126, ]
        self.log.debug('Driveable module: %r' % (is_drivable,))
        if not (is_drivable or is_readable):
            raise ConfigurationError(self, 'Object is not a moveable module')

    def doStart(self, target):
        self.log.debug('target : %r' % (target,))
        target += (self.coderoffset + self.offset)
        timeout = 0
        if hasattr(self._caressObject, 'drive_module'):
            result = self._caressObject.drive_module(0, self._cid, target,
                                                     timeout)
            if result[0] != CARESS.OK:
                raise NicosError(self, 'Could not start the device')
        else:
            params = []
            params.append(CORBA.Any(CORBA._tc_long, self._cid))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # status placeholder
            params.append(CORBA.Any(CORBA._tc_long, 2))  # 2 values
            params.append(CORBA.Any(CORBA._tc_long, 5))  # type 32 bit float
            params.append(CORBA.Any(CORBA._tc_float, target))
            params.append(CORBA.Any(CORBA._tc_float, self.precision))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # no next module
            result = self._caressObject.drive_module_orb(0, params, 0, timeout)
            if result[0] != 0:
                raise NicosError(self, 'Could not start the device')
        self._setROParam('_started', True)

    def doRead(self, maxage=0):
        return self._read()[1] - (self.coderoffset + self.offset)

    def doStatus(self, maxage=0):
        state = CARESSDevice.doStatus(self, maxage)
        if self._started and state[0] == status.OK:
            self.doStop()
            self._setROParam('_started', False)
        return state

    def doStop(self):
        if hasattr(self._caressObject, 'stop_module'):
            result = self._caressObject.stop_module(11, self._cid)
            if result in [(CARESS.OK, ACTIVE), (CARESS.OK, ACTIVE1)]:
                raise NicosError(self, 'Could not stop the module')
        else:
            result = self._caressObject.stop_module_orb(11, self._cid)
            if result in [(0, ACTIVE), (0, ACTIVE1)]:
                raise NicosError(self, 'Could not stop the module')

    def doSetPosition(self, pos):
        pass


class Channel(CARESSDevice, ActiveChannel):

    parameters = {
        'runnumber': Param('Run number',
                           type=int, settable=True,
                           ),
        'counterfile': Param('File storing the run number',
                             type=str, default='runid.txt',
                             ),
    }

    def doInit(self, mode):
        CARESSDevice.doInit(self, mode)
        if mode == SIMULATION:
            return
        if hasattr(self._caressObject, 'is_counting_module'):
            is_counting = self._caressObject.is_counting_module(self._cid)
        else:
            is_counting = self._device_kind() in [1, 2, 5, 8, 19, 20, 58, 59,
                                                  63, 64, 74, 101, 102, 109,
                                                  113, 116, 117, 121, 122]
        self.log.debug('Counting module: %r' % (is_counting,))
        if not is_counting:
            raise ConfigurationError(self, 'Object is not a measurable module')

    def doSetPreset(self, **preset):
        raise ProgrammingError(self, 'Channel.setPreset should not be called')

    def doStart(self):
        self._reset()

        if not self.ismaster:
            self._load_preset(LOADSLAVE)
            self._start(0)
        else:
            if isinstance(self, (Timer,)):
                value = int(self.preselection * 100)
            else:
                value = int(self.preselection)
            self._load_preset(LOADMASTER, value)
            self._start(0)
            self.runnumber += 1

    def _start(self, kind):
        if hasattr(self._caressObject, 'start_module'):
            result = self._caressObject.start_module(kind, self._cid,
                                                     self.runnumber, 0)
            if result[0] != CARESS.OK:
                raise NicosError(self, 'Could not start the module')
        else:
            result = self._caressObject.start_acquisition_orb(kind,
                                                              self.runnumber,
                                                              0)
            if result[0] != 0:
                raise NicosError(self, 'Could not start the module')

    def doFinish(self):
        self._break(0)
        self._break(1)

    def doStop(self):
        self.doFinish()

    def _break(self, kind=0):
        if hasattr(self._caressObject, 'stop_module'):
            result = self._caressObject.stop_module(kind, self._cid)
            if result[0] != CARESS.OK:
                raise NicosError('Could not set module into paused state!')
        elif self.ismaster:
            result = self._caressObject.stop_acquisition_orb(kind)
            if result[0] != 0:
                raise NicosError('Could not set module into paused state!')

    def doPause(self):
        self._break(0)

    def doResume(self):
        self._start(1)

    def _reset(self):
        self._load_preset(RESETMODULE)

    def _load_preset(self, kind, preset=0):
        if hasattr(self._caressObject, 'load_module'):
            result = self._caressObject.load_module(kind, self._cid,
                                                    CARESS.Value(l=preset))
            self.log.debug('Preset module: %r' % (result,))
            if result[0] != CARESS.OK:
                raise NicosError(self, 'Could not reset module')
        else:
            params = []
            params.append(CORBA.Any(CORBA._tc_long, self._cid))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # status placeholder
            params.append(CORBA.Any(CORBA._tc_long, 1))  # 1 value
            params.append(CORBA.Any(CORBA._tc_long, 2))  # 32 bit int type
            params.append(CORBA.Any(CORBA._tc_long, preset))
            params.append(CORBA.Any(CORBA._tc_long, 0))  # no next module
            result = self._caressObject.load_module_orb(kind, params, 0)
            self.log.debug('Preset module: %r' % (result,))
            if result[0] != 0:
                raise NicosError(self, 'Could not reset module')

    def doReset(self):
        self._reset()

    def doReadRunnumber(self):
        return 0
        # return readFileCounter(self.counterfile)

    def doWriteRunnumber(self, value):
        # updateFileCounter(self.counterfile, value)
        pass


class Timer(TimerChannelMixin, Channel):

    def doRead(self, maxage=0):
        return [self._read()[1] / 500.]


class Counter(CounterChannelMixin, Channel):

    def doRead(self, maxage=0):
        return [self._read()[1]]
