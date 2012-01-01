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

"""Exception classes for usage in NICOS."""

__version__ = "$Revision$"


class NicosError(Exception):
    """
    The basic exception class for exceptions raised by NICOS.

    Every NicosError subclass has a "category" attribute, a string that is shown
    to the user instead of the exception class.

    The constructor also accepts a :class:`.Device` instance as its first
    argument, which is then used to display the error to the user as coming from
    this device.  For example::

       def doRead(self):
           if not self._ready:
               raise NicosError(self, 'device is not ready')
    """
    category = 'Error'
    device = None
    tacoerr = None

    def __init__(self, *args, **kwds):
        # store the originating device on the exception
        args = list(args)
        if args and not isinstance(args[0], basestring):
            self.device = args[0]
            args[0] = '[%s] ' % args[0].name
        self.__dict__.update(kwds)
        Exception.__init__(self, ''.join(args))


class ProgrammingError(NicosError):
    """
    Exception to be raised when an error in the code is detected.
    """
    category = 'Programming error'

class ConfigurationError(NicosError):
    """
    Exception to be raised when an error in the :term:`setup` is detected, or a
    device is supplied with invalid configuration data.
    """
    category = 'Configuration error'

class UsageError(NicosError):
    """
    Exception to be raised when user commands are used wrongly.

    When this exception is caught by the :term:`user command` handler, the help
    for the command that was executed is shown.
    """
    category = 'Usage error'

class InvalidValueError(NicosError):
    """
    Exception to be raised when the user gives an invalid value to a device
    (as a move target or parameter value).
    """
    category = 'Invalid value'

class ModeError(NicosError):
    """
    Exception to be raised when an action is not allowed in the current
    :term:`execution mode`.
    """
    category = 'Mode error'

class PositionError(NicosError):
    """
    Exception to be raised when a device detects an invalid position.
    """
    category = 'Position error'

class MoveError(NicosError):
    """
    Exception to be raised when moving a device is not possible.
    """
    category = 'Positioning error'

class LimitError(NicosError):
    """
    Exception to be raised when a requested move target is out of limits.
    """
    category = 'Out of bounds'

class CommunicationError(NicosError):
    """
    Exception to be raised when some hardware communication fails.
    """
    category = 'Communication error'

class TimeoutError(CommunicationError):
    """
    Exception to be raised when a timeout occurs.
    """
    category = 'Timeout'

class ComputationError(NicosError):
    """
    Exception to be raised when a computation (e.g. of physical values) fails.
    """
    category = 'Computation error'

class FixedError(NicosError):
    """
    Exception to be raised when moving a :term:`fix`\ ed device is attempted.
    """
    category = 'Device fixed'

class CacheLockError(ProgrammingError):
    """
    Exception to be raised when a :term:`cache lock` cannot be acquired.
    """
    def __init__(self, locked_by):
        self.locked_by = locked_by
        ProgrammingError.__init__(self, 'locked by ' + locked_by)
