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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS core utility functions."""

import sys
from time import sleep, localtime, time as currenttime
from collections import namedtuple

from nicos import session
from nicos.core import status, NicosError, SIMULATION
from nicos.pycompat import reraise, to_ascii_escaped, listitems
from nicos.utils import formatDuration


# user access levels
GUEST = 0
USER = 10
ADMIN = 20
ACCESS_LEVELS = {0: 'guest', 10: 'user', 20: 'admin'}


User = namedtuple('User', 'name, level')

system_user = User('system', ADMIN)
watchdog_user = User('watchdog', ADMIN)


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
        devices = listitems(devices)
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
                        for subsubdev in devIter(subdev._getWaiters(),
                                                 baseclass, onlydevs,
                                                 allwaiters):
                            yield subsubdev
                    yield subdev if onlydevs else (subdev.name, subdev)
        else:
            if isinstance(dev, baseclass):
                if allwaiters:
                    for subdev in devIter(dev._getWaiters(), baseclass,
                                          onlydevs, allwaiters):
                        yield subdev
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
    from nicos.core import Readable
    # get to work
    rettext = []
    retstate = 0
    for devname, dev in devIter(devices, Readable, onlydevs=False):
        state, text = dev.status(maxage)
        if '=' in text:
            rettext.append('%s=(%s)' % (devname, text))
        elif text:
            rettext.append('%s=%s' % (devname, text))
        if state > retstate:
            retstate = state
    if retstate > 0:
        return retstate, ', '.join(rettext)
    else:
        return status.UNKNOWN, 'no status could be determined (no doStatus ' \
                               'implemented?)'


def multiWait(devices):
    """Wait for the *devices*.

    Returns a dictionary mapping devices to current values after waiting.

    This is the main waiting loop to be used when waiting for multiple devices.
    It checks the device status until all devices are OK or errored.

    Errors raised are handled like in _multiMethod: the first one is reraised
    at the end, the others are only printed as errors.

    *baseclass* allows to restrict the devices waited on.
    """
    from nicos.core import Waitable

    def get_target_str():
        return ', '.join('%s -> %s' % (dev, dev.format(dev.target))
                         if hasattr(dev, 'target') else str(dev)
                         for dev in reversed(devlist))

    delay = 0.3
    first_exc = None
    devlist = list(devIter(devices, baseclass=Waitable, allwaiters=True))
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
            loops += 1
            for dev in devlist[:]:
                try:
                    done = dev.isCompleted()
                    if done:
                        dev.finish()
                except Exception:
                    if not first_exc:
                        first_exc = sys.exc_info()
                    else:
                        dev.log.exception('while waiting')
                    # remove this device from the waiters - we might still have
                    # its subdevices in the list so that multiWait() should not
                    # return until everything is either OK or ERROR
                    devlist.remove(dev)
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
                    # of excplicitly given devices
                    values[dev] = dev.read()
                # this device is done: don't wait for it anymore
                devlist.remove(dev)
                target_str = get_target_str()
                session.action(eta_str + target_str)
            if devlist:
                if eta_update >= 1:
                    eta_update -= 1
                    now = currenttime()
                    eta = set(dev.estimateTime(now - first_ts)
                              for dev in devlist)
                    eta.discard(None)
                    # use max here as we wait for ALL movements to finish
                    eta_str = ('estimated %s left / ' % formatDuration(max(eta))
                               if eta else '')
                    session.action(eta_str + target_str)
                sleep(delay)
                eta_update += delay
        if first_exc:
            reraise(*first_exc)
    finally:
        session.endActionScope()
    return values


def waitForStatus(dev, delay=0.3, ignore_errors=False):
    """Wait for *dev* to exit the busy state.

    Calls `isCompleted` until it returns true or raises.
    """
    try:
        while not dev.isCompleted():
            sleep(delay)
    except NicosError:
        if ignore_errors:
            return
        raise


def formatStatus(st):
    const, message = st
    const = status.statuses.get(const, str(const))
    return const + (message and ': ' + message or '')


def statusString(*strs):
    """Combine multiple status strings, using commas as needed."""
    return ', '.join(s for s in strs if s)


def _multiMethod(baseclass, method, devices):
    """Calls a method on a list of devices.

    The first given exception is re-raised after all method calls have been
    finished, all other exceptions are logged and not re-raised.

    Additional arguments are used when calling the method.
    The same arguments are used for *ALL* calls.
    """
    first_exc = None
    for dev in devIter(devices, baseclass):
        try:
            # method has to be provided by baseclass!
            getattr(dev, method)()
        except Exception:
            if not first_exc:
                first_exc = sys.exc_info()
            else:
                dev.log.exception('during %s()' % method)
    if first_exc:
        reraise(*first_exc)


def multiStop(devices):
    """Stop every 'stoppable' device in the *devices* list.

    The first given exception is re-raised after all stop() calls have been
    finished, all other exceptions are logged and not re-raised.
    """
    from nicos.core import Moveable
    _multiMethod(Moveable, 'stop', devices)


def multiReset(devices):
    """Resets every 'resetable' device in the *devices* list.

    The first given exception is re-raised after all reset() calls have been
    finished, all other exceptions are logged and not re-raised.
    """
    from nicos.core import Readable
    _multiMethod(Readable, 'reset', devices)


class DeviceValue(namedtuple('DeviceValue',
                             ('raw', 'formatted', 'unit', 'category'))):
    """Wrapper for metainfo values

        Provides different ways to access the meta info:
        - as a tuple with numeric indexing
        - as an object with named access
        - string representation compatible with legacy DeviceValueDict usage
    """
    __slots__ = ()

    def __str__(self):
        return str(self.formatted)

    def __int__(self):
        return int(self.raw)

    def __long__(self):
        return long(self.raw)

    def __float__(self):
        return float(self.raw)


class DeviceValueDict(object):
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
        # we dont want to raise anything!
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
                        for key in extra:
                            yield key
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
                        session.log.debug('calling %s%r' % (dev, args))
                        dev = dev(*args)
                    elif hasattr(dev, sub):
                        dev = getattr(dev, sub)
                    elif hasattr(dev, '_adevs') and sub in dev._adevs:
                        dev = dev._adevs[sub]
                    elif hasattr(dev, '__contains__') and sub in dev:
                        dev = dev[sub]
                    else:
                        session.log.warning("invalid key %r requested, "
                                            "returning %r" % (key, res),
                                            exc=1)
                        break
                else:
                    # stringify result
                    res = str(dev)
        except Exception:
            session.log.warning("invalid key %r requested, returning %r" %
                                (key, res), exc=1)
        if isinstance(res, bytes):
            res = to_ascii_escaped(res)
        if isinstance(res, DeviceValue):
            return res
        if raw is None:
            raw = res
        final = DeviceValue(raw=raw,
                            formatted=res,
                            unit=unit or '',
                            category='meta')
        return final
