#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Base device classes for use in NICOS
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   $Author$
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""
Base device classes for usage in NICOS.
"""

import time

from nicm import nicos
from nicm import status, loggers
from nicm.utils import MergedAttrsMeta
from nicm.errors import ConfigurationError, ProgrammingError, UsageError, \
     LimitError, FixedError


class Configurable(object):
    """
    An object that has a list of parameters that are read from the configuration
    and have default values.
    """

    __metaclass__ = MergedAttrsMeta
    __mergedattrs__ = ['parameters', 'attached_devices']

    parameters = {
        'name': ('', False, 'The name of the device.'),
        'description': ('', False, 'A description of the device.'),
        'autocreate': (False, False, 'Whether the device is automatically '
                       'created when the setup is loaded.'),
        'loglevel': ('info', False, 'The logging level of the device.'),
    }

    attached_devices = {}

    def __init__(self, name, config):
        # initialize a logger for the device
        self._log = nicos.get_logger(name)
        for level in ('debug', 'info', 'warning', 'error', 'exception'):
            setattr(self, 'print' + level, getattr(self._log, level))

        # initialize parameters
        self._params = {}
        # make all parameter names lower-case
        config = dict((name.lower(), value) for (name, value) in config.items())
        for param, paraminfo in self.parameters.iteritems():
            param = param.lower()

            # check validity of parameter info
            if not isinstance(paraminfo, tuple) or len(paraminfo) != 3:
                raise ProgrammingError('%r device %r configuration parameter '
                                       'info should be a 3-tuple' %
                                       (name, param))
            default, mandatory, doc = paraminfo
            deftype = type(default)
            if deftype in (int, long, float):
                deftype = (int, long, float)

            # check the parameter type and set it in self._params
            if param in config:
                if not isinstance(config[param], deftype):
                    raise ConfigurationError(
                        '%s: %r configuration parameter has wrong type '
                        '(expected %s, found %s)' %
                        (name, param, type(default).__name__,
                         type(config[param]).__name__))
                self._params[param] = config[param]
            elif not mandatory:
                self._params[param] = default
            else:
                raise ConfigurationError('%s: missing configuration '
                                         'parameter %r' % (name, param))

            # create getter and setter methods for the parameter
            def getter(param=param):
                methodname = 'doGet' + param.title()
                if hasattr(self, methodname):
                    return getattr(self, methodname)()
                else:
                    return self._params[param.lower()]
            def setter(value, param=param):
                methodname = 'doSet' + param.title()
                if hasattr(self, methodname):
                    getattr(self, methodname)(value)
                else:
                    raise ConfigurationError(
                        '%s: cannot set the %s parameter' % (self, param))
            setattr(self, 'get' + param.title(), getter)
            setattr(self, 'set' + param.title(), setter)

        # initialize some standard parameters
        self._params['name'] = name
        if not self._params['description']:
            self._params['description'] = name
        # set loglevel (also checks validity explicitly)
        self.setPar('loglevel', self._params['loglevel'])

    def __str__(self):
        return self._params['name']

    def getPar(self, name):
        """Get a parameter of the device."""
        if name.lower() not in self.parameters:
            raise UsageError('device %s has no parameter %s' % (self, name))
        return getattr(self, 'get' + name.title())()

    def setPar(self, name, value):
        """Set a parameter of the device to a new value."""
        if name.lower() not in self.parameters:
            raise UsageError('%s: device has no parameter %s' % (self, name))
        getattr(self, 'set' + name.title())(value)

    def doSetLoglevel(self, value):
        if value not in loggers.loglevels:
            raise UsageError('%s: loglevel must be one of %s' % (self,
                             ', '.join(map(repr, loggers.loglevels.keys()))))
        self._log.setLevel(loggers.loglevels[value])
        self._params['loglevel'] = value

    def init(self):
        """Initialize the object; this is called when the object is created."""
        if hasattr(self, 'doInit'):
            self.doInit()

    def shutdown(self):
        """Shut down the object; called from destroy_device()."""
        if hasattr(self, 'doShutdown'):
            self.doShutdown()


class Device(Configurable):
    """
    Base class for all NICOS devices.
    """

    parameters = {
        'adev': ({}, False, 'A dictionary with attached devices.'),
    }

    def __init__(self, name, config):
        Configurable.__init__(self, name, config)

        # initialize attached devices
        adev = self._params['adev']
        for aname, cls in self.attached_devices.iteritems():
            if aname not in adev:
                raise ConfigurationError(
                    '%s: device misses device %r in adev list' % (self, aname))
            if adev[aname] is None:
                setattr(self, aname, None)
                continue
            if isinstance(cls, list):
                cls = cls[0]
                devlist = []
                setattr(self, aname, devlist)
                for i, devname in enumerate(adev[aname]):
                    dev = nicos.create_device(devname)
                    if not isinstance(dev, cls):
                        raise ConfigurationError(
                            '%s: device adev %r item %d has wrong type' %
                            (self, aname, i))
                    devlist.append(dev)
            else:
                dev = nicos.create_device(adev[aname])
                if not isinstance(dev, cls):
                    raise ConfigurationError(
                        '%s: device adev %r has wrong type' % (self, aname))
                setattr(self, aname, dev)

    def __repr__(self):
        if self.getPar('name') == self.getPar('description'):
            return '<device %s (a %s)>' % (self.getPar('name'),
                                           self.__class__.__name__)
        return '<device %s, %s (a %s)>' % (self.getPar('name'),
                                           self.getPar('description'),
                                           self.__class__.__name__)


class Readable(Device):
    """
    Base class for all readable devices.
    """

    parameters = {
        'fmtstr': ('%s', False, 'Format string for the device value.'),
        'unit': ('', True, 'Unit of the device main value.'),
        'histories': ([], False, 'List of history managers.'),
    }

    def __init__(self, name, config):
        Device.__init__(self, name, config)
        from nicm.history import History
        self.__histories = []
        histnames = self.getHistories() + nicos.get_system_device().getHistories()
        for histname in histnames:
            self.__histories.append(nicos.get_device(histname, History))

    def __call__(self):
        """Allow dev() as shortcut for read."""
        return self.read()

    def read(self):
        """Read the main value of the device and save it in the history."""
        value = self.doRead()
        timestamp = time.time()
        for history in self.__histories:
            try:
                history.put(self, 'value', timestamp, value)
            except Exception, err:
                self.printwarning('could not save value to %s: %s' %
                                  (history, err))
        return value

    def status(self):
        """Return the status of the device as one of the integer constants
        defined in the nicm.status module.
        """
        if hasattr(self, 'doStatus'):
            value = self.doStatus()
            if value not in status.statuses:
                raise ProgrammingError('%s: status return %r unknown' %
                                       (self, value))
            timestamp = time.time()
            for history in self.__histories:
                try:
                    history.put(self, 'status', timestamp, value)
                except Exception, err:
                    self.printwarning('could not save status to %s: %s' %
                                      (history, err))
            return value
        return status.UNKNOWN

    def reset(self):
        """Reset the device hardware.  Return status afterwards."""
        if hasattr(self, 'doReset'):
            self.doReset()
        return self.status()

    def format(self, value):
        """Format a value from self.read() into a human-readable string."""
        if hasattr(self, 'doFormat'):
            return self.Format(value)
        return self.getPar('fmtstr') % value

    def history(self, name='value', fromtime=None, totime=None):
        """Return a history of the parameter *name*."""
        for history in self.__histories:
            hist = history.get(self, name, fromtime, totime)
            if hist is not None:
                return hist

    def doSetUnit(self, value):
        self._params['unit'] = value

    def doSetFmtstr(self, value):
        self._params['fmtstr'] = value


class Startable(Readable):
    """
    Common base class for Moveable, Switchable and Countable.

    This is used for typechecking, e.g. when any device with a stop()
    method is required.
    """

    def __init__(self, name, config):
        Readable.__init__(self, name, config)
        self.__is_fixed = False

    def __call__(self, pos=None):
        """Allow dev() and dev(newpos) as shortcuts for read and start."""
        if pos is None:
            return self.read()
        return self.start(pos)

    def start(self, pos):
        """Start main action of the device."""
        if self.__is_fixed:
            raise FixedError('%s is fixed' % self)
        self.doStart(pos)

    def stop(self):
        """Stop main action of the device."""
        if self.__is_fixed:
            raise FixedError('%s is fixed' % self)
        if hasattr(self, 'doStop'):
            self.doStop()

    def wait(self):
        """Wait until main action of device is completed."""
        if hasattr(self, 'doWait'):
            self.doWait()
            # update device value in histories
            self.read()

    def isAllowed(self, pos):
        """Return a tuple describing the validity of the given position.

        The first item is a boolean indicating if the position is valid,
        the second item is a string with the reason if it is invalid.
        """
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(pos)
        return True, ''

    def fix(self):
        """Fix the device, i.e. don't allow movement anymore."""
        if self.__is_fixed:
            return
        if hasattr(self, 'doFix'):
            self.doFix()
        self.__is_fixed = True

    def release(self):
        """Release the device, i.e. undo the effect of fix()."""
        if not self.__is_fixed:
            return
        if hasattr(self, 'doRelease'):
            self.doRelease()
        self.__is_fixed = False


class Moveable(Startable):
    """
    Base class for all continuously moveable devices.
    """

    parameters = {
        # XXX put limit checks directly in this class
        'usermin': (0, False, 'User defined minimum of device value.'),
        'usermax': (0, False, 'User defined maximum of device value.'),
        'absmin': (0, False, 'Absolute minimum of device value.'),
        'absmax': (0, False, 'Absolute maximum of device value.'),
    }

    def init(self):
        Startable.init(self)
        self.__checkAbsLimits()
        self.__checkUserLimits(setthem=True)

    def start(self, pos):
        """Start movement of the device to a new position."""
        ok, why = self.isAllowed(pos)
        if not ok:
            raise LimitError('%s: moving to %r is not allowed: %s' %
                             (self, pos, why))
        Startable.start(self, pos)

    moveTo = start
    move = start

    def __checkAbsLimits(self):
        absmin = self.getAbsmin()
        absmax = self.getAbsmax()
        if not absmin and not absmax:
            raise ConfigurationError('%s: no absolute limits defined '
                                     '(absmin, absmax)' % self)
        if absmin >= absmax:
            raise ConfigurationError('%s: absolute minimum (%s) above the '
                                     'absolute maximum (%s)' %
                                     (self, absmin, absmax))

    def __checkUserLimits(self, setthem=False):
        absmin = self._params['absmin']
        absmax = self._params['absmax']
        usermin = self._params['usermin']
        usermax = self._params['usermax']
        if not usermin and not usermax and setthem:
            # if both not set (0) then use absolute min. and max.
            usermin = absmin
            usermax = absmax
            self._params['usermin'] = usermin
            self._params['usermax'] = usermax
        if usermin >= usermax:
            raise ConfigurationError('%s: user minimum (%s) above the user '
                                     'maximum (%s)' % (self, usermin, usermax))
        if usermin < absmin:
            raise ConfigurationError('%s: user minimum (%s) below the absolute '
                                     'minimum (%s)' % (self, usermin, absmin))
        if usermin > absmax:
            raise ConfigurationError('%s: user minimum (%s) above the absolute '
                                     'maximum (%s)' % (self, usermin, absmax))
        if usermax > absmax:
            raise ConfigurationError('%s: user maximum (%s) above the absolute '
                                     'maximum (%s)' % (self, usermin, absmax))
        if usermax < absmin:
            raise ConfigurationError('%s: user minimum (%s) below the absolute '
                                     'minimum (%s)' % (self, usermin, absmin))

    def isAllowed(self, target):
        if not self._params['usermin'] <= target <= self._params['usermax']:
            return False, 'limits are [%s, %s]' % (self._params['usermin'],
                                                   self._params['usermax'])
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(pos)
        return True, ''

    def doSetUsermin(self, value):
        """Set the user minimum value to value after checking the value against
        absolute limits and user maximum.
        """
        old = self._params['usermin']
        self._params['usermin'] = float(value)
        try:
            self.__checkUserLimits()
        except ConfigurationError, e:
            self._params['usermin'] = old
            raise

    def doSetUsermax(self, value):
        """Set the user maximum value to value after checking the value against
        absolute limits and user minimum.
        """
        old = self._params['usermax']
        self._params['usermax'] = float(value)
        try:
            self.__checkUserLimits()
        except ConfigurationError, e:
            self._params['usermax'] = old
            raise


class Switchable(Startable):
    """
    Base class for all switchable devices.

    The *switchlist* attribute must be a dictionary that maps human-readable
    values to "internal" values.
    """

    switchlist = {}

    def init(self):
        Readable.init(self)
        if not isinstance(self.switchlist, dict):
            raise ProgrammingError('%s: switchlist is not a dict' % self)
        self.__rswitchlist = dict((v, k) for (k, v) in self.switchlist.items())
        if len(self.__rswitchlist) != len(self.switchlist):
            raise ProgrammingError('%s: duplicate value in switchlist' % self)

    def start(self, pos):
        """Switch the device to a new value.

        The given position can be either a human-readable value from the
        switchlist, or the "internal" value.
        """
        realpos = self.switchlist.get(pos, pos)
        if realpos not in self.__rswitchlist:
            raise UsageError('%s: %r is not an acceptable switch value' %
                             (self, pos))
        ok, why = self.isAllowed(realpos)
        if not ok:
            raise LimitError('%s: switching to %r is not allowed: %s' %
                             (self, pos, why))
        Startable.start(self, realpos)

    switchTo = start
    switch = start

    def format(self, pos):
        """Format a value from self.read() into the corresponding human-readable
        value from the switchlist.
        """
        return self.__rswitchlist.get(pos, pos)


class Countable(Startable):
    """
    Base class for all counters.
    """

    def start(self, preset=None):
        """Start the counter.  If *preset* is None, use the current
        standard preset.
        """
        self.doStart(preset)

    count = start

    def stop(self):
        """Stop the counter."""
        self.doStop()

    def resume(self):
        """Resume the counter."""
        self.doResume()

    def clear(self):
        """Clear the counter value."""
        self.doClear()

    def wait(self):
        """Wait until the counting is complete."""
        self.doWait()

    def setPreset(self, value):
        """Set a new standard preset."""
        self.doSetPreset(value)
