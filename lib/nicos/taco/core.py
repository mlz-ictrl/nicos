#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

import os
import sys
import threading
from time import sleep
from subprocess import Popen, PIPE

import TACOStates
from TACOClient import TACOError

from nicos.core import status, tacodev, intrange, Param, Override, NicosError, \
     ProgrammingError, CommunicationError, LimitError, InvalidValueError
from nicos.utils import HardwareStub
from nicos.cache.utils import cache_dump, cache_load


class TacoDevice(object):
    """Mixin class for TACO devices.

    Use it in concrete device classes like this::

        class Counter(TacoDevice, Measurable):
            taco_class = IO.Counter

            # more overwritten methods

    i.e., put TacoDevice first in the base class list.

    TacoDevice provides the following methods already:

    * `.doVersion` (returns TACO device version)
    * `.doPreinit` (creates the TACO device from the `tacodevice` parameter)
    * `.doRead` (reads the TACO device)
    * `.doStatus` (returns status.OK for ON and DEVICE_NORMAL, ERROR otherwise)
    * `.doReset` (resets the TACO device)
    * `.doReadUnit` (reads the unit parameter from the TACO device if not
      configured in setup)

    You can however override them and provide your own specialized
    implementation.

    TacoDevice subclasses will automatically log all calls to TACO if their
    loglevel is DEBUG.

    TacoDevice also has the following class attributes, which can be overridden
    in derived classes:

    * `taco_class` -- the Python class to use for the TACO client
    * `taco_resetok` -- a boolean value indicating if the device can be reset
      during connection if it is in error state
    * `taco_errorcodes` -- a dictionary mapping TACO error codes to NICOS
      exception classes

    The following utility methods are provided:

    .. automethod:: _taco_guard
    .. automethod:: _taco_multitry
    .. automethod:: _taco_update_resource
    .. automethod:: _create_client
    """

    parameters = {
        'tacodevice':  Param('TACO device name', type=tacodev, mandatory=True,
                             preinit=True),
        'tacotimeout': Param('TACO client network timeout', unit='s',
                             default=3, settable=True, preinit=True),
        'tacotries':   Param('Number of tries per TACO call', default=1,
                             type=intrange(1, 10), settable=True),
        'tacodelay':   Param('Delay between retries', unit='s', default=0.1,
                             settable=True),
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
        if self.loglevel == 'debug':
            self._taco_guard = self._taco_guard_log
        if self.taco_class is None:
            raise ProgrammingError('missing taco_class attribute in class '
                                   + self.__class__.__name__)
        if self._mode != 'simulation':
            self._dev = self._create_client()

    def _setMode(self, mode):
        super(TacoDevice, self)._setMode(mode)
        # remove the TACO device on entering simulation mode, to prevent
        # accidental access to the hardware
        if mode == 'simulation':
            self._dev = HardwareStub(self)

    def doVersion(self):
        return [(self.tacodevice,
                 self._taco_guard(self._dev.deviceVersion))]

    def doRead(self):
        return self._taco_guard(self._dev.read)

    def doStatus(self):
        state = self._taco_guard(self._dev.deviceState)
        if state in (TACOStates.ON, TACOStates.DEVICE_NORMAL):
            return (status.OK, TACOStates.stateDescription(state))
        elif state in (TACOStates.RAMP,):
            return (status.BUSY, TACOStates.stateDescription(state))
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

    def doUpdateLoglevel(self, value):
        super(TacoDevice, self).doUpdateLoglevel(value)
        self._taco_guard = value == 'debug' and self._taco_guard_log or \
                           self._taco_guard_nolog

    # internal utilities

    def _create_client(self, devname=None, class_=None, resetok=None,
                       timeout=None):
        """Create a new TACO client to the device given by *devname*, using the
        Python class *class_*.  Initialize the device in a consistent state,
        handling eventual errors.

        If no arguments are given, the values of *devname*, *class_*, *resetok*
        and *timeout* are taken from the class attributes *taco_class* and
        *taco_resetok* as well as the device parameters *tacodevice* and
        *tacotimeout*.  This is done during `.doPreinit`, so that you usually
        don't have to call this method in TacoDevice subclasses.

        You can use this method to create additional TACO clients in a device
        implementation that uses more than one TACO device.
        """
        if devname is None:
            devname = self.tacodevice
        if class_ is None:
            class_ = self.taco_class
        if resetok is None:
            resetok = self.taco_resetok
        if timeout is None:
            timeout = self.tacotimeout

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

        return dev

    def _taco_guard_log(self, function, *args):
        """Like _taco_guard(), but log the call."""
        self.log.debug('TACO call: %s%r' % (function.__name__, args))
        self.__lock.acquire()
        try:
            ret = function(*args)
        except TACOError, err:
            # for performance reasons, starting the loop and querying
            # self.tacotries only triggers in the error case
            if self.tacotries > 1:
                tries = self.tacotries - 1
                self.log.warning('TACO %s failed, retrying up to %d times' %
                                 (function.__name__, tries), exc=1)
                while True:
                    sleep(self.tacodelay)
                    tries -= 1
                    try:
                        ret = function(*args)
                        self.log.debug('TACO return: %r' % ret)
                        return ret
                    except TACOError, err:
                        if tries == 0:
                            break  # and fall through to _raise_taco
                        self.log.warning('TACO %s failed again' %
                                         function.__name__, exc=1)
            self._raise_taco(err)
        else:
            self.log.debug('TACO return: %r' % ret)
            return ret
        finally:
            self.__lock.release()

    def _taco_guard_nolog(self, function, *args):
        """Try running the TACO function, and raise a NicosError on exception.

        A more specific NicosError subclass is chosen if appropriate.  For
        example, database-related errors are converted to `.CommunicationError`.
        A TacoDevice subclass can add custom error code to exception class
        mappings by using the `.taco_errorcodes` class attribute.

        If the `tacotries` parameter is > 1, the call is retried accordingly.
        """
        self.__lock.acquire()
        try:
            return function(*args)
        except TACOError, err:
            # for performance reasons, starting the loop and querying
            # self.tacotries only triggers in the error case
            if self.tacotries > 1:
                tries = self.tacotries - 1
                self.log.warning('TACO %s failed, retrying up to %d times' %
                                 (function.__name__, tries))
                while True:
                    sleep(self.tacodelay)
                    tries -= 1
                    try:
                        return function(*args)
                    except TACOError, err:
                        if tries == 0:
                            break  # and fall through to _raise_taco
            self._raise_taco(err, '%s%r' % (function.__name__, args))
        finally:
            self.__lock.release()

    _taco_guard = _taco_guard_nolog

    def _taco_update_resource(self, resname, value):
        """Update the TACO resource *resname* to *value* (both must be strings),
        switching the device off and on.
        """
        self.__lock.acquire()
        try:
            self.log.debug('TACO resource update: %s %s' %
                           (resname, value))
            self._dev.deviceOff()
            self._dev.deviceUpdateResource(resname, value)
            self._dev.deviceOn()
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
        if code in self.taco_errorcodes:
            cls = self.taco_errorcodes[code]
        elif code < 50:
            # error numbers 0-50: RPC call errors
            cls = CommunicationError
        elif 400 <= code < 500:
            # error number 400-499: database system error messages
            cls = CommunicationError
        elif code == 4017:
            # range error
            cls = LimitError
        elif code == 4018:
            # invalid value
            cls = InvalidValueError
        elif code == 4024:
            # IO error
            cls = CommunicationError
        msg = '[TACO %d] %s' % (err.errcode, err)
        if addmsg is not None:
            msg = addmsg + ': ' + msg
        exc = cls(self, msg, tacoerr=err.errcode)
        raise exc, None, tb

    def _taco_multitry(self, what, tries, func, *args):
        """Try the TACO method *func* with given *args* for the number of times
        given by *tries*.  On each failure, a warning log message is emitted.
        If the device is in error state after a try, it is reset.  If the number
        of tries is exceeded, the error from the call is re-raised.

        *what* is a string that explains the call; it is used in the warning
        messages.
        """
        while True:
            tries -= 1
            try:
                return self._taco_guard(func, *args)
            except NicosError:
                if tries <= 0:
                    raise
                self.log.warning('%s failed; trying again' % what)
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


class ProxyTacoDevice(TacoDevice):

    def _create_client(self, devname=None, class_=None, resetok=None,
                       timeout=None):
        if class_ is None:
            class_ = self.taco_class
        if devname is None:
            devname = self.tacodevice
        mod = class_.__module__
        cls = class_.__name__
        return TacoStub(mod, cls, devname)
