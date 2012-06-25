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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS-TANGO base classes."""

__version__ = "$Revision$"

import sys
import threading
from time import sleep

from TANGOStates import TANGOState

from nicos.core import status, tangodev, intrange, Param, NicosError, \
     ProgrammingError


class TangoDevice(object):
    """Mixin class for TANGO devices.

    Use it in concrete device classes like this::

        class Counter(TangoDevice, Measurable):
            tango_class = CounterClient.CounterClient

            # more overwritten methods

    i.e., put TangoDevice first in the base class list.

    TangoDevice provides the following methods already:

    * `.doVersion` (returns TANGO device version)
    * `.doPreinit` (creates the TANGO device from the `tangodevice` parameter)
    * `.doStatus` (returns status.OK for ON, BUSY for MOVING and RUNNING, ERROR for FAULT and ALARM, UNKNOWN otherwise)
    * `.doReset` (resets the TANGO device)

    You can however override them and provide your own specialized
    implementation.

    TangoDevice subclasses will automatically log all calls to TANGO if their
    loglevel is DEBUG.

    TangoDevice also has the following class attributes, which can be overridden
    in derived classes:

    * `tango_class` -- the Python class to use for the TANGO client
    * `tango_resetok` -- a boolean value indicating if the device can be reset
      during connection if it is in error state
    * `tango_errorcodes` -- a dictionary mapping TANGO error codes to NICOS
      exception classes

    The following utility methods are provided:

    .. automethod:: _tango_guard
    .. automethod:: _tango_multitry
    .. automethod:: _tango_update_resource
    .. automethod:: _create_client
    """

    parameters = {
        'tangodevice':  Param('TANGO device name', type=tangodev, mandatory=True,
                             preinit=True),
        'tangotimeout': Param('TANGO client network timeout', unit='s',
                             default=3, settable=True, preinit=True),
        'tangotries':   Param('Number of tries per TANGO call', default=1,
                             type=intrange(1, 10), settable=True),
        'tangodelay':   Param('Delay between retries', unit='s', default=0.1,
                             settable=True),
    }
    # the TANGO client class to instantiate
    tango_class = None
    # whether to call deviceReset() if the initial switch-on fails
    tango_resetok = True
    # additional TANGO error codes mapping to Nicos exception classes
    tango_errorcodes = {}
    # TANGO device instance
    _dev = None

    def doPreinit(self, mode):
        self.__lock = threading.Lock()
        if self.loglevel == 'debug':
            self._tango_guard = self._tango_guard_log
        if self.tango_class is None:
            raise ProgrammingError('missing tango_class attribute in class '
                                   + self.__class__.__name__)
        if mode != 'simulation':
            self._dev = self._create_client()

    def doStatus(self):
        state = self._tango_guard(self._dev.getDeviceState)
        statusStr = self._dev.getDeviceStatus()
        if state == TANGOState.ON:
            return (status.OK, statusStr)
        elif state in [TANGOState.MOVING,  TANGOState.RUNNING]:
            return (status.BUSY, statusStr)
        elif state in [TANGOState.FAULT,  TANGOState.ALARM]:
            return (status.ERROR, statusStr)
        return (status.UNKNOWN, statusStr)

    def doReset(self):
        self._tango_guard(self._dev.init)
        if self._tango_guard(self._dev.getDeviceState) == TANGOState.OFF:
            self._tango_guard(self._dev.on)

    def doUpdateTangotimeout(self, value):
        if self._dev:
            self._tango_guard(self._dev.setClientTimeout, int(value*1000))

    def doUpdateLoglevel(self, value):
        super(TangoDevice, self).doUpdateLoglevel(value)
        self._tango_guard = value == 'debug' and self._tango_guard_log or \
                           self._tango_guard_nolog

    # internal utilities

    def _create_client(self, devname=None, class_=None, resetok=None,
                       timeout=None):
        """Create a new TANGO client to the device given by *devname*, using the
        Python class *class_*.  Initialize the device in a consistent state,
        handling eventual errors.

        If no arguments are given, the values of *devname*, *class_*, *resetok*
        and *timeout* are taken from the class attributes *tango_class* and
        *tango_resetok* as well as the device parameters *tangodevice* and
        *tangotimeout*.  This is done during `.doPreinit`, so that you usually
        don't have to call this method in TangoDevice subclasses.

        You can use this method to create additional TANGO clients in a device
        implementation that uses more than one TANGO device.
        """

        if devname is None:
            devname = self.tangodevice
        if class_ is None:
            class_ = self.tango_class
        if resetok is None:
            resetok = self.tango_resetok
        if timeout is None:
            timeout = self.tangotimeout

        self.log.debug('creating %s TANGO device' % class_.__name__)

        try:
            dev = class_(devname)
            dev.getDeviceState()
        except RuntimeError, err:
            self._raise_tango(err, 'Could not connect to device %r; make sure '
                             'the device server is running' % devname)

        try:
            if timeout != 0:
                dev.setClientTimeout(int(timeout*1000))
        except RuntimeError, err:
            self.log.warning('Setting TANGO network timeout failed: '
                              '[TANGO] %s' % (err))

        try:
            if dev.getDeviceState() == TANGOState.OFF:
                dev.on()
        except RuntimeError, err:
            self.log.warning('Switching TANGO device %r on failed: '
                              '[TANGO] %s' % (devname, err))
            try:
                if dev.getDeviceState() == TANGOState.FAULT:
                    if resetok:
                        dev.init()
                dev.on()
            except RuntimeError, err:
                self._raise_tango(err, 'Switching device %r on after '
                                 'reset failed' % devname)

        # XXX: automatically wrap all TANGO methods with _tango_guard?
        return dev

    def _tango_guard_log(self, function, *args):
        """Like _tango_guard(), but log the call."""
        self.log.debug('TANGO call: %s%r' % (function.__name__, args))
        self.__lock.acquire()
        try:
            ret = function(*args)
        except RuntimeError, err:
            # for performance reasons, starting the loop and querying
            # self.tangotries only triggers in the error case
            if self.tangotries > 1:
                tries = self.tangotries - 1
                self.log.warning('TANGO %s failed, retrying up to %d times' %
                                 (function.__name__, tries), exc=1)
                while True:
                    sleep(self.tangodelay)
                    tries -= 1
                    try:
                        ret = function(*args)
                        self.log.debug('TANGO return: %r' % ret)
                        return ret
                    except RuntimeError, err:
                        if tries == 0:
                            break  # and fall through to _raise_tango
                        self.log.warning('TANGO %s failed again' %
                                         function.__name__, exc=1)
            self._raise_tango(err)
        else:
            self.log.debug('TANGO return: %r' % ret)
            return ret
        finally:
            self.__lock.release()

    def _tango_guard_nolog(self, function, *args):
        """Try running the TANGO function, and raise a NicosError on exception.

        A more specific NicosError subclass is chosen if appropriate.
        A TangoDevice subclass can add custom error code to exception class
        mappings by using the `.tango_errorcodes` class attribute.

        If the `tangotries` parameter is > 1, the call is retried accordingly.
        """
        self.__lock.acquire()
        try:
            return function(*args)
        except RuntimeError, err:
            # for performance reasons, starting the loop and querying
            # self.tangotries only triggers in the error case
            if self.tangotries > 1:
                tries = self.tangotries - 1
                self.log.warning('TANGO %s failed, retrying up to %d times' %
                                 (function.__name__, tries))
                while True:
                    sleep(self.tangodelay)
                    tries -= 1
                    try:
                        return function(*args)
                    except RuntimeError, err:
                        if tries == 0:
                            break  # and fall through to _raise_tango
            self._raise_tango(err, '%s%r' % (function.__name__, args))
        finally:
            self.__lock.release()

    _tango_guard = _tango_guard_nolog

    def _raise_tango(self, err, addmsg=None):
        """Raise a suitable NicosError for a given RuntimeError instance
        (Tango::DevFailed is currently mapped to RuntimeError."""
        tb = sys.exc_info()[2]
        cls = NicosError

        # XXX: Better error handling needs better SWIG wrapping

        msg = '[TANGO] %s' % (err)
        if addmsg is not None:
            msg = addmsg + ': ' + msg
        exc = cls(self, msg)
        raise exc, None, tb

    def _tango_multitry(self, what, tries, func, *args):
        """Try the TANGO method *func* with given *args* for the number of times
        given by *tries*.  On each failure, a warning log message is emitted.
        If the device is in error state after a try, it is reset.  If the number
        of tries is exceeded, the error from the call is re-raised.

        *what* is a string that explains the call; it is used in the warning
        messages.
        """
        while True:
            tries -= 1
            try:
                return self._tango_guard(func, *args)
            except NicosError:
                self.log.warning('%s failed; trying again' % what)
                if tries <= 0:
                    raise
                self.__lock.acquire()
                try:
                    if self._dev.getDeviceState() == TANGOState.FAULT:
                        self._dev.init()
                    self._dev.on()
                    sleep(0.5)
                except RuntimeError:
                    pass
                finally:
                    self.__lock.release()

