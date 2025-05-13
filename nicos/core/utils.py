# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS core utility functions."""

from collections import namedtuple
from functools import wraps
from time import localtime, time as currenttime

from nicos import nicos_version, session
from nicos.core import status
from nicos.core.constants import SIMULATION
from nicos.core.errors import CommunicationError, ComputationError, \
    InvalidValueError, LimitError, MoveError, NicosError, NicosTimeoutError, \
    PositionError
from nicos.protocols.daemon import BREAK_AFTER_STEP
from nicos.utils import createThread, formatDuration, toAscii

# Exceptions at which a scan point is measured anyway.
CONTINUE_EXCEPTIONS = (PositionError, MoveError, NicosTimeoutError)
# Exceptions at which a scan point is skipped.
SKIP_EXCEPTIONS = (InvalidValueError, LimitError, CommunicationError,
                   ComputationError)


# user access levels
GUEST = 0
USER = 10
ADMIN = 20
ACCESS_LEVELS = {GUEST: 'guest', USER: 'user', ADMIN: 'admin'}

_User = namedtuple('User', ('name', 'level', 'data'))


class User(_User):
    """Named tuple for NICOS users that provides a default value for the
    ``data`` field.
    """

    def __new__(cls, name, level, data=None):
        return _User.__new__(cls, name, level, {} if data is None else data)


system_user = User('system', ADMIN)
watchdog_user = User('watchdog', ADMIN)


def usermethod(func=None, doc=None, helparglist=None):
    """Decorator that marks a method as a user-visible method.

    The method will be shown to the user in the help for a device.
    """
    # new style usage:
    #   @usermethod(doc='blah')
    #   def meth(...)
    if func is None:
        def deco(func):
            func.is_usermethod = True
            if doc:
                func.help_doc = doc
            if helparglist:
                func.help_arglist = helparglist
            return func
        return deco
    # legacy usage:
    #   @usermethod
    #   def meth(...)
    func.is_usermethod = True
    return func


def deprecated(since=nicos_version, comment=''):
    """This is a decorator which can be used to mark functions as deprecated.

    It will result in a warning being emitted when the function is used.

    The parameter ``since`` should contain the NICOS version number on which
    the deprecation starts.

    The ``comment`` should contain a hint to the user, what should be used
    instead.
    """
    def deco(f):
        msg = '%r is deprecated since version %r.' % (f.__name__, since)

        @wraps(f)
        def new_func(*args, **options):
            for l in [msg, comment]:
                session.log.warning(l)
            return f(*args, **options)
        new_func.__doc__ += ' %s %s' % (msg, comment)
        return new_func
    return deco


def devIter(devices, baseclass=None, onlydevs=True, allwaiters=False):
    """Filtering generator over the given devices.

    Iterates over the given devices.  If the *baseclass* argument is specified
    (not ``None``), filter out (ignore) those devices which do not belong to
    the given baseclass.  If the boolean *onlydevs* argument is false, yield
    ``(name, devices)`` tuples otherwise just the devices.

    If *allwaiters* is true, recursively include devices given by devices'
    ``_getWaiters`` methods.

    The given devices argument can either be a dictionary (_adevs, _sdevs,...)
    or a list of (name, device) tuples or a simple list of devices.
    """
    if baseclass is None:
        # avoid import loop and still default to Device
        from nicos.core.device import Device
        baseclass = Device
    # convert dict to list of name:dev tuples
    if isinstance(devices, dict):
        devices = list(devices.items())
    else:
        # we iterate twice: make sure to convert generators
        # to a list first
        devices = list(devices)
        try:  # to convert list of devices into desired format
            devices = [(dev.name, dev) for dev in devices if dev]
        except AttributeError:
            pass  # not convertible, must be right format already...
    for devname, dev in devices:
        # handle _adevs style entries correctly
        if isinstance(dev, (tuple, list)):
            for subdev in dev:
                if isinstance(subdev, baseclass):
                    if allwaiters:
                        yield from devIter(subdev._getWaiters(), baseclass,
                                           onlydevs, allwaiters)
                    yield subdev if onlydevs else (subdev.name, subdev)
        else:
            if isinstance(dev, baseclass):
                if allwaiters:
                    yield from devIter(dev._getWaiters(), baseclass,
                                       onlydevs, allwaiters)
                yield dev if onlydevs else (devname, dev)


def multiStatus(devices, maxage=None):
    """Combine the status of multiple devices to form a single status value.

    This is called in the default `doStatus` method of "superdevices" that
    control several attached devices.

    The resulting state value is the highest value of all devices' values
    (i.e. if all devices are `OK`, it will be `OK`, if one is `BUSY`, it will
    be `BUSY`, but if one is `ERROR`, it will be `ERROR`).

    The resulting state text is a combination of the status texts of all
    devices.
    """
    from nicos.core.device import Readable

    # get to work
    rettext = []
    retstate = 0
    for devname, dev in devIter(devices, Readable, onlydevs=False):
        state, text = dev.status(maxage)
        if '=' in text:
            rettext.append('%s=(%s)' % (devname, text))
        elif text:
            rettext.append('%s=%s' % (devname, text))
        retstate = max(retstate, state)
    if retstate > 0:
        return retstate, ', '.join(rettext)
    return status.UNKNOWN, 'no status could be determined (no doStatus ' \
                           'implemented?)'


def multiWait(devices):
    """Wait for the *devices*.

    Returns a dictionary mapping devices to current values after waiting.

    This is the main waiting loop to be used when waiting for multiple devices.
    It checks the device status until all devices are OK or errored.

    Errors raised are handled like in the following way:
    The error is logged, and the first exception with the highest severity
    (exception in `CONTINUE_EXECPTIONS` < `SKIP_EXCEPTIONS` < other exceptions)
    is re-raised at the end.

    *baseclass* allows to restrict the devices waited on.
    """
    from nicos.core.device import Waitable

    def get_target_str():
        return ', '.join('%s -> %s' % (dev, dev.format(dev.target))
                         if hasattr(dev, 'target') else str(dev)
                         for dev in reversed(devlist))

    delay = 0.3
    final_exc = None
    devlist = list(devIter(devices, baseclass=Waitable, allwaiters=True))
    session.log.debug('multiWait: initial devices %s, all waiters %s',
                      devices, devlist)
    values = {}
    loops = -2  # wait 2 iterations for full loop
    eta_update = 1 if session.mode != SIMULATION else 0
    first_ts = currenttime()
    session.beginActionScope('Waiting')
    eta_str = ''
    target_str = get_target_str()
    session.action(target_str)
    try:
        while devlist:
            session.breakpoint(BREAK_AFTER_STEP)  # allow break and continue here
            session.log.debug('multiWait: iteration %d, devices left %s',
                              loops, devlist)
            loops += 1
            for dev in devlist[:]:
                try:
                    done = dev.isCompleted()
                    if done:
                        dev.finish()
                except Exception as exc:
                    final_exc = filterExceptions(exc, final_exc)
                    # remove this device from the waiters - we might still have
                    # its subdevices in the list so that multiWait() should not
                    # return until everything is either OK or ERROR
                    devlist.remove(dev)
                    if devlist:
                        # at least one more device left, show the exception now
                        dev.log.exception('while waiting')
                    continue
                if not done:
                    # we found one busy dev, normally go to next iteration
                    # until this one is done (saves going through the whole
                    # list of devices and doing unnecessary HW communication)
                    if loops % 10:
                        break
                    # every 10 loops, go through everything to get an accurate
                    # display in the action line
                    continue
                if dev in devices:
                    # populate the results dictionary, but only with the values
                    # of explicitly given devices
                    values[dev] = dev.read()
                # this device is done: don't wait for it anymore
                devlist.remove(dev)
                target_str = get_target_str()
                session.action(eta_str + target_str)
            if devlist:
                if eta_update >= 1:
                    eta_update -= 1
                    now = currenttime()
                    eta = {dev.estimateTime(now - first_ts) for dev in devlist}
                    eta.discard(None)
                    # use max here as we wait for ALL movements to finish
                    eta_str = ('Estimated %s left / ' % formatDuration(max(eta))
                               if eta else '')
                    session.action(eta_str + target_str)
                session.delay(delay)
                eta_update += delay
        if final_exc:
            raise final_exc
    finally:
        session.endActionScope()
        session.log.debug('multiWait: finished')
    return values


def filterExceptions(curr, prev):
    if not prev:
        return curr
    if (isinstance(prev, CONTINUE_EXCEPTIONS) and
       not isinstance(curr, CONTINUE_EXCEPTIONS)):
        return curr
    if (isinstance(prev, SKIP_EXCEPTIONS) and
       not isinstance(curr, SKIP_EXCEPTIONS + CONTINUE_EXCEPTIONS)):
        return curr
    return prev


def waitForState(dev, state, delay=0.3, ignore_errors=False):
    """Wait for `dev` to getting into `state`.

    Calls `status` until it returns `state` on its first element or raises.
    """
    try:
        while True:
            st = dev.status()[0]
            if st == state:
                break
            session.delay(delay)
    except Exception:
        if ignore_errors:
            return
        raise


def waitForCompletion(dev, delay=0.3, ignore_errors=False):
    """Wait for *dev* to exit the busy state.

    Calls `isCompleted` until it returns true or raises.
    """
    try:
        while not dev.isCompleted():
            session.delay(delay)
    except NicosError:
        if ignore_errors:
            return
        raise


def multiReference(dev, subdevs, parallel=False):
    """Run a reference drive of *subdevs* (belonging to the main *dev*).

    If *parallel* is true, use one thread per device.
    """
    from nicos.devices.abstract import CanReference

    if not parallel:
        for subdev in subdevs:
            if isinstance(subdev, CanReference):
                dev.log.info('referencing %s...', subdev)
                subdev.reference()
            else:
                dev.log.warning('%s cannot be referenced', subdev)
        return

    def threaded_ref(i, d):
        try:
            d.reference()
        except Exception:
            d.log.error('while referencing', exc=1)
            errored[i] = True

    threads = []
    errored = [False] * len(subdevs)

    for (i, subdev) in enumerate(subdevs):
        if isinstance(subdev, CanReference):
            dev.log.info('referencing %s...', subdev)
            threads.append(createThread('reference %s' % subdev,
                                        threaded_ref, (i, subdev)))
        else:
            dev.log.warning('%s cannot be referenced', subdev)

    for thread in threads:
        thread.join()
    if any(errored):
        raise MoveError(dev, 'referencing failed for ' +
                        ', '.join(str(subdev) for (subdev, err)
                                  in zip(subdevs, errored) if err))


def formatStatus(st):
    const, message = st
    const = status.statuses.get(const, str(const))
    return const + (message and ': ' + message or '')


def statusString(*strs):
    """Combine multiple status strings, using commas as needed."""
    return ', '.join(s for s in strs if s)


def _multiMethod(baseclass, method, devices):
    """Calls a method on a list of devices.

    Errors raised are handled like in the following way:
    The error is logged, and the first exception with the highest severity
    (exception in `CONTINUE_EXCEPTIONS` < `SKIP_EXCEPTIONS` < other exceptions)
    is re-raised at the end.

    Additional arguments are used when calling the method.
    The same arguments are used for *ALL* calls.
    """
    final_exc = None
    for dev in devIter(devices, baseclass):
        try:
            # method has to be provided by baseclass!
            getattr(dev, method)()
        except Exception as exc:
            dev.log.exception('during %s()', method)
            final_exc = filterExceptions(exc, final_exc)
    if final_exc:
        raise final_exc


def multiStop(devices):
    """Stop every 'stoppable' device in the *devices* list.

    The first given exception is re-raised after all stop() calls have been
    finished, all other exceptions are logged and not re-raised.
    """
    from nicos.core.device import Moveable
    _multiMethod(Moveable, 'stop', devices)


def multiReset(devices):
    """Resets every 'resetable' device in the *devices* list.

    The first given exception is re-raised after all reset() calls have been
    finished, all other exceptions are logged and not re-raised.
    """
    from nicos.core.device import Readable
    _multiMethod(Readable, 'reset', devices)


class DeviceValue(namedtuple('DeviceValue',
                             ('raw', 'formatted', 'unit', 'category'))):
    """Wrapper for metainfo values

        Provides different ways to access the metainfo:
        - as a tuple with numeric indexing
        - as an object with named access
        - string representation compatible with legacy DeviceValueDict usage
    """
    __slots__ = ()

    def __str__(self):
        return str(self.formatted)

    def __int__(self):
        return int(self.raw)

    def __float__(self):
        return float(self.raw)


class DeviceValueDict:
    """Convenience class to be used for templating device values/params.

    Constructor works like a dict, so you can specify any mappings there.

    Requesting a key, the following rules are checked in that order:
    1) if a key is request which was specified to the constructor,
       that specified value will be returned.
    2) if a key names a device, that device is read.
    3) if a key contains dots and the substring before the first dot names
       a device, we follow the 'chain' of substring named attributes/calls.
       A substring ending in '()' causes the attribute to be called.
       If all substrings could be resolved we return the
       attribute.  If some steps fail, we warn and return an empty string.
       This is unlike an ordinary dictionary which would raise a KeyError
       if the requested key does not exist.

    All return values are wrapped as a DeviceValue object. If no raw value
    is present, then the raw and formatted value are the same.

    Examples:

    >>> d = DeviceValueDict(stuff=1)
    >>> d['experiment.proposal']
    'p4992'
    >>> '%(stuff)03d_%(Sample.samplename)s' % d # intended use case
    '001_Samplename of currently used sample.'
    """
    def __init__(self, *args, **kwargs):
        self._constvals = dict(*args, **kwargs)
        # convenience stuff
        l = localtime()
        self._constvals.setdefault('year', l.tm_year)
        self._constvals.setdefault('month', l.tm_mon)
        self._constvals.setdefault('day', l.tm_mday)
        self._constvals.setdefault('hour', l.tm_hour)
        self._constvals.setdefault('minute', l.tm_min)
        self._constvals.setdefault('second', l.tm_sec)

    def __setitem__(self, key, value):
        self._constvals[key] = value

    def update(self, *args, **kwargs):
        self._constvals.update(*args, **kwargs)

    def __delitem__(self, key):
        del self._constvals[key]

    def __getitem__(self, key):
        res = ''
        raw = None
        unit = None
        # we don't want to raise anything!
        try:
            # value given to constructor?
            if key in self._constvals:
                res = self._constvals[key]
            # just a device?
            elif key in session.configured_devices:
                dev = session.getDevice(key)
                raw = dev.read()
                res = dev.format(raw)
                unit = dev.unit
            # attrib path? (must start with a device!)
            elif '.' in key:
                keys = key.split('.')
                # handle session specially
                if keys[0] == 'session':
                    dev = session
                else:
                    dev = session.getDevice(keys[0])
                # we got a starting point, follow the chain of attribs...

                def _keyiter(keys):
                    for key in keys:
                        extra = []
                        while key:
                            if key.endswith(']') and '[' in key:
                                splitpos = key.rfind('[')
                                extra.insert(0, key[splitpos:])
                                key = key[:splitpos]
                            elif key.endswith(')') and '(' in key:
                                splitpos = key.rfind('(')
                                extra.insert(0, key[splitpos:])
                                key = key[:splitpos]
                            else:
                                break
                        yield key
                        yield from extra
                for sub in _keyiter(keys[1:]):
                    if sub.endswith(']'):
                        val = sub[1:-1]
                        try:
                            val = float(val)
                            val = int(val)
                        except Exception:
                            pass
                        dev = dev[val]
                    elif sub.endswith(')'):
                        args = sub[1:-1].split(',')
                        args = [a for a in args if a]  # strip empty args
                        for i, a in enumerate(args):
                            try:
                                args[i] = float(a)
                                args[i] = int(a)
                            except Exception:
                                pass
                        # TODO: handle kwargs
                        args = tuple(args)
                        session.log.debug('calling %s%r', dev, args)
                        dev = dev(*args)
                    elif hasattr(dev, sub):
                        dev = getattr(dev, sub)
                    elif hasattr(dev, '_adevs') and sub in dev._adevs:
                        dev = dev._adevs[sub]
                    elif hasattr(dev, '__contains__') and sub in dev:
                        dev = dev[sub]
                    else:
                        session.log.warning('invalid key %r requested, '
                                            'returning %r', key, res,
                                            exc=1)
                        break
                else:
                    # stringify result
                    res = str(dev)
        except Exception:
            session.log.warning('invalid key %r requested, returning %r',
                                key, res, exc=1)
        if isinstance(res, bytes):
            res = toAscii(res.decode('latin1', 'ignore'))
        if isinstance(res, DeviceValue):
            return res
        if raw is None:
            raw = res
        final = DeviceValue(raw=raw,
                            formatted=res,
                            unit=unit or '',
                            category='meta')
        return final
