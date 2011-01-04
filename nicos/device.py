#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""Base device classes for usage in NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from time import time as currenttime, sleep

from nicos import session
from nicos import status, loggers
from nicos.utils import AutoPropsMeta, Param, Override, getVersions
from nicos.errors import ConfigurationError, ProgrammingError, UsageError, \
     LimitError, FixedError, ModeError, CommunicationError, CacheLockError


class Device(object):
    """
    An object that has a list of parameters that are read from the configuration
    and have default values.

    Subclasses *can* implement:

    * doPreinit()
    * doInit()
    * doShutdown()
    * doVersion()
    * doSave()
    """

    __metaclass__ = AutoPropsMeta
    __mergedattrs__ = ['parameters', 'parameter_overrides', 'attached_devices']

    parameters = {
        'description': Param('A description of the device', type=str,
                             settable=True),
        'lowlevel':    Param('Whether the device is not interesting to users',
                             type=bool, default=False),
        'loglevel':    Param('The logging level of the device', type=str,
                             default='info', settable=True),
    }
    parameter_overrides = {}
    attached_devices = {}

    def __init__(self, name, **config):
        # register self in device registry
        if name in session.devices:
            raise ProgrammingError('device with name %s already exists' % name)
        session.devices[name] = self

        if session.system.mode == 'simulation':
            raise UsageError('no new devices can be created in simulation mode')

        self.__dict__['name'] = name
        # _config: device configuration (all parameter names lower-case)
        self._config = dict((name.lower(), value)
                            for (name, value) in config.items())
        # _params: parameter values from config
        self._params = {}
        # _changedparams: set of all changed params for save()
        self._changedparams = set()
        # _infoparams: cached list of parameters to get on info()
        self._infoparams = []
        # _adevs: "attached" device instances
        self._adevs = {}
        # superdevs: reverse adevs for dependency tracking
        self._sdevs = set()
        # execution mode
        self._mode = session.system.mode

        # initialize a logger for the device
        self._log = session.getLogger(name)
        for mn in ('debug', 'info', 'warning', 'error', 'exception'):
            setattr(self, 'print' + mn, getattr(self._log, mn))

        try:
            # initialize device
            self.init()
        except Exception:
            # if initialization fails, remove from device registry
            del session.devices[name]
            # and remove from adevs' sdevs
            for adev in self._adevs.values():
                if isinstance(adev, list):
                    [real_adev._sdevs.discard(self.name) for real_adev in adev]
                elif adev is not None:
                    adev._sdevs.discard(self.name)
            raise
        else:
            # set correct log level now that the parameter is initialized
            self._log.setLevel(loggers.loglevels[self.loglevel])

    def __setattr__(self, name, value):
        # disallow modification of public attributes that are not parameters
        if name not in self.__class__.__dict__ and name[0] != '_' and \
               not name.startswith('print'):
            raise UsageError(self, 'device has no parameter %s, use '
                             'listparams(%s) to show all' % (name, self))
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        return self.name

    def __repr__(self):
        if not self.description:
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
                             'listparams(%s) to show all' % (name, self))
        return getattr(self, name.lower())

    def setPar(self, name, value):
        """Set a parameter of the device to a new value."""
        if name.lower() not in self.parameters:
            raise UsageError(self, 'device has no parameter %s, use '
                             'listparams(%s) to show all' % (name, self))
        setattr(self, name.lower(), value)

    def doWriteLoglevel(self, value):
        if value not in loggers.loglevels:
            raise UsageError(self, 'loglevel must be one of %s' %
                             ', '.join(map(repr, loggers.loglevels.keys())))
        self._log.setLevel(loggers.loglevels[value])

    def init(self):
        """Initialize the object; this is called when the object is created."""

        # validate and create attached devices
        for aname, cls in sorted(self.attached_devices.iteritems()):
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
                    dev = session.getDevice(devname)
                    if not isinstance(dev, cls):
                        raise ConfigurationError(
                            self, 'device %r item %d has wrong type' %
                            (aname, i))
                    devlist.append(dev)
                    dev._sdevs.add(self.name)
            else:
                dev = session.getDevice(value)
                if not isinstance(dev, cls):
                    raise ConfigurationError(
                        self, 'device %r has wrong type' % aname)
                self._adevs[aname] = dev
                dev._sdevs.add(self.name)

        self._cache = self._getCache()

        def _init_param(param, paraminfo):
            param = param.lower()
            # mandatory parameters must be in config, regardless of cache
            if paraminfo.mandatory and param not in self._config:
                raise ConfigurationError(self, 'missing configuration '
                                         'parameter %r' % param)
            # try to get from cache
            value = None
            if self._cache:
                value = self._cache.get(self, param)
            if value is not None:
                if param in self._config:
                    cfgvalue = self._config[param]
                    if cfgvalue != value:
                        self.printwarning('value of %s from cache (%r) differs '
                                          'from configured value (%r), using '
                                          'the latter' % (param, value, cfgvalue))
                        value = cfgvalue
                        self._cache.put(self, param, value)
                self._params[param] = value
            else:
                self._initParam(param, paraminfo)
                notfromcache.append(param)
            if paraminfo.category is not None:
                self._infoparams.append((paraminfo.category, param,
                                         paraminfo.unit))

        notfromcache = []
        later = []

        for param, paraminfo in self.parameters.iteritems():
            if paraminfo.preinit:
                _init_param(param, paraminfo)
            else:
                later.append((param, paraminfo))

        if hasattr(self, 'doPreinit'):
            self.doPreinit()

        for param, paraminfo in later:
            _init_param(param, paraminfo)

        # warn about parameters that weren't present in cache
        if self._cache and notfromcache:
            self.printwarning('these parameters were not present in cache: ' +
                              ', '.join(notfromcache))

        self._infoparams.sort()

        # call custom initialization
        if hasattr(self, 'doInit'):
            self.doInit()

        # record parameter changes from now on
        self._changedparams.clear()

    def _getCache(self):
        return session.system.cache

    def _initParam(self, param, paraminfo=None):
        """Get an initial value for the parameter, called when the cache
        doesn't contain such a value.
        """
        paraminfo = paraminfo or self.parameters[param]
        methodname = 'doRead' + param.title()
        if hasattr(self, methodname):
            value = getattr(self, methodname)()
        elif param in self._params:
            # happens when called from a param getter, not from init()
            value = self._params[param]
        else:
            value = self._config.get(param, paraminfo.default)
        if self._cache:
            self._cache.put(self, param, value)
        self._params[param] = value

    def _setROParam(self, param, value):
        """Set an otherwise read-only parameter."""
        self._params[param] = value
        if self._cache:
            self._cache.put(self, param, value)

    def _setMode(self, mode):
        """Set a new execution mode."""
        self._mode = mode
        if mode == 'simulation':
            # switching to simulation mode: remove cache entirely
            # and rely on saved _params and values
            self._cache = None

    def info(self):
        """Return device information as an iterable of tuples (name, value)."""
        if hasattr(self, 'doInfo'):
            for item in self.doInfo():
                yield item
        selfunit = getattr(self, 'unit', '')
        for category, name, unit in self._infoparams:
            parvalue = getattr(self, name)
            parunit = (unit or '').replace('main', selfunit)
            yield (category, name, '%s %s' % (parvalue, parunit))

    def shutdown(self):
        """Shut down the object; called from Session.destroyDevice()."""
        if self._mode == 'simulation':
            # do not execute shutdown actions when simulating
            return
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

    def _cachelock_acquire(self, timeout=3):
        if not self._cache:
            return
        start = currenttime()
        while True:
            try:
                self._cache.lock(self.name)
            except CacheLockError:
                if currenttime() > start + timeout:
                    raise CommunicationError(self, 'device locked in cache')
                sleep(0.3)
            else:
                break

    def _cachelock_release(self):
        if not self._cache:
            return
        try:
            self._cache.unlock(self.name)
        except CacheLockError:
            raise CommunicationError(self, 'device locked by other instance')


class Readable(Device):
    """
    Base class for all readable devices.

    Subclasses *need* to implement:

    * doRead()
    * doStatus()

    Subclasses *can* implement:

    * doReset()
    * doPoll()
    """

    parameters = {
        'fmtstr':       Param('Format string for the device value', type=str,
                              default='%s', settable=True),
        'unit':         Param('Unit of the device main value', type=str,
                              mandatory=True, settable=True),
        'maxage':       Param('Maximum age of cached value and status',
                              unit='s', default=5),
        'pollinterval': Param('Polling interval for value and status',
                              unit='s', default=2),
    }

    def init(self):
        Device.init(self)
        # value in simulation mode
        self._sim_value = None

    def _setMode(self, mode):
        if mode == 'simulation':
            # save the last known value
            try:
                self._sim_value = self.read()
            except Exception, err:
                self.printwarning(exc=err)
        Device._setMode(self, mode)

    def __call__(self, value=None):
        """Allow dev() as shortcut for read."""
        if value is not None:
            # give a nicer error message than "TypeError: takes 1 argument"
            raise UsageError(self, 'not a moveable device')
        return self.read()

    def _get_from_cache(self, name, func):
        """Get *name* from the cache, or call *func* if outdated/not present."""
        if not self._cache:
            return func()
        val = self._cache.get(self, name)
        if val is None:
            val = func()
            self._cache.put(self, name, val, currenttime(), self.maxage)
        return val

    def read(self):
        """Read the main value of the device and save it in the cache."""
        if self._mode == 'simulation':
            return self._sim_value
        return self._get_from_cache('value', self.doRead)

    def status(self):
        """Return the status of the device as one of the integer constants
        defined in the nicos.status module.
        """
        if self._mode == 'simulation':
            return status.OK
        if hasattr(self, 'doStatus'):
            value = self._get_from_cache('status', self.doStatus)
            if value[0] not in status.statuses:
                raise ProgrammingError(self, 'status constant %r is unknown' %
                                       value[0])
            return value
        return (status.UNKNOWN, 'doStatus not implemented')

    def poll(self):
        """Get status and value directly from the device and put both values
        into the cache.
        """
        stval = None
        if hasattr(self, 'doStatus'):
            stval = self.doStatus()
            self._cache.put(self, 'status', stval, currenttime(), self.maxage)
        rdval = self.doRead()
        self._cache.put(self, 'value', rdval, currenttime(), self.maxage)
        if hasattr(self, 'doPoll'):
            self.doPoll()
        return stval, rdval

    def _pollParam(self, name):
        self._cache.put(self, name, getattr(self, 'doRead' + name.title())())

    def reset(self):
        """Reset the device hardware.  Return status afterwards."""
        if self._mode == 'slave':
            raise ModeError('reset not possible in slave mode')
        elif self._mode == 'simulation':
            return
        if hasattr(self, 'doReset'):
            self.doReset()
        return self.status()

    def format(self, value):
        """Format a value from self.read() into a human-readable string."""
        return self.fmtstr % value

    def history(self, name='value', fromtime=None, totime=None):
        """Return a history of the parameter *name*."""
        if not self._cache:
            raise ConfigurationError('no cache is configured for this setup')
        else:
            if fromtime is None:
                fromtime = 0
            if totime is None:
                totime = currenttime()
            return self._cache.history(self, name, fromtime, totime)

    def info(self):
        """Automatically add device main value and status (if not OK)."""
        try:
            val = self.read()
            yield ('general', 'value', self.format(val) + ' ' + self.unit)
        except Exception, err:
            self.printwarning('error reading device for info()', exc=err)
            yield ('general', 'value', 'Error: %s' % err)
        try:
            st = self.status()
        except Exception, err:
            self.printwarning('error getting status for info()', exc=err)
            yield ('status', 'status', 'Error: %s' % err)
        else:
            if st[0] not in (status.OK, status.UNKNOWN):
                yield ('status', 'status', '%s: %s' % st)
        for item in Device.info(self):
            yield item


class Startable(Readable):
    """
    Common base class for Moveable and Measurable.

    This is used for typechecking, e.g. when any device with a stop()
    method is required.

    Subclasses *need* to implement:

    * doStart(value)

    Subclasses *can* implement:

    * doStop()
    * doWait()
    * doIsAllowed()
    * doFix()
    * doRelease()
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
        if self._mode == 'slave':
            raise ModeError(self, 'start not possible in slave mode')
        if self.__isFixed:
            raise FixedError(self, 'use release() first')
        ok, why = self.isAllowed(pos)
        if not ok:
            raise LimitError(self, 'moving to %r is not allowed: %s' %
                             (pos, why))
        if self._mode == 'simulation':
            self._sim_value = pos
            return
        if self._cache:
            self._cache.invalidate(self, 'value')
        self.doStart(pos)

    def stop(self):
        """Stop main action of the device."""
        if self._mode == 'slave':
            raise ModeError(self, 'stop not possible in slave mode')
        elif self._mode == 'simulation':
            return
        if self.__isFixed:
            raise FixedError(self, 'use release() first')
        if hasattr(self, 'doStop'):
            self.doStop()

    def wait(self):
        """Wait until main action of device is completed.
        Return current value after waiting.
        """
        if self._mode == 'simulation':
            return self._sim_value
        lastval = None
        if hasattr(self, 'doWait'):
            lastval = self.doWait()
        # update device value in cache and return it
        if lastval is not None:
            # if doWait() returns something, assume it's the latest value
            val = lastval
        else:
            # else, assume the device did move and the cache needs to be
            # updated in most cases
            val = self.doRead()
        if self._cache and self._mode != 'slave':
            self._cache.put(self, 'value', val, currenttime(), self.maxage)
        return val

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
    Base class for moveable devices.
    """

    move = Startable.start


class HasLimits(object):
    """
    Mixin for "simple" continuously moveable devices that have limits.
    """

    parameters = {
        'usermin': Param('User defined minimum of device value', unit='main',
                         settable=True),
        'usermax': Param('User defined maximum of device value', unit='main',
                         settable=True),
        'absmin':  Param('Absolute minimum of device value', unit='main',
                         mandatory=True),
        'absmax':  Param('Absolute maximum of device value', unit='main',
                         mandatory=True),
    }

    def init(self):
        Moveable.init(self)
        if self.absmin > self.absmax:
            raise ConfigurationError(self, 'absolute minimum (%s) above the '
                                     'absolute maximum (%s)' %
                                     (self.absmin, self.absmax))

    def _setMode(self, mode):
        Moveable._setMode(self, mode)
        if mode == 'master':
            self.__checkUserLimits(self.usermin, self.usermax, setthem=True)

    move = Startable.start

    def __checkUserLimits(self, usermin, usermax, setthem=False):
        absmin = self.absmin
        absmax = self.absmax
        if not usermin and not usermax and setthem:
            # if both not set (0) then use absolute min. and max.
            self.usermin = absmin
            self.usermax = absmax
            return
        if usermin > usermax:
            raise ConfigurationError(self, 'user minimum (%s) above the user '
                                     'maximum (%s)' % (usermin, usermax))
        if usermin < absmin:
            raise ConfigurationError(self, 'user minimum (%s) below the '
                                     'absolute minimum (%s)' % (usermin, absmin))
        if usermin > absmax:
            raise ConfigurationError(self, 'user minimum (%s) above the '
                                     'absolute maximum (%s)' % (usermin, absmax))
        if usermax > absmax:
            raise ConfigurationError(self, 'user maximum (%s) above the '
                                     'absolute maximum (%s)' % (usermax, absmax))
        if usermax < absmin:
            raise ConfigurationError(self, 'user maximum (%s) below the '
                                     'absolute minimum (%s)' % (usermax, absmin))

    def isAllowed(self, target):
        if not self.usermin <= target <= self.usermax:
            return False, 'limits are [%s, %s]' % (self.usermin, self.usermax)
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(target)
        return True, ''

    def doWriteUsermin(self, value):
        """Set the user minimum value to value after checking the value against
        absolute limits and user maximum.
        """
        self.__checkUserLimits(value, self.usermax)

    def doWriteUsermax(self, value):
        """Set the user maximum value to value after checking the value against
        absolute limits and user minimum.
        """
        self.__checkUserLimits(self.usermin, value)


class HasOffset(object):
    """
    Mixin class for Readable or Moveable devices that want to provide an
    'offset' parameter and that can be adjusted via adjust().

    This is *not* directly a feature of Moveable, because providing this
    transparently this would mean that doRead() returns the un-adjusted value
    while read() returns the adjusted value.  It would also mean that the
    un-adjusted value is stored in the cache, which is wrong for monitoring
    purposes.

    Instead, each class that provides an offset must inherit this mixin, and
    subtract/add self.offset in doRead()/doStart().
    """

    parameters = {
        'offset':  Param('Offset of device zero to hardware zero', unit='main',
                         settable=True, category='offsets'),
    }

    def doWriteOffset(self, value):
        """Adapt the limits to the new offset."""
        if isinstance(self, Moveable):
            # this applies only to Moveables
            diff = value - self.offset
            # Avoid the use of the setPar method for the absolute limits
            if diff < 0:
                self._setROParam('absmax', self.absmax - diff)
                self._setROParam('absmin', self.absmin - diff)
            else:
                self._setROParam('absmin', self.absmin - diff)
                self._setROParam('absmax', self.absmax - diff)

            if diff < 0:
                self.usermin = self.usermin - diff
                self.usermax = self.usermax - diff
            else:
                self.usermax = self.usermax - diff
                self.usermin = self.usermin - diff
        # Since offset changes directly change the device value, refresh
        # the cache instantly here
        if self._cache:
            self._cache.put(self, 'value', self.doRead() - diff,
                            currenttime(), self.maxage)


class Measurable(Startable):
    """
    Base class for devices used for data acquisition.

    Subclasses *need* to implement:

    * doRead()
    * doStart(**preset)
    * doStop()
    * doIsCompleted()

    Subclasses *can* implement:

    * doPause()
    * doResume()
    """

    parameter_overrides = {
        'unit':  Override(description='(not used)', mandatory=False),
    }

    def start(self, **preset):
        """Start measurement."""
        if self._mode == 'slave':
            raise ModeError(self, 'start not possible in slave mode')
        elif self._mode == 'simulation':
            return
        self.doStart(**preset)

    def pause(self):
        """Pause the measurement, if possible.  Return True if paused
        successfully.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'pause not possible in slave mode')
        elif self._mode == 'simulation':
            return True
        if hasattr(self, 'doPause'):
            return self.doPause()
        return False

    def resume(self):
        """Resume paused measurement."""
        if self._mode == 'slave':
            raise ModeError(self, 'resume not possible in slave mode')
        elif self._mode == 'simulation':
            return True
        if hasattr(self, 'doResume'):
            return self.doResume()
        return False

    def stop(self):
        """Stop measurement now."""
        if self._mode == 'slave':
            raise ModeError(self, 'stop not possible in slave mode')
        elif self._mode == 'simulation':
            return
        self.doStop()

    def isCompleted(self):
        """Return true if measurement is complete."""
        if self._mode == 'simulation':
            return True
        return self.doIsCompleted()

    def wait(self):
        """Wait for completion of measurement."""
        if self._mode == 'simulation':
            return
        while not self.isCompleted():
            sleep(0.1)

    def read(self):
        """Return the result of the last measurement."""
        if self._mode == 'simulation':
            # XXX simulate a return value
            return []
        # always get fresh result from cache
        if self._cache:
            self._cache.invalidate(self, 'value')
        result = self._get_from_cache('value', self.doRead)
        if not isinstance(result, list):
            return [result]
        return result

    def valueInfo(self):
        """Return two lists: list of value names and list of value units."""
        return [], []

    def info(self):
        """Automatically add device status (if not OK).  Does not add the
        device value since that is typically not useful for Measurables.
        """
        try:
            st = self.status()
        except Exception, err:
            self.printwarning('error getting status for info()', exc=err)
            yield ('status', 'status', 'Error: %s' % err)
        else:
            if st[0] not in (status.OK, status.UNKNOWN):
                yield ('status', 'status', '%s: %s' % st)
        for item in Device.info(self):
            yield item
