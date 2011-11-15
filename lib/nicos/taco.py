#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS-TACO base classes."""

__version__ = "$Revision$"

import sys
import threading
from time import sleep

import TACOStates
from TACOClient import TACOError

from nicos import status
from nicos.utils import tacodev
from nicos.device import Param, Override
from nicos.errors import NicosError, ProgrammingError, CommunicationError


class TacoDevice(object):
    """Mixin class for TACO devices.

    Use it in concrete device classes like this:

        class Counter(TacoDevice, Countable):
            taco_class = IO.Counter

            # more overwritten methods

    i.e., put TacoDevice first in the base class list.
    """

    parameters = {
        'tacodevice':  Param('TACO device name', type=tacodev, mandatory=True,
                             preinit=True),
        'tacotimeout': Param('TACO client network timeout', unit='s',
                             default=3, settable=True, preinit=True),
        'tacolog':     Param('If true, log all TACO calls', type=bool,
                             settable=True, preinit=True),
    }

    parameter_overrides = {
        # the unit isn't mandatory -- TACO usually knows it already
        'unit':        Override(mandatory=False),
    }

    # the TACO client class to instantiate
    taco_class = None
    # whether to call deviceReset() if the initial switch-on fails
    taco_resetok = True
    # additional TACO error codes mapping to Nicos exception classes
    taco_errorcodes = {}
    # TACO device instance
    _dev = None

    def doPreinit(self):
        self.__lock = threading.Lock()
        if self.tacolog:
            self._taco_guard = self._taco_guard_log
        if self.taco_class is None:
            raise ProgrammingError('missing taco_class attribute in class '
                                   + self.__class__.__name__)
        if self._mode != 'simulation':
            self._dev = self._create_client()

    def doVersion(self):
        return [(self.tacodevice,
                 self._taco_guard(self._dev.deviceVersion))]

    def doRead(self):
        return self._taco_guard(self._dev.read)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state in (TACOStates.ON, TACOStates.DEVICE_NORMAL):
            return (status.OK, TACOStates.stateDescription(state))
        # rather status.UNKNOWN?
        return (status.ERROR, TACOStates.stateDescription(state))

    def doReset(self):
        self._taco_guard(self._dev.deviceReset)
        if self._taco_guard(self._dev.isDeviceOff):
            self._taco_guard(self._dev.deviceOn)

    def doReadUnit(self):
        # explicitly configured unit has precendence
        if 'unit' in self._config:
            return self._config['unit']
        if hasattr(self._dev, 'unit'):
            return self._taco_guard(self._dev.unit)
        return ''

    def doUpdateTacotimeout(self, value):
        if self._dev:
            self._taco_guard(self._dev.setClientNetworkTimeout, value)

    def doWriteTacolog(self, value):
        # automatically set the loglevel to debug, otherwise taco log
        # messages won't be emitted
        if value:
            self.loglevel = 'debug'

    def doUpdateTacolog(self, value):
        self._taco_guard = value and self._taco_guard_log or \
                           self._taco_guard_nolog

    # internal utilities

    def _create_client(self, devname=None, class_=None, resetok=None,
                       timeout=None):
        """
        Create a new TACO client and initialize the device in a
        consistent state, handling eventual errors.
        """
        if devname is None:
            devname = self.tacodevice
        if class_ is None:
            class_ = self.taco_class
        if resetok is None:
            resetok = self.taco_resetok
        if timeout is None:
            timeout = self.tacotimeout
        log = self.tacolog

        if log:
            self.log.debug('creating %s TACO device' % class_.__name__)

        try:
            dev = class_(devname)
            dev.deviceVersion()
        except TACOError, err:
            self._raise_taco(err, 'Could not connect to device %r; make sure '
                             'the device server is running' % devname)

        try:
            if timeout != 0:
                dev.setClientNetworkTimeout(timeout)
        except TACOError, err:
            self.log.warning('Setting TACO network timeout failed: '
                              '[TACO %d] %s' % (err.errcode, err))

        try:
            if dev.isDeviceOff():
                dev.deviceOn()
        except TACOError, err:
            self.log.warning('Switching TACO device %r on failed: '
                              '[TACO %d] %s' % (devname, err.errcode, err))
            try:
                if dev.deviceState() == TACOStates.FAULT:
                    if resetok:
                        dev.deviceReset()
                dev.deviceOn()
            except TACOError, err:
                self._raise_taco(err, 'Switching device %r on after '
                                 'reset failed' % devname)

        # XXX: automatically wrap all TACO methods with _taco_guard?
        return dev

    def _taco_guard_log(self, function, *args):
        """Like _taco_guard(), but log the call."""
        self.log.debug('TACO call: %s%r' % (function.__name__, args))
        self.__lock.acquire()
        try:
            ret = function(*args)
        except TACOError, err:
            self._raise_taco(err)
        else:
            self.log.debug('TACO return: %r' % ret)
            return ret
        finally:
            self.__lock.release()

    def _taco_guard_nolog(self, function, *args):
        """Try running the TACO function, and raise a NicosError on exception."""
        self.__lock.acquire()
        try:
            return function(*args)
        except TACOError, err:
            self._raise_taco(err, '%s%r' % (function.__name__, args))
        finally:
            self.__lock.release()

    _taco_guard = _taco_guard_nolog

    def _taco_update_resource(self, resname, value):
        """Update a TACO resource, switching the device off and on."""
        self.__lock.acquire()
        try:
            if self.tacolog:
                self.log.debug('TACO resource update: %s %s' %
                                (resname, value))
            self._dev.deviceOff()
            self._dev.deviceUpdateResource(resname, value)
            self._dev.deviceOn()
            if self.tacolog:
                self.log.debug('TACO resource update successful')
        except TACOError, err:
            self._raise_taco(err, 'While updating %s resource' % resname)
        finally:
            self.__lock.release()

    def _raise_taco(self, err, addmsg=None):
        """Raise a suitable NicosError for a given TACOError instance."""
        tb = sys.exc_info()[2]
        code = err.errcode
        cls = NicosError
        if code in (2, 16, 4019):
            # client call timeout or no network manager
            cls = CommunicationError
        elif 401 <= code < 499:
            # error number 401-499: database system error messages
            cls = CommunicationError
        elif code in self.taco_errorcodes:
            cls = self.taco_errorcodes[code]
        # TODO: add more cases
        msg = '[TACO %d] %s' % (err.errcode, err)
        if addmsg is not None:
            msg = addmsg + ': ' + msg
        exc = cls(self, msg, tacoerr=err.errcode)
        raise exc, None, tb

    def _taco_multitry(self, what, tries, func, *args):
        while True:
            tries -= 1
            try:
                return self._taco_guard(func, *args)
            except NicosError:
                self.log.warning('%s failed; trying again' % what)
                if tries <= 0:
                    raise
                self.__lock.acquire()
                try:
                    if self._dev.deviceState() == TACOStates.FAULT:
                        self._dev.deviceReset()
                    self._dev.deviceOn()
                    sleep(0.5)
                except TACOError:
                    pass
                finally:
                    self.__lock.release()


# XXX hack around segfaults, enable by renaming MTacoDevice to TacoDevice

import os
import sys
from subprocess import *
from nicos.cache.utils import cache_dump, cache_load

class TacoStub(object):
    def __init__(self, mod, cls, dev):
        from nicos import session
        self.mod = mod
        self.cls = cls
        self.dev = dev
        self.script = os.path.join(session.config.control_path,
                                   'bin', 'nicos-tacoexec')

    def __getattr__(self, cmd):
        def method(*args):
            n = 0
            while n < 5:
                p = Popen([sys.executable, self.script,
                           self.mod, self.cls, self.dev, cmd, cache_dump(args)],
                          stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                if err:
                    raise NicosError(err)
                if not out:
                    continue
                n += 1
                return cache_load(out)
            raise NicosError('command failed, no output')
        return method


class MTacoDevice(TacoDevice):

    def _create_client(self, devname=None, class_=None, resetok=None,
                       timeout=None):
        if class_ is None:
            class_ = self.taco_class
        if devname is None:
            devname = self.tacodevice
        mod = class_.__module__
        cls = class_.__name__
        return TacoStub(mod, cls, devname)
