# -*- coding: utf-8 -*-
"""
    nicm.device
    ~~~~~~~~~~~

    Base device classes for usage in NICOS.
"""

from nicm import nicos
from nicm import status, loggers
from nicm.utils import MergedAttrsMeta
from nicm.errors import ConfigurationError, ProgrammingError, UsageError, \
     OutofBoundsError


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
        'autocreate': (True, False, 'Whether the device is automatically '
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
                    raise UsageError('%s: cannot set the %s parameter' %
                                     (self, param))
            setattr(self, 'get' + param.title(), getter)
            setattr(self, 'set' + param.title(), setter)

        # initialize some standard parameters
        self._params['name'] = name
        if not self._params['description']:
            self._params['description'] = name
        # set loglevel (also checks validity explicitly)
        self.setPar('loglevel', self._params['loglevel'])

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
        self.init()

    def __str__(self):
        return self._params['name']

    def __repr__(self):
        if self.getPar('name') == self.getPar('description'):
            return '<device %s (a %s)>' % (self.getPar('name'),
                                           self.__class__.__name__)
        return '<device %s, %s (a %s)>' % (self.getPar('name'),
                                           self.getPar('description'),
                                           self.__class__.__name__)

    def init(self):
        """Initialize the device; this is called when a device is created."""
        if hasattr(self, 'doInit'):
            self.doInit()

    def shutdown(self):
        """Shut down the device; called from NicmDestroy()."""
        if hasattr(self, 'doShutdown'):
            self.doShutdown()


class Readable(Device):
    """
    Base class for all readable devices.
    """

    parameters = {
        'fmtstr': ('%s', False, 'Format string for the device value.'),
        'unit': ('', True, 'Unit of the device main value.'),
    }

    def read(self):
        """Read the main value of the device."""
        return self.doRead()

    def status(self):
        """Return the status of the device as one of the integer constants
        defined in the nicm.status module.
        """
        if hasattr(self, 'doStatus'):
            value = self.doStatus()
            if value not in status.statuses:
                raise ProgrammingError('%s: status return %r unknown' %
                                       (self, value))
            return value
        return status.UNKNOWN

    def reset(self):
        """Reset the device hardware."""
        if hasattr(self, 'doReset'):
            self.doReset()

    def format(self, value):
        """Format a value from self.read() into a human-readable string."""
        return self.getPar('fmtstr') % value

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

    def start(self, pos):
        """Start movement of the device to a new position."""
        ok, why = self.isAllowed(pos)
        if not ok:
            raise OutofBoundsError('%s: moving to %r is not allowed: %s' %
                                   (self, pos, why))
        self.doStart(pos)

    moveTo = start
    move = start

    def stop(self):
        """Stop any movement of the device."""
        if hasattr(self, 'doStop'):
            self.doStop()

    def wait(self):
        """Wait until the device has stopped moving."""
        if hasattr(self, 'doWait'):
            self.doWait()

    def isAllowed(self, pos):
        """Return a tuple describing the validity of the given position.

        The first item is a boolean indicating if the position is valid,
        the second item is a string with the reason if it is invalid.
        """
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(pos)
        return True, ''


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
        self.rev_switchlist = dict((v, k) for (k, v) in self.switchlist.items())
        if len(self.rev_switchlist) != len(self.switchlist):
            raise ProgrammingError('%s: duplicate value in switchlist' % self)

    def start(self, pos):
        """Switch the device to a new value.

        The given position can be either a human-readable value from the
        switchlist, or the "internal" value.
        """
        realpos = self.switchlist.get(pos, pos)
        if realpos not in self.rev_switchlist:
            raise UsageError('%s: %r is not an acceptable switch value' %
                             (self, pos))
        ok, why = self.isAllowed(realpos)
        if not ok:
            raise OutofBoundsError('%s: switching to %r is not allowed: %s' %
                                   (self, pos, why))
        self.doStart(realpos)

    def stop(self):
        """Stop any switching activity of the device."""
        if hasattr(self, 'doStop'):
            self.doStop()

    def wait(self):
        """Wait until the switching is completed."""
        if hasattr(self, 'doWait'):
            self.doWait()

    switchTo = start
    switch = start

    def isAllowed(self, pos):
        """Return a tuple describing the validity of the given position.

        The first item is a boolean indicating if the position is valid,
        the second item is a string with the reason if it is invalid.
        """
        if hasattr(self, 'doIsAllowed'):
            return self.doIsAllowed(pos)
        return True, ''

    def format(self, pos):
        """Format a value from self.read() into the corresponding human-readable
        value from the switchlist.
        """
        return self.rev_switchlist.get(pos, pos)


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

    def clear(self):
        """Clear the counter value."""
        self.doClear()

    def wait(self):
        """Wait until the counting is complete."""
        self.doWait()

    def setPreset(self, value):
        """Set a new standard preset."""
        self.doSetPreset(value)
