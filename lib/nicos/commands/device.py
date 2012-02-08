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

"""Module for simple device-related user commands."""

__version__ = "$Revision$"

import time
import threading
import __builtin__

from nicos import session
from nicos.utils import printTable
from nicos.core import Device, Moveable, Measurable, Readable, HasOffset, \
     HasLimits, NicosError, UsageError
from nicos.core.status import statuses
from nicos.commands import usercommand
from nicos.commands.basic import sleep
from nicos.commands.output import printinfo


def _devposlist(dev_pos_list, cls):
    devlist = []
    poslist = []
    if len(dev_pos_list) == 0:
        raise UsageError('at least one device and position must be given')
    if len(dev_pos_list) % 2 != 0:
        raise UsageError('a position must be given for every device')
    for i in range(len(dev_pos_list)):
        if i % 2 == 0:
            devlist.append(session.getDevice(dev_pos_list[i], cls))
            poslist.append(dev_pos_list[i+1])
    return zip(devlist, poslist)

@usercommand
def move(*dev_pos_list):
    """Move one or more devices to a new position.

    This can be used with multiple devices like this::

        move(dev1, pos1, dev2, pos2, ...)
    """
    for dev, pos in _devposlist(dev_pos_list, Moveable):
        dev.log.info('moving to', dev.format(pos), dev.unit)
        dev.move(pos)

@usercommand
def drive(*dev_pos_list):
    """Move one or more devices to a new position.  Same as `move()`.

    This can be used with multiple devices like this::

        drive(dev1, pos1, dev2, pos2, ...)
    """
    return move(*dev_pos_list)

@usercommand
def maw(*dev_pos_list):
    """Move one or more devices to a new position and wait until motion
    of all devices is completed.

    This can be used with multiple devices like this::

        maw(dev1, pos1, dev2, pos2, ...)
    """
    devs = []
    for dev, pos in _devposlist(dev_pos_list, Moveable):
        dev.log.info('moving to', dev.format(pos), dev.unit)
        dev.move(pos)
        devs.append(dev)
    for dev in devs:
        dev.wait()
        read(dev)

@usercommand
def switch(*dev_pos_list):
    """Move one or more devices to a new position and wait until motion
    of all devices is completed.  Same as `maw()`.

    This can be used with multiple devices like this::

        switch(dev1, pos1, dev2, pos2, ...)
    """
    maw(*dev_pos_list)

@usercommand
def wait(*devlist):
    """Wait until motion of one or more devices is complete, or device is
    out of "busy" status.  A time in seconds can also be used to wait the
    given number of seconds.

    Example::

        wait(T, 60)

    waits for the T device, and then another 60 seconds.
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname],
                                 (Moveable, Measurable))]
    for dev in devlist:
        if isinstance(dev, (int, float, long)):
            sleep(dev)
            continue
        dev = session.getDevice(dev, (Moveable, Measurable))
        dev.log.info('waiting for device')
        value = dev.wait()
        if value:
            dev.log.info('at %20s %s' % (dev.format(value), dev.unit))

@usercommand
def read(*devlist):
    """Read the position (or value) of one or more devices.

    If no device is given, read all readable devices.
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Readable)]
        devlist.sort(key=lambda dev: dev.name)
    for dev in devlist:
        dev = session.getDevice(dev, Readable)
        try:
            value = dev.read()
        except NicosError:
            dev.log.exception('error reading device')
            continue
        unit = dev.unit
        if isinstance(dev, Moveable):
            target = dev.target
            if target != 'unknown' and target != value:
                dev.log.info('at %20s %-5s  (target: %20s %s)' %
                    (dev.format(value), unit, dev.format(target), unit))
            else:
                dev.log.info('at %20s %-5s' % (dev.format(value), unit))
        else:
            dev.log.info('at %20s %-5s' % (dev.format(value), unit))

def _formatStatus(status):
    const, message = status
    const = statuses.get(const, str(const))
    return const + (message and ': ' + message or '')

@usercommand
def status(*devlist):
    """Read the status of one or more devices.

    If no device is given, read the status of all readable devices.
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Readable)]
    for dev in devlist:
        dev = session.getDevice(dev, Readable)
        try:
            status = dev.status()
        except NicosError:
            dev.log.exception('error reading status')
        else:
            dev.log.info('status is %s' % _formatStatus(status))

@usercommand
def stop(*devlist):
    """Stop one or more devices.

    If no device is given, stop all stoppable devices in parallel.
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname],
                                 (Moveable, Measurable))]
        for dev in devlist:
            stopthread = threading.Thread(target=stop, args=(dev,))
            stopthread.setDaemon(True)
            stopthread.start()
    for dev in devlist:
        dev = session.getDevice(dev, (Moveable, Measurable))
        try:
            status = dev.stop()
        except NicosError:
            dev.log.exception('error stopping device')
        else:
            dev.log.info('stopped, status is now %s' % _formatStatus(status))

@usercommand
def reset(*devlist):
    """Reset the given device(s)."""
    for dev in devlist:
        dev = session.getDevice(dev, Readable)
        status = dev.reset()
        dev.log.info('reset done, status is now %s' % _formatStatus(status))

@usercommand
def set(dev, parameter, value):
    """Set a the parameter of the device to a new value."""
    session.getDevice(dev).setPar(parameter, value)
    dev.log.info('%s set to %r' % (parameter, value))

@usercommand
def get(dev, parameter):
    """Return the value of a parameter of the device."""
    value = getattr(session.getDevice(dev), parameter)
    dev.log.info('parameter %s is %s' % (parameter, value))

@usercommand
def fix(dev, reason=''):
    """Fix a device, i.e. prevent movement until `release()` is called.

    You can give a reason that is displayed when movement is attempted.
    Example::

        fix(phi, 'will drive into the wall')
    """
    dev = session.getDevice(dev, Moveable)
    dev.fix(reason)
    dev.log.info(reason and 'now fixed: ' + reason or 'now fixed')

@usercommand
def release(*devlist):
    """Release one or more devices, i.e. undo the effect of `fix()`."""
    if not devlist:
        raise UsageError('at least one device argument is required')
    for dev in devlist:
        dev = session.getDevice(dev, Moveable)
        dev.release()
        dev.log.info('released')

@usercommand
def adjust(dev, value, newvalue=None):
    """Adjust the offset of the device.

    There are two ways to call this function:

    * with one value: the offset is adjusted so that `read()` then returns
      the given value.
    * with two values: the offset is adjusted so that the position that
      previously had the value of the first parameter now has the value of
      the second parameter.

    Examples:

    >>> adjust(om, 100)     # om's current value is now 100
    >>> adjust(om, 99, 100) # what was om = 99 before is now om = 100

    "dev" must be a device that supports the "offset" parameter.
    """
    dev = session.getDevice(dev, HasOffset)
    if newvalue is None:
        diff = dev.read(0) - value
    else:
        diff = value - newvalue
    dev.offset += diff
    dev.log.info('adjusted to %s %s, new offset is %.3f' %
                 (dev.format(value), dev.unit, dev.offset))

@usercommand
def version(*devlist):
    """List version info of the device(s)."""
    for dev in devlist:
        dev = session.getDevice(dev, Device)
        versions = dev.version()
        dev.log.info('relevant versions for this device:')
        printTable(('module/component', 'version'), versions, printinfo)

@usercommand
def history(dev, key='value', fromtime=None, totime=None):
    """Print history of a device parameter.

    The optional argument *key* selects a parameter of the device.  "value" is
    the main value, and "status" is the device status.

    *fromtime* and *totime* are UNIX timestamps, or negative numbers giving
    **hours** in the past.  The default is to list history of the last hour for
    "value" and "status", or from the last day for other parameters.  For
    example:

    >>> history(mth)              # show value of mth in the last hour
    >>> history(mth, -48)         # show value of mth in the last two days
    >>> history(mtt, 'offset')    # show offset of mth in the last day
    """
    # support calling history(dev, -3600)
    if isinstance(key, (int, float)):
        totime = fromtime
        fromtime = key
        key = 'value'
    if key not in ('value', 'status') and fromtime is None:
        fromtime = -24
    if fromtime is not None:
        fromtime *= 3600
    if totime is not None:
        totime *= 3600
    hist = session.getDevice(dev, Device).history(key, fromtime, totime)
    entries = []
    ltime = time.localtime
    ftime = time.strftime
    for t, v in hist:
        entries.append((ftime('%Y-%m-%d %H:%M:%S', ltime(t)), repr(v)))
    printTable(('timestamp', 'value'), entries, printinfo)

@usercommand
def limits(*devlist):
    """Print the limits of the device(s)."""
    for dev in devlist:
        try:
            dev = session.getDevice(dev, HasLimits)
        except UsageError:
            dev.log.warning('device has no limits')
            continue
        dev.log.info('limits for this device:')
        if isinstance(dev, HasOffset):
            printinfo('    absolute limits (physical): %8s --- %8s %s' %
                      (dev.format(dev.absmin), dev.format(dev.absmax),
                       dev.unit))
            printinfo('user limits (including offset): %8s --- %8s %s' %
                      (dev.format(dev.usermin), dev.format(dev.usermax),
                       dev.unit))
            printinfo('                current offset: %8s %s' %
                      (dev.format(dev.offset), dev.unit))
            printinfo('     => user limits (physical): %8s --- %8s %s' %
                      (dev.format(dev.usermin + dev.offset),
                       dev.format(dev.usermax + dev.offset), dev.unit))
        else:
            printinfo('absolute limits: %8s --- %8s %s' %
                      (dev.format(dev.absmin), dev.format(dev.absmax),
                       dev.unit))
            printinfo('    user limits: %8s --- %8s %s' %
                      (dev.format(dev.usermin), dev.format(dev.usermax),
                       dev.unit))

@usercommand
def resetlimits(*devlist):
    """Reset the user limits for the device(s) to the absolute limits."""
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], HasLimits)]
    for dev in devlist:
        try:
            dev = session.getDevice(dev, HasLimits)
        except UsageError:
            dev.log.warning('device has no limits')
            continue
        alim = dev.abslimits
        if isinstance(dev, HasOffset):
            newlim = (alim[0] - dev.offset, alim[1] - dev.offset)
        else:
            newlim = alim
        if dev.userlimits != newlim:
            dev.userlimits = newlim
            dev.log.info('limits reset to absolute limits, new range: %8s --- %8s %s'
                         % (dev.format(dev.userlimits[0]),
                            dev.format(dev.userlimits[1]), dev.unit))

@usercommand
def listparams(dev):
    """List all parameters of the device."""
    dev = session.getDevice(dev, Device)
    dev.log.info('Device parameters:')
    devunit = getattr(dev, 'unit', '')
    items = []
    for name, info in sorted(dev.parameters.iteritems()):
        if not info.userparam:
            continue
        try:
            value = getattr(dev, name)
        except Exception:
            value = '<could not get value>'
        unit = (info.unit or '').replace('main', devunit)
        vstr = repr(value)
        if len(vstr) > 40:
            vstr = vstr[:37] + '...'
        settable = info.settable and 'yes' or 'no'
        name = dev.name + '.' + name
        items.append((name, vstr, unit, settable, info.description))
    printTable(('name', 'value', 'unit', 'r/w?', 'description'),
               items, printinfo)

@usercommand
def listmethods(dev):
    """List user-callable methods for the device."""
    dev = session.getDevice(dev, Device)
    items = []
    listed = __builtin__.set()
    def _list(cls):
        if cls in listed: return
        listed.add(cls)
        for name, (args, doc) in sorted(cls.commands.iteritems()):
            items.append((dev.name + '.' + name + args, cls.__name__, doc))
        for base in cls.__bases__:
            if issubclass(base, Device):
                _list(base)
    _list(dev.__class__)
    dev.log.info('Device methods:')
    printTable(('method', 'from class', 'description'), items, printinfo)

@usercommand
def listallparams(*names):
    """List the given parameters for all existing devices that have them.

    Example::

        listallparams('offset')

    lists the offset for all devices with an "offset" parameter.
    """
    items = []
    for name, dev in session.devices.iteritems():
        pvalues = []
        for param in names:
            if param in dev.parameters:
                pvalues.append(repr(getattr(dev, param)))
            else:
                pvalues.append(None)
        if any(v is not None for v in pvalues):
            items.append([name] + map(str, pvalues))
    printTable(('device',) + names, items, printinfo)

@usercommand
def listdevices():
    """List all currently created devices."""
    printinfo('All created devices:')
    items = []
    for devname in sorted(session.explicit_devices):
        dev = session.devices[devname]
        items.append((dev.name, dev.__class__.__name__, dev.description))
    printTable(('name', 'type', 'description'), items, printinfo)
