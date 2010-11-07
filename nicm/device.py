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

"""Base device classes for usage in NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import time

from nicm import nicos
from nicm import status, loggers
from nicm.utils import AutoPropsMeta, getVersions, listof
from nicm.errors import ConfigurationError, ProgrammingError, UsageError, \
     LimitError, FixedError


class Device(object):
    """
    An object that has a list of parameters that are read from the configuration
    and have default values.
    """

    __metaclass__ = AutoPropsMeta
    __mergedattrs__ = ['parameters', 'attached_devices']

    parameters = {
        'name': (str, '', False, 'The name of the device.'),
        'description': (str, '', False, 'A description of the device.'),
        #'autocreate': (bool, False, False, 'Whether the device is '
        #               'automatically created when the setup is loaded.'),
        'loglevel': (str, 'info', False, 'The logging level of the device.'),
    }

    attached_devices = {}

    def __init__(self, name, **config):
        # _config: device configuration (all parameter names lower-case)
        self._config = dict((name.lower(), value)
                            for (name, value) in config.items())
        # _params: parameter values from config
        self._params = {'name': name}  # pre-set "name" for str(self) to work
        # _changedparams: set of all changed params for save()
        self._changedparams = set()
        # _adevs: "attached" device instances
        self._adevs = {}

        # initialize a logger for the device
        self._log = nicos.getLogger(name)
        for mn in ('debug', 'info', 'warning', 'error', 'exception'):
            setattr(self, 'print' + mn, getattr(self._log, mn))

    def __setattr__(self, name, value):
        # disallow modification of public attributes that are not parameters
        if name not in self.__class__.__dict__ and name[0] != '_' and \
               not name.startswith('print'):
            raise UsageError(self, 'device has no parameter %s, use '
                             'listparams() to show all' % name)
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        return self._params['name']

    def __repr__(self):
        if self.name == self.description:
            return '<device %s (a %s.%s)>' % (self.name,
                                              self.__class__.__module__,
                                              self.__class__.__name__)
        return '<device %s "%s" (a %s.%s)>' % (self.name,
                                               self.description,
                                               self.__class__.__module__,
                                               self.__class__.__name__)

    def getPar(self, name):
        """Get a parameter of the device."""
        if name.lower() not in self.parameters:
            raise UsageError(self, 'device has no parameter %s, use '
                             'listparams() to show all' % name)
        return getattr(self, name.lower())

    def setPar(self, name, value):
        """Set a parameter of the device to a new value."""
        if name.lower() not in self.parameters:
            raise UsageError(self, 'device has no parameter %s, use '
                             'listparams() to show all' % name)
        setattr(self, name.lower(), value)

    def doSetDescription(self, value):
        self._params['description'] = value

    def doSetLoglevel(self, value):
        if value not in loggers.loglevels:
            raise UsageError(self, 'loglevel must be one of %s' %
                             ', '.join(map(repr, loggers.loglevels.keys())))
        self._log.setLevel(loggers.loglevels[value])
        self._params['loglevel'] = value

    def init(self):
        """Initialize the object; this is called when the object is created."""

        if hasattr(self, 'doPreinit'):
            self.doPreinit()

        # validate and create attached devices
        for aname, cls in self.attached_devices.iteritems():
            if aname not in self._config:
                raise ConfigurationError(
                    self, 'device misses device %r in configuration' % aname)
            value = self._config[aname]
            if value is None:
                self._adevs[aname] = None
                continue
            if isinstance(cls, list):
                cls = cls[0]
                devlist = []
                self._adevs[aname] = devlist
                for i, devname in enumerate(value):
                    dev = nicos.createDevice(devname)
                    if not isinstance(dev, cls):
                        raise ConfigurationError(
                            self, 'device %r item %d has wrong type' %
                            (aname, i))
                    devlist.append(dev)
            else:
                dev = nicos.createDevice(value)
                if not isinstance(dev, cls):
                    raise ConfigurationError(
                        self, 'device %r has wrong type' % aname)
                self._adevs[aname] = dev

        # validate and assign parameters
        for param, paraminfo in self.parameters.iteritems():
            param = param.lower()
            if param == 'name':
                # already set
                continue
            pconv, default, mandatory, doc = paraminfo
            # determine parameter value to set
            if param in self._config:
                paramvalue = self._config[param]
                try:
                    paramvalue = pconv(paramvalue)
                except ValueError, err:
                    raise ConfigurationError(self, 'configuration parameter %s '
                                             'value %r invalid: %s' %
                                             (param, paramvalue, err))
            elif not mandatory:
                if default is None:
                    continue
                paramvalue = default
            else:
                raise ConfigurationError(self, 'missing configuration '
                                         'parameter %r' % param)
            # set parameter either via setter, or in _params
            if hasattr(self, 'doSet' + param.title()):
                setattr(self, param, paramvalue)
            else:
                self._params[param] = paramvalue

        if not self.description:
            self.description = self.name

        # call custom initialization
        if hasattr(self, 'doInit'):
            self.doInit()

        # record parameter changes from now on
        self._changedparams.clear()

    def info(self):
        """Return device information as an iterable of tuples (name, value)."""
        if hasattr(self, 'doInfo'):
            for item in self.doInfo():
                yield item

    def shutdown(self):
        """Shut down the object; called from NICOS.destroyDevice()."""
        if hasattr(self, 'doShutdown'):
            self.doShutdown()

    def version(self):
        """Return a list of versions for this component."""
        versions = getVersions(self)
        if hasattr(self, 'doVersion'):
            versions.extend(self.doVersion())
        return versions

    def save(self):
        code = []
        if hasattr(self, 'doSave'):
            code.append(self.doSave())
        for param in sorted(self._changedparams):
            code.append('%s.%s = %r\n' %
                        (self.name, param, self.getPar(param)))
        return ''.join(code)


class Readable(Device):
    """
    Base class for all readable devices.
    """

    parameters = {
        'fmtstr': (str, '%s', False, 'Format string for the device value.'),
        'unit': (str, '', True, 'Unit of the device main value.'),
        'histories': (listof(str), [], False, 'List of history managers.'),
    }

    def init(self):
        Device.init(self)
        from nicm.history import History
        self.__histories = []
        histnames = self.histories + nicos.system.histories
        for histname in histnames:
            self.__histories.append(nicos.getDevice(histname, History))

    def __call__(self, value=None):
        """Allow dev() as shortcut for read."""
        if value is not None:
            # give a nicer error message than "TypeError: takes 1 argument"
            raise UsageError(self, 'not a moveable device')
        return self.read()

    def read(self):
        """Read the main value of the device and save it in the history."""
        value = self.doRead()
        timestamp = time.time()
        for history in self.__histories:
            try:
                history.put(self, 'value', timestamp, value)
            except Exception:
                self.printwarning('could not save value to %s' % history,
                                  exc=True)
        return value

    def status(self):
        """Return the status of the device as one of the integer constants
        defined in the nicm.status module.
        """
        if hasattr(self, 'doStatus'):
            value = self.doStatus()
            if value not in status.statuses:
                raise ProgrammingError(self, 'status return %r unknown' % value)
            timestamp = time.time()
            for history in self.__histories:
                try:
                    history.put(self, 'status', timestamp, value)
                except Exception:
                    self.printwarning('could not save status to %s' % history,
                                      exc=True)
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
        return self.fmtstr % value

    def history(self, name='value', fromtime=None, totime=None):
        """Return a history of the parameter *name*."""
        for history in self.__histories:
            hist = history.get(self, name, fromtime, totime)
            if hist is not None:
                return hist

    def info(self):
        """Automatically add device main value and status (if not OK)."""
        # XXX this can fail; catch exceptions around every item
        return
        yield ('value', self.read())
        value = self.status()
        if value != status.OK:
            yield ('status', status.statuses[value])
        for item in Device.info(self):
            yield item

    def doSetUnit(self, value):
        self._params['unit'] = value

    def doSetFmtstr(self, value):
        self._params['fmtstr'] = value


class Startable(Readable):
    """
    Common base class for Moveable, Switchable and Measurable.

    This is used for typechecking, e.g. when any device with a stop()
    method is required.
    """

    def __init__(self, name, **config):
        Readable.__init__(self, name, **config)
        self.__isFixed = False

    def __call__(self, pos=None):
        """Allow dev() and dev(newpos) as shortcuts for read and start."""
        if pos is None:
            return self.read()
        return self.start(pos)

    def start(self, pos):
        """Start main action of the device."""
        if self.__isFixed:
            raise FixedError(self, 'use release() first')
        self.doStart(pos)

    def stop(self):
        """Stop main action of the device."""
        if self.__isFixed:
            raise FixedError(self, 'use release() first')
        if hasattr(self, 'doStop'):
            self.doStop()

    def wait(self):
        """Wait until main action of device is completed.
        Return current value after waiting."""
        lastval = None
        if hasattr(self, 'doWait'):
            lastval = self.doWait()
        # if doWait() returns something, assume it's the latest value
        # (saves reading twice for wait functions that read the value anyway)
        if lastval is not None:
            return lastval
        # update device value in histories
        return self.read()

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
        if self.__isFixed:
            return
        if hasattr(self, 'doFix'):
            self.doFix()
        self.__isFixed = True

    def release(self):
        """Release the device, i.e. undo the effect of fix()."""
        if not self.__isFixed:
            return
        if hasattr(self, 'doRelease'):
            self.doRelease()
        self.__isFixed = False


class Moveable(Startable):
    """
    Base class for all continuously moveable devices.
    """

    parameters = {
        'usermin': (float, 0, False, 'User defined minimum of device value.'),
        'usermax': (float, 0, False, 'User defined maximum of device value.'),
        'absmin': (float, 0, False, 'Absolute minimum of device value.'),
        'absmax': (float, 0, False, 'Absolute maximum of device value.'),
    }

    def init(self):
        Startable.init(self)
        self.__checkAbsLimits()
        self.__checkUserLimits(setthem=True)

    def start(self, pos):
        """Start movement of the device to a new position."""
        ok, why = self.isAllowed(pos)
        if not ok:
            raise LimitError(self,
                             'moving to %r is not allowed: %s' % (pos, why))
        Startable.start(self, pos)

    moveTo = start
    move = start

    def __checkAbsLimits(self):
        absmin = self.absmin
        absmax = self.absmax
        if not absmin and not absmax:
            raise ConfigurationError(self, 'no absolute limits defined '
                                     '(absmin, absmax)')
        if absmin >= absmax:
            raise ConfigurationError(self, 'absolute minimum (%s) above the '
                                     'absolute maximum (%s)' % (absmin, absmax))

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
            raise ConfigurationError(self, 'user minimum (%s) above the user '
                                     'maximum (%s)' % (usermin, usermax))
        if usermin < absmin:
            raise ConfigurationError(self, 'user minimum (%s) below the absolute '
                                     'minimum (%s)' % (usermin, absmin))
        if usermin > absmax:
            raise ConfigurationError(self, 'user minimum (%s) above the absolute '
                                     'maximum (%s)' % (usermin, absmax))
        if usermax > absmax:
            raise ConfigurationError(self, 'user maximum (%s) above the absolute '
                                     'maximum (%s)' % (usermax, absmax))
        if usermax < absmin:
            raise ConfigurationError(self, 'user maximum (%s) below the absolute '
                                     'minimum (%s)' % (usermax, absmin))

    def isAllowed(self, target):
        if not self._params['usermin'] <= target <= self._params['usermax']:
            return False, 'limits are [%s, %s]' % (self._params['usermin'],
                                                   self._params['usermax'])
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(target)
        return True, ''

    def doSetUsermin(self, value):
        """Set the user minimum value to value after checking the value against
        absolute limits and user maximum.
        """
        if 'usermin' not in self._params:
            # first time from setup file
            self._params['usermin'] = float(value)
            return
        old = self._params['usermin']
        self._params['usermin'] = float(value)
        try:
            self.__checkUserLimits()
        except ConfigurationError:
            self._params['usermin'] = old
            raise

    def doSetUsermax(self, value):
        """Set the user maximum value to value after checking the value against
        absolute limits and user minimum.
        """
        if 'usermax' not in self._params:
            # first time from setup file
            self._params['usermax'] = float(value)
            return
        old = self._params['usermax']
        self._params['usermax'] = float(value)
        try:
            self.__checkUserLimits()
        except ConfigurationError:
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
            raise ProgrammingError(self, 'switchlist is not a dict')
        self.__rswitchlist = dict((v, k) for (k, v) in self.switchlist.items())
        if len(self.__rswitchlist) != len(self.switchlist):
            raise ProgrammingError(self, 'duplicate value in switchlist')

    def start(self, pos):
        """Switch the device to a new value.

        The given position can be either a human-readable value from the
        switchlist, or the "internal" value.
        """
        realpos = self.switchlist.get(pos, pos)
        if realpos not in self.__rswitchlist:
            raise UsageError(self, '%r is not an acceptable switch value' % pos)
        ok, why = self.isAllowed(realpos)
        if not ok:
            raise LimitError(self, 'switching to %r is not allowed: %s' %
                             (pos, why))
        Startable.start(self, realpos)

    switchTo = start
    switch = start

    def format(self, pos):
        """Format a value from self.read() into the corresponding human-readable
        value from the switchlist.
        """
        return self.__rswitchlist.get(pos, pos)


class Measurable(Startable):
    """
    Base class for devices used for data acquisition.
    """

    parameters = {
        'unit': (str, '', False, '(not used)'),
    }

    def start(self, **preset):
        """Start measurement."""
        self.doStart(**preset)

    def pause(self):
        """Pause the measurement, if possible.  Return True if paused
        successfully.
        """
        if hasattr(self, 'doPause'):
            return self.doPause()
        return False

    def resume(self):
        """Resume paused measurement."""
        if hasattr(self, 'doResume'):
            return self.doResume()

    def stop(self):
        """Stop measurement now."""
        self.doStop()

    def isCompleted(self):
        """Return true if measurement is complete."""
        return self.doIsCompleted()

    def wait(self):
        """Wait for completion of measurement."""
        while not self.isCompleted():
            time.sleep(0.1)

    def read(self):
        """Return the result of the last measurement."""
        result = self.doRead()
        if not isinstance(result, list):
            return [result]
        return result

    def valueInfo(self):
        """Return two lists: list of value names and list of value units."""
        return [], []
