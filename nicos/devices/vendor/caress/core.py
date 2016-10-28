#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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

import subprocess
import sys

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

from nicos import session
from nicos.core import HasCommunication, Override, POLLER, Param, SIMULATION, \
    absolute_path, none_or, status
from nicos.core.errors import CommunicationError, ConfigurationError, \
    InvalidValueError, NicosError, ProgrammingError


CORBA_DEVICE = 500

LOADMASTER = 14
LOADSLAVE = 15
RESETMODULE = 16
SPECIALLOAD = 18

MODULE_ERROR = -1
NOT_ACTIVE = 1
ACTIVE = 2
DONE = 3
LOADED = 4
ACTIVE1 = 5
COMBO_ACTIVE = 6

OFF_LINE = 0
ON_LINE = 1
MANUAL_MODE = 2
NOT_DEFINED = 3

INIT_NORMAL = 0
INIT_REINIT = 1
INIT_CONNECT = 4

READBLOCK_NORMAL = 0
READBLOCK_SINGLE = 1
READBLOCK_MULTI = 2

LOAD_NORMAL = 0


class CARESSDevice(HasCommunication):
    """The CARESS base device."""

    _orb = None

    _kind = None

    _used_counter = 0

    _caressObject = None

    _initialized = False

    _caress_name = ''

    _caress_maps = {}

    _caress_initialized = False

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
        'absdev': Param('CORBA object is a the legacy absdev device',
                        type=bool, default=True, settable=False),
        'loadblock': Param('Additional init block',
                           type=str, settable=False, default=''),
        'cid': Param('CARESS device ID',
                     type=int, settable=False, userparam=False),
    }

    parameter_overrides = {
        'comtries': Override(default=5),
        'comdelay': Override(default=0.2),
    }

    def _initORB(self, args):
        if not self._orb:
            self._orb = CORBA.ORB_init(args, CORBA.ORB_ID)

    def _getCID(self, device):
        if session.sessiontype == POLLER:
            while not self.cid:
                session.delay(0.5)
            return self.cid
        self.log.debug('Get CARESS device ID: %r' % (device,))
        answer = subprocess.Popen('cd %s && %s/dump_u1 -n %s' %
                                  (self.caresspath, self.toolpath, device, ),
                                  shell=True,
                                  stdout=subprocess.PIPE).stdout.read()
        self._caress_name = device
        if answer in ('', None):
            if not CARESSDevice._caress_maps:
                CARESSDevice._caress_maps[device] = 4096
            elif device not in CARESSDevice._caress_maps:
                CARESSDevice._caress_maps[device] = 1 + \
                    max(CARESSDevice._caress_maps.values())
            res = CARESSDevice._caress_maps[device]
        else:
            res = int(answer.split('=')[1])
        self.log.debug('Get CARESS device ID: %r' % (res,))
        return res

    def _is_corba_device(self):
        return self._device_kind() == CORBA_DEVICE and (not self.absdev)

    def _device_kind(self):
        if not self._kind:
            tmp = self.config.split(None, 2)
            self._kind = int(tmp[1]) if len(tmp) > 1 else 0
        return self._kind

    def _initObject(self):
        if not self._orb:
            raise ProgrammingError(self, 'Programmer forgot to call _initORB')

        obj = self._orb.resolve_initial_references('NameService')
        _root_context = obj._narrow(CosNaming.NamingContext)

        if not _root_context:
            raise CommunicationError(self, 'Failed to narrow the root naming'
                                     ' context')
        if self._is_corba_device():
            try:
                tmp = self.objname.split('.') if self.objname else \
                    self.config.split()[2].split('.')
                if len(tmp) < 2:
                    tmp.append('caress_object')
                self.log.debug('%r' % tmp)
                obj = _root_context.resolve([CosNaming.NameComponent(tmp[0],
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

        _cid = self._getCID(self.config.split(None, 2)[0])
        if session.sessiontype != POLLER:
            self._setROParam('cid', _cid)
            if self._cache:
                self._cache.invalidate(self, 'cid')

    def _normalized_config(self):
        tmp = self.config.split()
        if tmp[2].count(':') and not self.absdev:
            tmp[2] = tmp[2].split(':/')[1]
            return ' '.join(tmp)
        else:
            return self.config

    def _name_server(self):
        tmp = self.config.split()
        if tmp[2].count(':') and not self.absdev:
            return tmp[2].split(':')[0]
        elif self.nameserver:
            return self.nameserver
        else:
            raise ConfigurationError(self, 'No name server configured. Please '
                                     'use the "nameserver" parameter or put it'
                                     'into the "config" parameter.')

    def _init(self):
        try:
            if session.sessiontype != POLLER:
                if hasattr(self._caressObject, 'init_system_orb'):
                    if not CARESSDevice._caress_initialized:
                        self.log.debug(self, 'initialize the CARESS absdev '
                                       'container')
                        if self._caressObject.init_system_orb(0)[0] in \
                           (0, CARESS.OK):
                            CARESSDevice._caress_initialized = True
                        else:
                            raise CommunicationError(self, 'could not '
                                                     'initialize CARESS absdev'
                                                     ' container')

            _config = self._normalized_config()

            res = self._caressObject.init_module(INIT_CONNECT, self.cid,
                                                 _config)
            self.log.debug(self, 'INIT_CONNECT: %r' % ((res, )))
            if res[0] in (0, CARESS.OK):
                if res[1] == OFF_LINE:
                    res = self._caressObject.init_module(INIT_REINIT, self.cid,
                                                         _config)
            else:
                res = self._caressObject.init_module(INIT_NORMAL, self.cid,
                                                     _config)
            self.log.debug('Init module (Connect): %r' % (res,))
            if res[0] not in (0, CARESS.OK) or res[1] == OFF_LINE:
                raise NicosError(self, 'Could not initialize module! (%r) %d' %
                                 ((res,), self._device_kind()))
            # res = self._caressObject.init_module(INIT_REINIT, self.cid,
            #                                          _config)
            # self.log.debug('Init module (Re-Init): %r' % (res,))
            # if res not in[(0, ON_LINE), (CARESS.OK, ON_LINE)]:
            #     self.log.error('Init module (Re-Init): %r (%d, %s)' %
            #                    (res, self.cid, self.config))
            if self._device_kind() == CORBA_DEVICE:
                if self.absdev:
                    res = self._caressObject \
                        .char_loadblock_module_orb(0, self.cid, 1,
                                                   len(self.loadblock), 16,
                                                   self.loadblock)
                else:
                    val = CARESS.Value(ab=self.loadblock)
                    res = self._caressObject \
                        .loadblock_module(0, self.cid, 1,
                                          len(self.loadblock), val)  # 16, val)
            self._initialized = True
            if not self._is_corba_device():
                CARESSDevice._used_counter += 1

        except CORBA.TRANSIENT as err:
            raise CommunicationError(self, 'could not init CARESS module %r '
                                     '(%d: %s)' % (err, self.cid, self.config))

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
        if session.mode == SIMULATION:
            return
        if session.sessiontype != POLLER:
            if self._caressObject and hasattr(self._caressObject,
                                              'release_system_orb'):
                if CARESSDevice._used_counter:
                    CARESSDevice._used_counter -= 1
                    if not CARESSDevice._used_counter:
                        if self._caressObject.release_system_orb(0) in \
                           (0, CARESS.OK):
                            CARESSDevice._caress_maps.clear()
                            CARESSDevice._caress_initialized = False
                        else:
                            raise NicosError(self, 'Could not release CARESS')
            self._setROParam('cid', 0)
            if self._cache:
                self._cache.invalidate(self, 'cid')
        self._orb = None
        self._initialized = False

    def _read(self):
        if not self.cid:
            raise InvalidValueError(self, 'Connection lost to CARESS')
        if hasattr(self._caressObject, 'read_module'):
            # result = self._caressObject.read_module(0x80000000, self.cid)
            result, state, val = self._caressObject.read_module(0, self.cid)
            if result != CARESS.OK:
                raise CommunicationError(self,
                                         'Could not read the CARESS module: %d'
                                         % self.cid)
            if hasattr(val, 'f'):
                return (state, val.f)
            return (state, val.l,)
        else:
            _ = ()
            self.log.debug(self, 'read module: %d' % self.cid)
            result = self._caressObject.read_module_orb(0, self.cid, _)
            self.log.debug('read_module: %r' % (result,))
            if result[0] != 0:
                raise CommunicationError(self,
                                         'Could not read the CARESS module: %d'
                                         % self.cid)
            if result[1][0].value() != self.cid:
                raise CommunicationError(self,
                                         'Answer from wrong module!: %d %r' %
                                         (self.cid, result[1][0]))
            if result[1][1].value() == OFF_LINE:
                raise NicosError(self, 'Module is off line!')
            if result[1][2].value() < 1:
                raise InvalidValueError(self, 'No position in data')
            return result[1][1].value(), result[1][4].value()

    def doRead(self, maxage=0):
        try:
            return self._caress_guard(self._read)[1]
        except (InvalidValueError, CommunicationError, NicosError):
            if session.sessiontype == POLLER:
                return None
            raise

    def doStatus(self, maxage=0):
        try:
            state = self._caress_guard(self._read)[0]
            if state == OFF_LINE:
                return status.ERROR, 'device is offline'
            elif state in (ACTIVE, ACTIVE1, COMBO_ACTIVE):
                return status.BUSY, 'moving or in manual mode'
            elif state == DONE:
                return status.OK, 'idle or paused'
            return status.OK, 'idle'
        except (InvalidValueError, CommunicationError, NicosError) as e:
            return status.ERROR, e.message

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
                session.delay(self.comdelay)
                if isinstance(err, CORBA.TRANSIENT):
                    CARESSDevice.doShutdown(self)
                    CARESSDevice.doInit(self, self._mode)
                session.delay(self.comdelay)
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
