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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Exception classes for usage in NICOS."""

from nicos.pycompat import string_types


class NicosError(Exception):
    """The basic exception class for exceptions raised by NICOS.

    Every NicosError subclass has a "category" attribute, a string that is
    shown to the user instead of the exception class.

    The constructor also accepts a :class:`.Device` instance as its first
    argument, which is then used to display the error to the user as coming
    from this device.  For example::

       def doRead(self, maxage=0):
           if not self._ready:
               raise NicosError(self, 'device is not ready')
    """
    category = 'Error'
    device = None
    tacoerr = None

    def __init__(self, *args, **kwds):
        # store the originating device on the exception
        args = list(args)
        nargs = len(args)
        if nargs:
            if args[0] is None:
                del args[0]
            elif not isinstance(args[0], string_types):
                self.device = args[0]
                prefix = '[%s] ' % args[0].name
                if nargs > 1 and args[1].startswith(prefix):
                    # do not add a prefix if it already exists
                    del args[0]
                else:
                    args[0] = prefix
        self.__dict__.update(kwds)
        Exception.__init__(self, ''.join(args))


class ProgrammingError(NicosError):
    """Exception to be raised when an error in the code is detected.

    This should not occur during normal operation.
    """
    category = 'Programming error'


class ConfigurationError(NicosError):
    """Exception to be raised when an error in the :term:`setup` is detected,
    or a device is supplied with invalid configuration data.
    """
    category = 'Configuration error'


class UsageError(NicosError):
    """Exception to be raised when user commands are used wrongly.

    When this exception is caught by the :term:`user command` handler, the help
    for the command that was executed is shown.
    """
    category = 'Usage error'


class InvalidValueError(NicosError):
    """Exception to be raised when the user gives an invalid value to a device
    (as a move target or parameter value).
    """
    category = 'Invalid value'


class ModeError(NicosError):
    """Exception to be raised when an action is not allowed in the current
    :term:`execution mode`.
    """
    category = 'Mode error'


class AccessError(NicosError):
    """Exception to be raised when an action is forbidden to the current user.

    Used by the `.requires` decorator.
    """
    category = 'Access denied'


class PositionError(NicosError):
    """Exception to be raised when a device detects an undefined position.

    For example, this should be raised when several coders do not agree.
    """
    category = 'Undefined position'


class MoveError(NicosError):
    """Exception to be raised when errors occur while moving a device."""
    category = 'Positioning error'


class LimitError(NicosError):
    """Exception to be raised when a requested move target is out of limits."""
    category = 'Out of bounds'


class CommunicationError(NicosError):
    """Exception to be raised when some hardware communication fails."""
    category = 'Communication error'


class HardwareError(NicosError):
    """Exception to be raised on fatal hardware errors."""
    category = 'Hardware failure'


class TimeoutError(NicosError):
    """Exception to be raised when a timeout waiting for hardware occurs.

    This is *not* a communication timeout; for that purpose
    `CommunicationError` should be used.
    """
    category = 'Timeout'


class ComputationError(NicosError):
    """Exception to be raised when a computation fails.

    Examples are the conversion of physical values to logical values.
    """
    category = 'Computation error'


class CacheLockError(NicosError):
    """Exception to be raised when a :term:`cache lock` cannot be acquired."""
    category = 'Cannot lock device in cache'

    def __init__(self, locked_by):
        self.locked_by = locked_by
        NicosError.__init__(self, 'locked by ' + locked_by)


class CacheError(NicosError):
    """Exception raised on cache connection errors."""
    category = 'Cannot connect to cache server'


class SPMError(NicosError):
    """Exception raised when invalid SPM syntax is entered."""
    category = 'Cannot process input'
