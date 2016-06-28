#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

import time
import sys
import subprocess

try:
    from omniORB import CORBA
    import CosNaming

    import CARESS  # pylint: disable=F0401,E0611,W0403
    import _GlobalIDL  # pylint: disable=F0401,E0611,W0403,W0611
    import omniORB

    sys.modules['CARESS'] = sys.modules['nicos.devices.vendor.caress.CARESS']
    sys.modules['ABSDEV'] = sys.modules['nicos.devices.vendor.caress._GlobalIDL']
    omniORB.updateModule('CARESS')
    omniORB.updateModule('ABSDEV')
except ImportError:
    omniORB = None

from nicos.core import Param, Override, absolute_path, none_or, status, \
    SIMULATION, HasCommunication

from nicos.core.errors import CommunicationError, ConfigurationError, \
    InvalidValueError, NicosError, ProgrammingError


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

LOAD_NORMAL = 0

CARESS_MAPS = {}


class CARESSDevice(HasCommunication):
    """The CARESS base device."""

    _orb = None

    _kind = None

    parameters = {
        'config': Param('Device configuration/setup string',
                        type=str, mandatory=True, settable=False,
                        ),
        'nameserver': Param('Computer name running the CORBA name service',
                            type=none_or(str), mandatory=False, default=None,
                            ),
        'objname': Param('Name of the CORBA object',
                         type=none_or(str), mandatory=False, default=None,
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

    parameter_overrides = {
        'comtries': Override(default=5),
        'comdelay': Override(default=0.2),
    }

    _initialized = False

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

    def _is_corba_device(self):
        return self._device_kind() == CORBA_DEVICE

    def _device_kind(self):
        if not self._kind:
            tmp = self.config.split(None, 2)
            self._kind = int(tmp[1]) if len(tmp) > 1 else 0
        return self._kind

    def _initObject(self):
        if not self._orb:
            raise ProgrammingError(self, 'Programmer forgot to call _initORB')

        obj = self._orb.resolve_initial_references('NameService')
        rootContext = obj._narrow(CosNaming.NamingContext)

        if not rootContext:
            raise CommunicationError(self, 'Failed to narrow the root naming'
                                     ' context')
        if self._is_corba_device():
            try:
                tmp = self.objname.split('.') if self.objname else \
                    self.config.split()[2].split('.')
                if len(tmp) < 2:
                    tmp.append('caress_object')
                self.log.debug('%r' % tmp)
                obj = rootContext.resolve([CosNaming.NameComponent(tmp[0],
                                                                   tmp[1]), ])
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
            except CORBA.BAD_PARAM as ex:
                raise ConfigurationError(self, 'Name not found: %s' % (ex,))

        if CORBA.is_nil(self._caressObject):
            raise CommunicationError(self, 'Could not create a CARESS device')

        if hasattr(self._caressObject, 'init_module_orb'):
            self._caressObject.init_module = self._caressObject.init_module_orb

        self._cid = self._getCID(self.config.split(None, 2)[0])

    def _normalized_config(self):
        tmp = self.config.split()
        if tmp[2].count(':'):
            tmp[2] = tmp[2].split(':/')[1]
            return ' '.join(tmp)
        else:
            return self.config

    def _name_server(self):
        tmp = self.config.split()
        if tmp[2].count(':'):
            return tmp[2].split(':')[0]
        elif self.nameserver:
            return self.nameserver
        else:
            raise ConfigurationError(self, 'No name server configured. Please '
                                     'use the "nameserver" parameter or put it'
                                     'into the "config" parameter.')

    def _init(self):
        try:
            _config = self._normalized_config()
            if self._is_corba_device():
                res = self._caressObject.init_module(INIT_NORMAL, self._cid,
                                                     _config)
            else:
                res = self._caressObject.init_module(INIT_CONNECT, self._cid,
                                                     _config)
            self.log.debug('Init module (Connect): %r' % (res,))
            if res not in [(0, ON_LINE), (CARESS.OK, ON_LINE)]:
                res = self._caressObject.init_module(INIT_REINIT, self._cid,
                                                     _config)
                self.log.debug('Init module (Re-Init): %r' % (res,))
                if res not in[(0, ON_LINE), (CARESS.OK, ON_LINE)]:
                    self.log.error('Init module (Re-Init): %r (%d, %s)' %
                                   (res, self._cid, self.config))
                    raise NicosError(self, 'Could not initialize module!')
            self._initialized = True
        except CORBA.TRANSIENT as err:
            raise CommunicationError(self, 'could not init CARESS module %r '
                                     '(%d: %s)' % (err, self._cid, self.config))

    def doInit(self, mode):
        if mode == SIMULATION:
            return
        if not omniORB:
            raise ConfigurationError(self, 'There is no CORBA module found')
        self._initORB(['-ORBInitRef',
                       'NameService=corbaname::%s' % self._name_server(), ])
        self._initObject()
        self._init()

    def doShutdown(self):
        self._orb = None
        self._initialized = False

    def _read(self):
        if hasattr(self._caressObject, 'read_module'):
            # result = self._caressObject.read_module(0x80000000, self._cid)
            result, state, val = self._caressObject.read_module(0, self._cid)
            if result != CARESS.OK:
                raise CommunicationError(self,
                                         'Could not read the CARESS module')
            if hasattr(val, 'f'):
                return (state, val.f)
            return (state, val.l,)
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
        return self._caress_guard(self._read)[1]

    def doStatus(self, maxage=0):
        state = self._caress_guard(self._read)[0]
        if state == OFF_LINE:
            return status.ERROR, 'device is offline'
        elif state in (ACTIVE, ACTIVE1, COMBO_ACTIVE):
            return status.BUSY, ''
        else:
            return status.OK, 'idle or paused'
        return status.OK, 'idle'

    def _caress_guard_nolog(self, function, *args):

        if not self._initialized or not self._caressObject:
            CARESSDevice.doInit(self, self._mode)

#       self._com_lock.aquire()
        try:
            return function(*args)
        except (CORBA.COMM_FAILURE, CORBA.TRANSIENT) as err:
            tries = self.comtries - 1
            while True and tries > 0:
                self.log.warning('Remaining tries: %d' % tries)
                time.sleep(self.comdelay)
                if isinstance(err, CORBA.TRANSIENT):
                    CARESSDevice.doShutdown(self)
                    CARESSDevice.doInit(self, self._mode)
                time.sleep(self.comdelay)
                try:
                    return function(*args)
                except (CORBA.COMM_FAILURE, CORBA.TRANSIENT) as err:
                    tries -= 1
            raise CommunicationError(self, 'CARESS error: %s%r: %s' %
                                     (function.__name__, args, err))
        finally:
            pass
#           self._com_lock.release()

    _caress_guard = _caress_guard_nolog
