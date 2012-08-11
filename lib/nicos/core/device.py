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

"""Base device classes for usage in NICOS."""

__version__ = "$Revision$"

import types
import inspect
from time import time as currenttime, sleep

from nicos import session
from nicos.core import status
from nicos.core.params import Param, Override, Value, tupleof, floatrange, \
     anytype, none_or
from nicos.core.errors import NicosError, ConfigurationError, \
     ProgrammingError, UsageError, LimitError, ModeError, \
     CommunicationError, CacheLockError, InvalidValueError, AccessError, \
     CacheError
from nicos.utils import loggers, getVersions, parseDateString


def usermethod(func):
    """Decorator that marks a method as a user-visible method.

    The method will be shown to the user in the help for a device.
    """
    func.is_usermethod = True
    return func


def requires(**access):
    """Decorator to implement user access control.

    The access is checked based on the keywords given.  Currently, the
    keywords with meaning are:

    * ``'level'``: gives the minimum required user access level and can
      have the values ``GUEST``, ``USER`` or ``ADMIN`` as defined in the
      :mod:`nicos.core.utils` module.
    * ``'mode'``: gives the required exection mode ("master", "slave",
      "maintenance", "simulation").
    * ``'passcode'``: only usable in the interactive console: gives a
      passcode that the user has to type back.

    The wrapper function calls `.Session.checkAccess` to verify the
    requirements.  If the check fails, `.AccessError` is raised.
    """
    def decorator(func):
        def new_func(*args, **kwds):
            try:
                session.checkAccess(access)
            except AccessError, err:
                if args and isinstance(args[0], Device):
                    raise AccessError(args[0], 'cannot execute %s: %s' %
                                      (func.__name__, err))
                raise AccessError('cannot execute %s: %s' %
                                  (func.__name__, err))
            return func(*args, **kwds)
        new_func.__name__ = func.__name__
        return new_func
    return decorator


class DeviceMeta(type):
    """
    A metaclass that automatically adds properties for the class' parameters,
    and determines a list of user methods ("commands").

    It also merges attached_devices, parameters and parameter_overrides defined
    in the class with those defined in all base classes.
    """

    def __new__(mcs, name, bases, attrs): #@NoSelf
        if 'parameters' in attrs:
            for pinfo in attrs['parameters'].itervalues():
                pinfo.classname = attrs['__module__'] + '.' + name
        for base in bases:
            if hasattr(base, 'parameters'):
                for pinfo in base.parameters.itervalues():
                    if pinfo.classname is None:
                        pinfo.classname = base.__module__ + '.' + base.__name__
        newtype = type.__new__(mcs, name, bases, attrs)
        for entry in newtype.__mergedattrs__:
            newentry = {}
            for base in reversed(bases):
                if hasattr(base, entry):
                    newentry.update(getattr(base, entry))
            newentry.update(attrs.get(entry, {}))
            setattr(newtype, entry, newentry)
        for param, info in newtype.parameters.iteritems():
            # parameter names are always lowercased
            param = param.lower()
            if not isinstance(info, Param):
                raise ProgrammingError('%r device %r parameter info should be '
                                       'a Param object' % (name, param))

            # process overrides
            override = newtype.parameter_overrides.get(param)
            if override:
                info = newtype.parameters[param] = override.apply(info)

            # create the getter method
            if not info.volatile:
                def getter(self, param=param):
                    if param not in self._params:
                        self._initParam(param)
                    if self._cache:
                        value = self._cache.get(self, param, Ellipsis)
                        if value is not Ellipsis:
                            self._params[param] = value
                            return value
                    return self._params[param]
            else:
                rmethod = getattr(newtype, 'doRead' + param.title(), None)
                if rmethod is None:
                    raise ProgrammingError('%r device %r parameter is marked '
                                           'as "volatile=True", but has no '
                                           'doRead%s method' %
                                           (name, param, param.title()))
                def getter(self, param=param, rmethod=rmethod):
                    if self._mode == 'simulation':
                        return self._initParam(param)
                    value = rmethod(self)
                    if self._cache:
                        self._cache.put(self, param, value)
                    self._params[param] = value
                    return value

            # create the setter method
            if not info.settable:
                def setter(self, value, param=param):
                    raise ConfigurationError(
                        self, 'the %s parameter can only be changed in the '
                        'setup file' % param)
            else:
                wmethod = getattr(newtype, 'doWrite' + param.title(), None)
                umethod = getattr(newtype, 'doUpdate' + param.title(), None)
                def setter(self, value, param=param, wmethod=wmethod,
                           umethod=umethod):
                    pconv = self.parameters[param].type
                    try:
                        value = pconv(value)
                    except (ValueError, TypeError), err:
                        raise ConfigurationError(
                            self, '%r is an invalid value for parameter '
                            '%s: %s' % (value, param, err))
                    if self._mode == 'slave':
                        raise ModeError('setting parameter %s not possible in '
                                        'slave mode' % param)
                    elif self._mode == 'simulation':
                        if umethod:
                            umethod(self, value)
                        self._params[param] = value
                        return
                    if wmethod:
                        # allow doWrite to override the value
                        rv = wmethod(self, value)
                        if rv is not None:
                            value = rv
                    if umethod:
                        umethod(self, value)
                    self._params[param] = value
                    if self._cache:
                        self._cache.put(self, param, value)

            # create a property and attach to the new device class
            setattr(newtype, param,
                    property(getter, setter, doc=info.formatDoc()))
        del newtype.parameter_overrides
        if 'parameter_overrides' in attrs:
            del attrs['parameter_overrides']
        if 'valuetype' in attrs:
            newtype.valuetype = staticmethod(attrs['valuetype'])

        newtype.commands = {}
        for methname in attrs:
            if methname.startswith(('_', 'do')):
                continue
            method = getattr(newtype, methname)
            if not isinstance(method, types.MethodType):
                continue
            if not hasattr(method, 'is_usermethod'):
                continue
            argspec = inspect.getargspec(method)
            if argspec[0] and argspec[0][0] == 'self':
                del argspec[0][0]  # get rid of "self"
            args = inspect.formatargspec(*argspec)
            if method.__doc__:
                docline = method.__doc__.strip().splitlines()[0]
            else:
                docline = ''
            newtype.commands[methname] = (args, docline)

        return newtype

    def __instancecheck__(cls, inst): # pylint: disable=C0203
        from nicos.generic import DeviceAlias
        if inst.__class__ == DeviceAlias and inst._initialized:
            return isinstance(inst._obj, cls)
        # does not work with Python 2.6!
        #return type.__instancecheck__(cls, inst)
        return issubclass(inst.__class__, cls)


class Device(object):
    """
    An object that has a list of parameters that are read from the configuration
    and have default values.

    Subclasses *can* implement:

    * doPreinit()
    * doInit()
    * doShutdown()
    * doVersion()
    """

    __metaclass__ = DeviceMeta
    __mergedattrs__ = ['parameters', 'parameter_overrides', 'attached_devices']

    # A dictionary mapping device names to classes (or lists of classes) that
    # describe this device's attached (subordinate) devices.
    attached_devices = {}

    # A dictionary mapping parameter names to parameter descriptions, given as
    # Param objects.
    parameters = {
        'description': Param('A description of the device', type=str,
                             settable=True),
        'lowlevel':    Param('Whether the device is not interesting to users',
                             type=bool, default=False, userparam=False),
        'loglevel':    Param('The logging level of the device', type=str,
                             default='info', settable=True, preinit=True),
    }

    # A dictionary mapping parameter names to Override objects that override
    # specific properties of parameters found in base classes.
    parameter_overrides = {}

    # Set this to True on devices that are only created for a time, and whose
    # name can be reused.
    temporary = False

    def __init__(self, name, **config):
        # register self in device registry
        if not self.temporary:
            if name in session.devices:
                raise ProgrammingError('device with name %s already exists' % name)
            session.devices[name] = self

        self.__dict__['name'] = name
        # _config: device configuration (all parameter names lower-case)
        self._config = dict((name.lower(), value)
                            for (name, value) in config.items())
        # _params: parameter values from config
        self._params = {}
        # _infoparams: cached list of parameters to get on info()
        self._infoparams = []
        # _adevs: "attached" device instances
        self._adevs = {}
        # superdevs: reverse adevs for dependency tracking
        self._sdevs = set()
        # execution mode
        self._mode = session.mode

        # initialize a logger for the device
        self.__dict__['log'] = session.getLogger(name)

        try:
            # initialize device
            self.init()
        except:  # here, really *all* exceptions are intended
            # if initialization fails, remove from device registry
            session.devices.pop(name, None)
            # and remove from adevs' sdevs
            for adev in self._adevs.values():
                if isinstance(adev, list):
                    for real_adev in adev:
                        real_adev._sdevs.discard(self.name)
                elif adev is not None:
                    adev._sdevs.discard(self.name)
            raise

    def __setattr__(self, name, value):
        # disallow modification of public attributes that are not parameters
        if name not in dir(self.__class__) and name[0] != '_' and \
               not name.startswith('print'):
            raise UsageError(self, 'device has no parameter %s, use '
                             'ListParams(%s) to show all' % (name, self))
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

    def __reduce__(self):
        # Used for pickling the device e.g. when sending between daemon and GUI
        return (str, (self.name,))

    def getPar(self, name):
        """Get a parameter of the device."""
        if name.lower() not in self.parameters:
            raise UsageError(self, 'device has no parameter %s, use '
                             'ListParams(%s) to show all' % (name, self))
        return getattr(self, name.lower())

    def setPar(self, name, value):
        """Set a parameter of the device to a new value."""
        if name.lower() not in self.parameters:
            raise UsageError(self, 'device has no parameter %s, use '
                             'ListParams(%s) to show all' % (name, self))
        setattr(self, name.lower(), value)

    def doUpdateLoglevel(self, value):
        if value not in loggers.loglevels:
            raise InvalidValueError(self, 'loglevel must be one of %s' %
                ', '.join(map(repr, loggers.loglevels.keys())))
        self.log.setLevel(loggers.loglevels[value])

    def init(self):
        """Initialize the object; this is called by the NICOS system when the
        device instance has been created.

        This method first initializes all attached devices (creating them if
        necessary), then initializes parameters.

        .. XXX expand parameter init procedure

        .. method:: doPreinit(mode)

           This method, if present, is called before parameters are initialized
           (except for parameters that have the ``preinit`` property set to
           true).

           This allows to initialize a hardware connection if it is necessary
           for the various ``doRead...()`` methods of other parameters that read
           the current parameter value from the hardware.

        .. method:: doInit(mode)

           This method, if present, is called after all parameters have been
           initialized.  It is the correct place to set up additional
           attributes, or to perform initial (read-only!) communication with the
           hardware.

        .. note:: ``doPreinit()`` and ``doInit()`` are called regardless of the
           current execution mode.  This means that if one of these methods does
           hardware access, it must be done only if ``mode != 'simulation'``.
        """
        # validate and create attached devices
        for aname, entry in sorted(self.attached_devices.iteritems()):
            if not isinstance(entry, tuple) or len(entry) != 2:
                raise ProgrammingError(self, 'attached device entry for %r is '
                                       'invalid; the value should be of the '
                                       'form (cls, docstring)' % aname)
            cls = entry[0]
            if aname not in self._config:
                raise ConfigurationError(
                    self, 'device misses device %r in configuration' % aname)
            value = self._config.pop(aname)
            if value is None:
                if isinstance(cls, list):
                    self._adevs[aname] = []
                else:
                    self._adevs[aname] = None
                continue
            if isinstance(cls, list):
                cls = cls[0]
                if not isinstance(value, list):
                    raise ConfigurationError(
                        self, '%r should be a list of device names, not %r'
                        % (aname, value))
                devlist = []
                self._adevs[aname] = devlist
                for i, devname in enumerate(value):
                    dev = session.getDevice(devname, source=self)
                    if not isinstance(dev, cls):
                        raise ConfigurationError(
                            self, 'device %r item %d has wrong type (should be '
                            '%s' % (aname, i, cls.__name__))
                    devlist.append(dev)
                    dev._sdevs.add(self.name)
            else:
                dev = session.getDevice(value, source=self)
                if not isinstance(dev, cls):
                    raise ConfigurationError(
                        self, 'device %r has wrong type (should be %s)' %
                        (aname, cls.__name__))
                self._adevs[aname] = dev
                dev._sdevs.add(self.name)

        self._cache = self._getCache()
        lastconfig = None
        if self._cache:
            lastconfig = self._cache.get('_lastconfig_', self.name, None)

        def _init_param(param, paraminfo):
            param = param.lower()
            # mandatory parameters must be in config, regardless of cache
            if paraminfo.mandatory and param not in self._config:
                raise ConfigurationError(self, 'missing configuration '
                                         'parameter %r' % param)
            # try to get from cache
            value = Ellipsis  # Ellipsis representing "no value" since None
                              # is a valid value for some parameters
            if self._cache:
                value = self._cache.get(self, param, Ellipsis)
            if value is not Ellipsis:
                if param in self._config:
                    cfgvalue = self._config[param]
                    if cfgvalue != value:
                        prefercache = paraminfo.prefercache
                        if prefercache is None:
                            prefercache = paraminfo.settable
                        if lastconfig and lastconfig.get(param) != cfgvalue:
                            self.log.warning(
                                'value of %s from cache (%r) differs from '
                                'configured value (%r), using configured '
                                'since it was changed in the setup file' %
                                (param, value, cfgvalue))
                            value = cfgvalue
                            self._cache.put(self, param, value)
                        elif prefercache:
                            self.log.warning(
                                'value of %s from cache (%r) differs from '
                                'configured value (%r), using cached' %
                                (param, value, cfgvalue))
                        else:
                            self.log.warning(
                                'value of %s from cache (%r) differs from '
                                'configured value (%r), using configured' %
                                (param, value, cfgvalue))
                            value = cfgvalue
                            self._cache.put(self, param, value)
                umethod = getattr(self, 'doUpdate' + param.title(), None)
                if umethod:
                    umethod(value)
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
            self.doPreinit(self._mode)

        for param, paraminfo in later:
            _init_param(param, paraminfo)

        # warn about parameters that weren't present in cache
        if self._cache and notfromcache:
            self.log.info('these parameters were not present in cache: ' +
                          ', '.join(notfromcache))

        self._infoparams.sort()

        # subscribe to parameter value updates, if a doUpdate method exists
        if self._cache:
            for param in self.parameters:
                umethod = getattr(self, 'doUpdate' + param.title(), None)
                if umethod:
                    def updateparam(key, value, time, umethod=umethod):
                        umethod(value)
                    self._cache.addCallback(self, param, updateparam)

        if self._cache:
            self._cache.put('_lastconfig_', self.name, self._config)

        # call custom initialization
        if hasattr(self, 'doInit'):
            self.doInit(self._mode)

    def _getCache(self):
        """Indirection needed by the Cache client itself."""
        return session.cache

    def _initParam(self, param, paraminfo=None):
        """Get an initial value for the parameter, called when the cache
        doesn't contain such a value.

        If present, a doReadParam method is called.  Otherwise, the value comes
        from either the setup file or the device-specific default value.
        """
        paraminfo = paraminfo or self.parameters[param]
        umethod = getattr(self, 'doUpdate' + param.title(), None)
        if self._mode == 'simulation':
            # in simulation mode, we only have the config file and the defaults:
            # cache isn't present, and we can't touch the hardware to ask
            if param not in self._params:
                self._params[param] = self._config.get(param, paraminfo.default)
            # do call update methods though, they should be harmless
            if umethod:
                umethod(self._params[param])
            return self._params[param]
        rmethod = getattr(self, 'doRead' + param.title(), None)
        done = False
        if rmethod:
            try:
                value = rmethod()
            except NicosError:
                self.log.warning('could not read initial value for parameter '
                                 '%s from device' % param)
            else:
                done = True
        if not done and param in self._params:
            # happens when called from a param getter, not from init()
            value = self._params[param]
        elif not done:
            value = self._config.get(param, paraminfo.default)
            try:
                value = paraminfo.type(value)
            except (ValueError, TypeError), err:
                raise ConfigurationError(
                    self, '%r is an invalid value for parameter '
                    '%s: %s' % (value, param, err))
        if self._cache:
            self._cache.put(self, param, value)
        if umethod:
            umethod(value)
        self._params[param] = value
        return value

    def _setROParam(self, param, value):
        """Set an otherwise read-only parameter.

        This is useful for parameters that change at runtime, but indirectly,
        such as "last filenumber".
        """
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
        """Return "device information" as an iterable of tuples ``(category,
        name, value)``.

        This "device information" is put into data files and should therefore
        include any parameters that will be essential to record the current
        status of the instrument.

        The default implementation already collects all parameters whose
        ``category`` property is set.

        .. method:: doInfo()

           This method can add more device information by returning it as a
           sequence of tuples.
        """
        if hasattr(self, 'doInfo'):
            for item in self.doInfo():
                yield item
        selfunit = getattr(self, 'unit', '')
        for category, name, unit in self._infoparams:
            try:
                parvalue = getattr(self, name)
            except Exception, err:
                self.log.warning('error getting %s parameter for info()' %
                                  name, exc=err)
                continue
            parunit = (unit or '').replace('main', selfunit)
            yield (category, name, '%s %s' % (parvalue, parunit))

    def shutdown(self):
        """Shut down the device.  This method is called by the NICOS system when
        the device is destroyed, manually or because the current setup is
        unloaded.

        .. method:: doShutdown()

           This method is called, if present, but not in simulation mode.  It
           should perform cleanup, for example closing connections to hardware.
        """
        if self._mode == 'simulation':
            # do not execute shutdown actions when simulating
            return
        if hasattr(self, 'doShutdown'):
            self.doShutdown()

    @usermethod
    def version(self):
        """Return a list of versions for this device.

        These are tuples (component, version) where a "component" can be the
        name of a Python module, or an external dependency (like a TACO server).

        The base implementation already collects VCS revision information
        available from all Python modules involved in the class inheritance
        chain of the device class.

        .. method:: doVersion()

           This method is called if present, and should return a list of
           (component, version) tuples that are added to the version info.
        """
        versions = getVersions(self)
        if hasattr(self, 'doVersion'):
            versions.extend(self.doVersion())
        return versions

    def _cachelock_acquire(self, timeout=3):
        """Acquire an exclusive lock for using this device from the cache.  This
        can be used if read access to the device needs to be locked (write
        access is locked anyway, since only one NICOS session can be the master
        session at a time).
        """
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
        """Release the exclusive cache lock for this device.

        Always use like this::

           self._cachelock_acquire()
           try:
               ...  # do locked operations
           finally:
               self._cachelock_release()
        """
        if not self._cache:
            return
        try:
            self._cache.unlock(self.name)
        except CacheLockError:
            raise CommunicationError(self, 'device locked by other instance')


class AutoDevice(object):
    """Abstract mixin for devices that are created automatically as dependent
    devices of other devices.
    """


class Readable(Device):
    """
    Base class for all readable devices.

    Subclasses *need* to implement:

    * doRead()
    * doStatus()

    Subclasses *can* implement:

    * doReset()
    * doPoll()
    * valueInfo()
    """

    # Set this to False on devices that directly access hardware, and therefore
    # should have their actions simulated.
    hardware_access = True

    parameters = {
        'fmtstr':       Param('Format string for the device value', type=str,
                              default='%.3f', settable=True),
        'unit':         Param('Unit of the device main value', type=str,
                              mandatory=True, settable=True),
        'maxage':       Param('Maximum age of cached value and status (zero to '
                              'never use cached values, or None to cache them '
                              'indefinitely)', unit='s', settable=True,
                              type=none_or(floatrange(0, 24*3600)), default=6),
        'pollinterval': Param('Polling interval for value and status (or None '
                              'to disable polling)', unit='s', settable=True,
                              type=none_or(floatrange(0.5, 24*3600)), default=5),
    }

    def init(self):
        self._sim_active = False
        Device.init(self)
        # value in simulation mode
        self._sim_active = self._mode == 'simulation' and self.hardware_access
        self._sim_old_value = None
        self._sim_value = 0   # XXX how to configure a useful default?
        self._sim_min = None
        self._sim_max = None
        self._sim_started = None
        self._sim_preset = {}

    def _sim_setValue(self, pos):
        self._sim_old_value = self._sim_value
        self._sim_value = pos
        if self._sim_min is None:
            self._sim_min = pos
        self._sim_min = min(pos, self._sim_min)
        if self._sim_max is None:
            self._sim_max = pos
        self._sim_max = max(pos, self._sim_max)

    def _setMode(self, mode):
        sim_active = mode == 'simulation' and self.hardware_access
        if sim_active:
            # save the last known value
            try:
                self._sim_value = self.read()  # cached value is ok here
                self.log.debug('last value before simulation mode is %r' %
                                (self._sim_value,))
            except Exception, err:
                self.log.warning('error reading last value', exc=err)
        self._sim_active = sim_active
        Device._setMode(self, mode)

    def __call__(self, value=None):
        """Allow dev() as shortcut for read."""
        if value is not None:
            # give a nicer error message than "TypeError: takes 1 argument"
            raise UsageError(self, 'not a moveable device')
        return self.read()

    def _get_from_cache(self, name, func, maxage=None):
        """Get *name* from the cache, or call *func* if outdated/not present.

        If the *maxage* parameter is set, do not allow the value to be older
        than that amount of seconds.
        """
        if not self._cache:
            return func()
        val = None
        if 1: # self.hardware_access:  XXX decide if this should be enabled
            if maxage != 0:
                val = self._cache.get(self, name,
                    mintime=currenttime()-maxage if maxage is not None else 0)
        if val is None:
            val = func(self.maxage if maxage is None else maxage)
            self._cache.put(self, name, val, currenttime(), self.maxage)
        return val

    def valueInfo(self):
        """Describe the values read by this device.

        Return a tuple of :class:`~nicos.core.params.Value` instances describing
        the values that :meth:`read` returns.

        This must be overridden by every Readable that returns more than one
        value in a list.  For example, a slit that returns a width and height
        would define ::

            def valueInfo(self):
                return (Value(self.name + '.width', unit=self.unit),
                        Value(self.name + '.height', unit=self.unit))

        By default, this returns a Value that indicates one return value with
        the proper unit and format string of the device.
        """
        return Value(self.name, unit=self.unit, fmtstr=self.fmtstr),

    @usermethod
    def read(self, maxage=None):
        """Read the (possibly cached) main value of the device.

        .. method:: doRead(maxage=0)

           This method must be implemented to read the actual device value from
           the device.  It is only called if the last cached value is out of
           date, or no cache is available.

           The *maxage* parameter should be given to read() calls of subdevices.
        """
        if self._sim_active:
            return self._sim_value
        return self._get_from_cache('value', self.doRead, maxage)

    @usermethod
    def status(self, maxage=None):
        """Return the (possibly cached) status of the device.

        The status is a tuple of one of the integer constants defined in the
        :mod:`nicos.core.status` module, and textual extended info.

        .. method:: doStatus(maxage=0)

           This method can be implemented to get actual device status from the
           device.  It is only called if the last cached value is out of
           date, or no cache is available.

           If no ``doStatus()`` is implemented, ``status()`` returns
           ``status.UNKNOWN``.

           The *maxage* parameter should be given to status() calls of
           subdevices.
        """
        if self._sim_active:
            return (status.OK, 'simulated ok')
        if hasattr(self, 'doStatus'):
            try:
                value = self._get_from_cache('status', self.doStatus, maxage)
            except NicosError, err:
                value = (status.ERROR, str(err))
            if value[0] not in status.statuses:
                raise ProgrammingError(self, 'status constant %r is unknown' %
                                       value[0])
            return value
        return (status.UNKNOWN, 'doStatus not implemented')

    def poll(self, n=0, maxage=0):
        """Get status and value directly from the device and put both values
        into the cache.  For continuous polling, *n* should increase by one with
        every call to *poll*.

        .. method:: doPoll(n)

           If present, this method is called to perform additional polling,
           e.g. on parameters that can be changed from outside the NICOS system.
           The *n* parameter can be used to perform the polling less frequently
           than the polling of value and status.

           If doPoll returns a (status, value) tuple, they are used instead of
           calling doStatus and doRead again.

        .. automethod:: _pollParam
        """
        if self._sim_active or self._cache is None:
            return (self.status(), self.read())
        ret = None
        if hasattr(self, 'doPoll'):
            try:
                ret = self.doPoll(n)
            except Exception:
                self.log.debug('error in doPoll', exc=1)
        if ret is not None:
            self._cache.put(self, 'status', ret[0], currenttime(), self.maxage)
            self._cache.put(self, 'value', ret[1], currenttime(), self.maxage)
            return ret[0], ret[1]
        stval = None
        if hasattr(self, 'doStatus'):
            stval = self.doStatus(maxage)
            self._cache.put(self, 'status', stval, currenttime(), self.maxage)
        rdval = self.doRead(maxage)
        self._cache.put(self, 'value', rdval, currenttime(), self.maxage)
        return stval, rdval

    def _pollParam(self, name, with_ttl=0):
        """Read a parameter value from the hardware and put its value into the
        cache.  This is intendend to be used from :meth:`doPoll` methods, so
        that they don't have to implement parameter polling themselves.  If
        *with_ttl* is > 0, the cached value gets the TTL of the device value,
        determined by :attr:`maxage`, multiplied by *with_ttl*.
        """
        value = getattr(self, 'doRead' + name.title())()
        if with_ttl:
            self._cache.put(self, name, value, currenttime(),
                            (self.maxage or 0) * with_ttl)
        else:
            self._cache.put(self, name, value)

    @usermethod
    def reset(self):
        """Reset the device hardware.  Returns the new status afterwards.

        This operation is forbidden in slave mode, and a no-op for hardware
        devices in simulation mode.

        .. method:: doReset()

           This method is called if implemented.  Otherwise, ``reset()`` is a
           no-op.
        """
        if self._mode == 'slave':
            raise ModeError('reset not possible in slave mode')
        elif self._sim_active:
            return
        if hasattr(self, 'doReset'):
            self.doReset()
        return self.status(0)

    def format(self, value):
        """Format a value from :meth:`read` into a human-readable string.

        The device unit is not included.

        This is done using Python string formatting (the ``%`` operator) with
        the :attr:`fmtstr` parameter value as the format string.
        """
        if isinstance(value, list):
            value = tuple(value)
        try:
            return self.fmtstr % value
        except (TypeError, ValueError):
            return str(value)

    def history(self, name='value', fromtime=None, totime=None):
        """Return a history of the parameter *name* (can also be ``'value'`` or
        ``'status'``).

        *fromtime* and *totime* can be used to limit the time window.  They can
        be:

        * positive numbers: interpreted as UNIX timestamps
        * negative numbers: interpreted as hours back from now
        * strings: in one of the formats 'HH:MM', 'HH:MM:SS',
          'YYYY-MM-DD', 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD HH:MM:SS'

        Default is to query the values of the last hour.
        """
        if not self._cache:
            # no cache is configured for this setup
            return []
        else:
            if fromtime is None:
                fromtime = -1
            if isinstance(fromtime, str):
                fromtime = parseDateString(fromtime)
            elif fromtime < 0:
                fromtime = currenttime() + fromtime * 3600
            if totime is None:
                totime = currenttime()
            elif isinstance(totime, str):
                totime = parseDateString(totime, enddate=True)
            elif totime < 0:
                totime = currenttime() + totime * 3600
            return self._cache.history(self, name, fromtime, totime)

    def info(self):
        """Automatically add device main value and status (if not OK)."""
        try:
            val = self.read()
            yield ('general', 'value', self.format(val) + ' ' + self.unit)
        except Exception, err:
            self.log.warning('error reading device for info()', exc=err)
            yield ('general', 'value', 'Error: %s' % err)
        try:
            st = self.status()
        except Exception, err:
            self.log.warning('error getting status for info()', exc=err)
            yield ('status', 'status', 'Error: %s' % err)
        else:
            if st[0] not in (status.OK, status.UNKNOWN):
                yield ('status', 'status', '%s: %s' % st)
        for item in Device.info(self):
            yield item


class Moveable(Readable):
    """
    Base class for moveable devices.

    Subclasses *need* to implement:

    * doStart(value)

    Subclasses *can* implement:

    * doStop()
    * doWait()
    * doIsAllowed()
    * doTime()
    """

    parameters = {
        'target': Param('Last target position of a start() action',
                        unit='main', type=anytype, default='unknown'),
        'fixed':  Param('None if the device is not fixed, else a string '
                        'describing why', settable=True, userparam=False,
                        type=str),
    }

    # The type of the device value, used for typechecking in doStart().
    @staticmethod
    def valuetype(value):
        """The type of the device value, used for type checking in doStart().

        This should be a static function as the real function is assigned
        externally from functions defined in nicos.core.params, so no class
        instance need to be passed.
        """
        return value
    valuetype = anytype

    def __call__(self, pos=None):
        """Allow dev() and dev(newpos) as shortcuts for read and start."""
        if pos is None:
            return self.read()
        return self.start(pos)

    @usermethod
    def isAllowed(self, pos):
        """Check if the given position can be moved to.

        The return value is a tuple ``(valid, why)``.  The first item is a
        boolean indicating if the position is valid, the second item is a string
        with the reason if it is invalid.

        .. method:: doIsAllowed(pos)

           This method must be implemented to check the validity.  If it does
           not exist, all positions are valid.

           Note: to implement ordinary (min, max) limits, do not use this method
           but inherit your device from :class:`HasLimits`.  This takes care of
           all limit processing.
        """
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(pos)
        return True, ''

    @usermethod
    def start(self, pos):
        """Start movement of the device to a new position.

        This method does not generally wait for completion of the movement,
        although individual devices can implement it that way if it is
        convenient.  In that case, no :meth:`doWait` should be implemented.

        The validity of the given *pos* is checked by calling :meth:`isAllowed`
        before :meth:`doStart` is called.

        This operation is forbidden in slave mode.  In simulation mode, it sets
        an internal variable to the given position for hardware devices instead
        of calling :meth:`doStart`.

        .. method:: doStart(pos)

           This method must be implemented and actually move the device to the
           new position.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'start not possible in slave mode')
        if self.fixed:
            # try to determine if we are already there
            try:
                # this may raise if the position values are not numbers
                if abs(self.read() - pos) <= getattr(self, 'precision', 0):
                    self.log.debug('device fixed; start() allowed since '
                                   'already at desired position %s' % pos)
                    return
            except Exception:
                pass
            self.log.warning('device fixed, not moving: %s' % self.fixed)
            return
        try:
            pos = self.valuetype(pos)
        except (ValueError, TypeError), err:
            raise InvalidValueError(self, '%r is an invalid value for this '
                                    'device: %s' % (pos, err))
        ok, why = self.isAllowed(pos)
        if not ok:
            raise LimitError(self, 'moving to %s is not allowed: %s' %
                             (self.format(pos), why))
        self._setROParam('target', pos)
        if self._sim_active:
            self._sim_setValue(pos)
            self._sim_started = session.clock.time
            return
        if self._cache:
            self._cache.invalidate(self, 'value')
        self.doStart(pos)

    move = start

    @usermethod
    def wait(self):
        """Wait until movement of device is completed.

        Return current device value after waiting.  This is a no-op for hardware
        devices in simulation mode.

        .. method:: doWait()

           If present, this method is called to actually do the waiting.
           Otherwise, the device is assumed to change position instantly.
        """
        if self._sim_active:
            if not hasattr(self, 'doTime'):
                if 'speed' in self.parameters and self.speed != 0 and \
                    self._sim_old_value is not None:
                    time = abs(self._sim_value - self._sim_old_value) / \
                        self.speed
                elif 'ramp' in self.parameters and self.ramp != 0 and \
                    self._sim_old_value is not None:
                    time = abs(self._sim_value - self._sim_old_value) / \
                        (self.ramp / 60.)
                else:
                    time = 0
            else:
                try:
                    time = self.doTime(self._sim_old_value, self._sim_value)
                except Exception:
                    self.log.warning('could not time movement', exc=1)
                    time = 0
            if self._sim_started is not None:
                session.clock.wait(self._sim_started + time)
                self._sim_started = None
            self._sim_old_value = self._sim_value
            return self._sim_value
        lastval = None
        try:
            if hasattr(self, 'doWait'):
                lastval = self.doWait()
        finally:
            # update device value in cache and return it
            if lastval is not None:
                # if doWait() returns something, assume it's the latest value
                val = lastval
            else:
                # else, assume the device did move and the cache needs to be
                # updated in most cases
                val = self.doRead(0)  # not read(0), we already cache value below
            if self._cache and self._mode != 'slave':
                self._cache.put(self, 'value', val, currenttime(), self.maxage)
        return val

    @usermethod
    def maw(self, target):
        """Move to target and wait for completion.

        Equivalent to ``dev.start(target); return dev.wait()``.
        """
        self.start(target)
        return self.wait()

    @usermethod
    def stop(self):
        """Stop any movement of the device.

        This operation is forbidden in slave mode, and a no-op for hardware
        devices in simulation mode.

        .. method:: doStop()

           This is called to actually stop the device.  If not present,
           :meth:`stop` will be a no-op.

        The `stop` method will return the device status after stopping.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'stop not possible in slave mode')
        elif self._sim_active:
            return
        if hasattr(self, 'doStop'):
            self.doStop()
        if self._cache:
            self._cache.invalidate(self, 'value')

    @usermethod
    def fix(self, reason=''):
        """Fix the device: don't allow movement anymore.

        This blocks :meth:`start` or :meth:`stop` when called on the device.
        """
        self.fixed = reason or 'fixed'

    @usermethod
    def release(self):
        """Release the device, i.e. undo the effect of fix()."""
        self.fixed = ''


class HasLimits(Moveable):
    """
    Mixin for "simple" continuously moveable devices that have limits.
    """

    parameters = {
        'userlimits': Param('User defined limits of device value', unit='main',
                            type=tupleof(float, float), settable=True),
        'abslimits':  Param('Absolute limits of device value', unit='main',
                            type=tupleof(float, float), mandatory=True),
    }

    def init(self):
        Moveable.init(self)
        if isinstance(self, HasOffset):
            offset = self.offset
        else:
            offset = 0
        if self.abslimits[0] > self.abslimits[1]:
            raise ConfigurationError(self, 'absolute minimum (%s) above the '
                                     'absolute maximum (%s)' % self.abslimits)
        if self.userlimits[0] + offset < self.abslimits[0]:
            self.log.warning('user minimum (%s) below absolute minimum (%s), '
                             'please check and re-set limits' %
                             (self.userlimits[0], self.abslimits[0]))
        if self.userlimits[1] + offset > self.abslimits[1]:
            self.log.warning('user maximum (%s) above absolute maximum (%s), '
                             'please check and re-set limits' %
                             (self.userlimits[1], self.abslimits[1]))
        if session.mode == 'simulation':
            # special case: in simulation mode, doReadUserlimits is not called,
            # so the limits are not set from the absolute limits, and are always
            # (0, 0) except when set in the setup file
            if self.userlimits == (0.0, 0.0):
                self.userlimits = self.abslimits

    @property
    def absmin(self):
        return self.abslimits[0]
    @property
    def absmax(self):
        return self.abslimits[1]

    def __getusermin(self):
        return self.userlimits[0]
    def __setusermin(self, value):
        self.userlimits = (value, self.userlimits[1])
    usermin = property(__getusermin, __setusermin)

    def __getusermax(self):
        return self.userlimits[1]
    def __setusermax(self, value):
        self.userlimits = (self.userlimits[0], value)
    usermax = property(__getusermax, __setusermax)

    del __getusermin, __setusermin, __getusermax, __setusermax

    def isAllowed(self, target):
        limits = self.userlimits
        if not limits[0] <= target <= limits[1]:
            return False, 'limits are [%s, %s]' % limits
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(target)
        return True, ''

    def _checkLimits(self, limits):
        umin, umax = limits
        amin, amax = self.abslimits
        if isinstance(self, HasOffset):
            offset = getattr(self, '_new_offset', self.offset)
            umin += offset
            umax += offset
        else:
            offset = 0
        if umin > umax:
            raise ConfigurationError(
                self, 'user minimum (%s, offset %s) above the user '
                'maximum (%s, offset %s)' % (umin, offset, umax, offset))
        if umin < amin:
            raise ConfigurationError(
                self, 'user minimum (%s, offset %s) below the '
                'absolute minimum (%s)' % (umin, offset, amin))
        if umax > amax:
            raise ConfigurationError(
                self, 'user maximum (%s, offset %s) above the '
                'absolute maximum (%s)' % (umax, offset, amax))

    def doReadUserlimits(self):
        if 'userlimits' not in self._config:
            self.log.info('setting userlimits from abslimits, which are %s'
                            % (self.abslimits,))
            return self.abslimits
        cfglimits = self._config['userlimits']
        self._checkLimits(cfglimits)
        return cfglimits

    def doWriteUserlimits(self, value):
        self._checkLimits(value)
        if isinstance(self, HasOffset) and hasattr(self, '_new_offset'):
            # when changing the userlimits are adjusted so that the value
            # stays within them, but only after the new offset is applied
            return
        curval = self.read(0)
        if not value[0] <= curval <= value[1]:
            self.log.warning('current device value (%s) not within new '
                              'userlimits (%s, %s)' %
                              ((self.format(curval),) + value))

    def _adjustLimitsToOffset(self, value, diff):
        """Adjust the user limits to the given offset.

        Used by the HasOffset mixin class to adjust the offset. *value* is the
        offset value, *diff* the offset difference.
        """
        limits = self.userlimits
        self._new_offset = value
        self.userlimits = (limits[0] - diff, limits[1] - diff)
        del self._new_offset


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
        old_offset = self.offset
        diff = value - old_offset
        if isinstance(self, HasLimits):
            self._adjustLimitsToOffset(value, diff)
        # Since offset changes directly change the device value, refresh
        # the cache instantly here
        if self._cache:
            self._cache.put(self, 'value', self.read(0) - diff,
                            currenttime(), self.maxage)
        session.elog_event('offset', (str(self), old_offset, value))


class HasPrecision(object):
    """
    Mixin class for Readable and Moveable devices that want to provide a
    'precision' parameter.

    This is mainly useful for user info, and for high-level devices that have to
    work with limited-precision subordinate devices.
    """

    parameters = {
        'precision': Param('Precision of the device value', unit='main',
                           settable=True, category='precisions'),
    }


class Measurable(Readable):
    """
    Base class for devices used for data acquisition.

    Subclasses *need* to implement:

    * doRead()
    * doSetPreset(**preset)
    * doStart(**preset)
    * doStop()
    * doIsCompleted()

    Subclasses *can* implement:

    * doPause()
    * doResume()
    * doTime()
    * doSimulate()
    * valueInfo()
    * presetInfo()
    """

    parameter_overrides = {
        'unit':  Override(description='(not used)', mandatory=False),
    }

    @usermethod
    def setPreset(self, **preset):
        """Set the new standard preset for this detector."""
        self.doSetPreset(**preset)

    @usermethod
    def start(self, **preset):
        """Start measurement, with either the given preset or the standard
        preset.

        This operation is forbidden in slave mode.

        .. method:: doStart(**preset)

           This method must be present and is called to start the measurement.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'start not possible in slave mode')
        elif self._sim_active:
            if hasattr(self, 'doTime'):
                time = self.doTime(preset)
            else:
                if 't' in preset:
                    time = preset['t']
                else:
                    time = 0
            session.clock.tick(time)
            self._sim_preset = preset
            return
        self.doStart(**preset)

    def __call__(self, pos=None):
        """Allow dev(), but not dev(pos)."""
        if pos is None:
            return self.read()
        raise UsageError(self, 'device cannot be moved')

    def duringMeasureHook(self, cycle):
        """Hook called during measurement.

        This can be overridden in subclasses to perform some periodic action
        while measuring.  The hook is called by `.count` for every detector in
        a loop with a delay of 0.025 seconds.  The *cycle* argument is a number
        incremented with each call to the hook.
        """

    @usermethod
    def pause(self):
        """Pause the measurement, if possible.

        Return True if paused successfully.  This operation is forbidden in
        slave mode.

        .. method:: doPause()

           If present, this is called to pause the measurement.  Otherwise,
           ``False`` is returned to indicate that pausing is not possible.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'pause not possible in slave mode')
        elif self._sim_active:
            return True
        if hasattr(self, 'doPause'):
            return self.doPause()
        return False

    @usermethod
    def resume(self):
        """Resume paused measurement.

        Return True if resumed successfully.  This operation is forbidden in
        slave mode.

        .. method:: doResume()

           If present, this is called to resume the measurement.  Otherwise,
           ``False`` is returned to indicate that resuming is not possible.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'resume not possible in slave mode')
        elif self._sim_active:
            return True
        if hasattr(self, 'doResume'):
            return self.doResume()
        return False

    @usermethod
    def stop(self):
        """Stop measurement now.

        This operation is forbidden in slave mode.

        .. method:: doStop()

           This method must be present and is called to actually stop the
           measurement.

        The `stop` method will return the device status after stopping.
        """
        if self._mode == 'slave':
            raise ModeError(self, 'stop not possible in slave mode')
        elif self._sim_active:
            return
        self.doStop()

    @usermethod
    def isCompleted(self):
        """Return true if measurement is complete.

        .. method:: doIsCompleted()

           This method must be present and is called to determine if the
           measurement is completed.
        """
        if self._sim_active:
            return True
        return self.doIsCompleted()

    @usermethod
    def wait(self):
        """Wait for completion of the measurement.

        This is implemented by calling :meth:`isCompleted` in a loop.
        """
        while not self.isCompleted():
            sleep(0.1)

    @usermethod
    def read(self, maxage=None):
        """Return a tuple with the result(s) of the last measurement."""
        if self._sim_active:
            if hasattr(self, 'doSimulate'):
                return self.doSimulate(self._sim_preset)
            return [0] * len(self.valueInfo())
        # always get fresh result from cache => maxage parameter is ignored
        if self._cache:
            self._cache.invalidate(self, 'value')
        result = self._get_from_cache('value', self.doRead)
        if not isinstance(result, list):
            return [result]
        return result

    def save(self):
        """Save the current measurement, if necessary.

        Called by `.count` for all detectors at the end of a counting.

        .. method:: doSave()

           This method can be implemented if the detector needs to save data.
        """
        if self._sim_active:
            return
        if hasattr(self, 'doSave'):
            self.doSave()

    def info(self):
        """Automatically add device status (if not OK).  Does not add the
        device value since that is typically not useful for Measurables.
        """
        try:
            st = self.status()
        except Exception, err:
            self.log.warning('error getting status for info()', exc=err)
            yield ('status', 'status', 'Error: %s' % err)
        else:
            if st[0] not in (status.OK, status.UNKNOWN):
                yield ('status', 'status', '%s: %s' % st)
        for item in Device.info(self):
            yield item

    def valueInfo(self):
        """Describe the values measured by this device.

        Return a tuple of :class:`~nicos.core.params.Value` instances describing
        the values that :meth:`read` returns.

        This must be overridden by every Measurable that returns more than one
        value in a list.  The default indicates a single return value with no
        additional info about the value type.
        """
        return Value(self.name, unit=self.unit),

    def presetInfo(self):
        """Return an iterable of preset keys accepted by this device.

        The default implementation returns only a 't' (time) preset.  This must
        be overridden by all measurables that support more presets.
        """
        return ('t',)
