#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

import time

from nicos import session, nicos_version, __version__ as nicos_revision
from nicos.utils import printTable, parseDateString, createThread
from nicos.core import Device, Moveable, Waitable, Measurable, Readable, \
    HasOffset, HasLimits, UsageError, AccessError, formatStatus, \
    INFO_CATEGORIES, multiWait
from nicos.core.status import OK, BUSY
from nicos.core.spm import spmsyntax, AnyDev, Dev, Bare, String, DevParam, Multi
from nicos.devices.abstract import CanReference
from nicos.commands import usercommand, hiddenusercommand, helparglist
from nicos.commands.basic import sleep
from nicos.commands.output import printinfo, printerror
from nicos.pycompat import builtins, itervalues, iteritems, number_types, \
    string_types


__all__ = [
    'move', 'drive', 'maw', 'switch', 'wait', 'read', 'status', 'stop',
    'reset', 'set', 'get', 'getall', 'setall', 'info', 'fix', 'release',
    'unfix', 'adjust', 'version', 'history', 'limits', 'resetlimits',
    'reference', 'ListParams', 'ListMethods', 'ListDevices',
]


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
@helparglist('dev, pos, ...')
@spmsyntax(Multi(Dev(Moveable), Bare))
def move(*dev_pos_list):
    """Start moving one or more devices to a new position.

    This can be used with multiple devices.  Examples:

    >>> move(dev, pos)                 # start one device
    >>> move(dev1, pos1, dev2, pos2)   # start two devices in parallel
    ...
    >>> wait(dev, dev1, dev2)          # now wait for all of them
    """
    for dev, pos in _devposlist(dev_pos_list, Moveable):
        dev.log.info('moving to', dev.format(pos, unit=True))
        dev.move(pos)


@hiddenusercommand
@helparglist('dev, pos, ...')
@spmsyntax(Multi(Dev(Moveable), Bare))
def drive(*dev_pos_list):
    """Move one or more devices to a new position.  Same as `move()`."""
    return move(*dev_pos_list)


@usercommand
@helparglist('dev, pos, ...')
@spmsyntax(Multi(Dev(Moveable), Bare))
def maw(*dev_pos_list):
    """Move one or more devices to a new position and wait for them.

    The command does not return until motion of all devices is completed.  It
    can be used with multiple devices.  Examples:

    >>> maw(dev, pos)                  # move a device to a new position
    >>> maw(dev1, pos1, dev2, pos2)    # move two devices in parallel
    """
    devs = []
    for dev, pos in _devposlist(dev_pos_list, Moveable):
        dev.log.info('moving to', dev.format(pos, unit=True))
        dev.move(pos)
        devs.append(dev)
    values = multiWait(devs)
    for dev in devs:
        dev.log.info('at %20s %s' % (dev.format(values[dev]), dev.unit))


@hiddenusercommand
@helparglist('dev, pos, ...')
@spmsyntax(Multi(Dev(Moveable), Bare))
def switch(*dev_pos_list):
    """Move one or more devices to a new position and wait until motion
    of all devices is completed.  Same as `maw()`."""
    maw(*dev_pos_list)


@usercommand
@helparglist('dev, ...')
@spmsyntax(Multi(Dev(Waitable)))
def wait(*devlist):
    """Wait until motion/action of one or more devices is complete.

    Usually, "wait" returns when the device is out of "busy" status.  A time in
    seconds can also be used to wait the given number of seconds.

    Examples:

    >>> wait(T, B)    # wait for T and B devices
    >>> wait(T, 60)   # wait for T device, and then another 60 seconds
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Waitable)]
    for dev in devlist:
        if isinstance(dev, number_types):
            sleep(dev)
            continue
        dev = session.getDevice(dev, Waitable)
        dev.log.info('waiting for device')
        try:
            value = dev.wait()
        except Exception:
            dev.log.exception('error waiting for device')
            continue
        if value is not None:
            dev.log.info('at %20s %s' % (dev.format(value), dev.unit))


@usercommand
@helparglist('[dev, ...]')
@spmsyntax(Multi(Dev(Readable)))
def read(*devlist):
    """Read the position (or value) of one or more devices.

    If no device is given, read all readable devices.

    Examples:

    >>> read()        # read all devices
    >>> read(T)       # read the T device
    >>> read(T, B)    # read the T and B devices
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Readable)]
        devlist.sort(key=lambda dev: dev.name.lower())
    for dev in devlist:
        try:
            dev = session.getDevice(dev, Readable)
        except UsageError as err:
            err.args = (err.args[0] + ', try info(%s)' % dev,)
            raise
        try:
            value = dev.read()
        except Exception:
            dev.log.exception('error reading device')
            continue
        unit = dev.unit
        if isinstance(dev, Moveable):
            target = dev.target
            if target is not None and dev.format(target) != dev.format(value):
                dev.log.info('at %20s %-5s  (target: %20s %s)' %
                             (dev.format(value), unit, dev.format(target), unit))
            else:
                dev.log.info('at %20s %-5s' % (dev.format(value), unit))
        else:
            dev.log.info('at %20s %-5s' % (dev.format(value), unit))


@usercommand
@helparglist('[dev, ...]')
@spmsyntax(Multi(Dev(Readable)))
def status(*devlist):
    """Read the status of one or more devices.

    If no device is given, read the status of all readable devices.

    Examples:

    >>> status()        # display status of all devices
    >>> status(T)       # status of the T device
    >>> status(T, B)    # status of the T and B devices
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Readable)]
        devlist.sort(key=lambda dev: dev.name.lower())
    for dev in devlist:
        dev = session.getDevice(dev, Readable)
        try:
            status = dev.status()
        except Exception:
            dev.log.exception('error reading status')
        else:
            if status[0] in (OK, BUSY):
                dev.log.info('status is %s' % formatStatus(status))
            else:
                dev.log.warning('status is %s' % formatStatus(status))


@usercommand
@helparglist('[dev, ...]')
@spmsyntax(Multi(Dev((Moveable, Measurable))))
def stop(*devlist):
    """Stop one or more devices.

    If no device is given, stop all stoppable devices in parallel.

    Examples:

    >>> stop(phi)       # stop the phi device
    >>> stop(phi, psi)  # stop the phi and psi devices
    >>> stop()          # stop all devices
    """
    stop_all = False
    if not devlist:
        stop_all = True
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname],
                                 (Moveable, Measurable))]
    finished = []

    def stopdev(dev):
        try:
            dev.stop()
            if not stop_all:
                dev.log.info('stopped')
        except AccessError:
            # do not warn about devices we cannot access if they were not
            # explicitly selected
            pass
        except Exception:
            dev.log.warning('error while stopping', exc=1)
        finally:
            finished.append(dev)
    for dev in devlist:
        createThread('device stopper %s' % dev, stopdev, (dev,))
    while len(finished) != len(devlist):
        time.sleep(Device._base_loop_delay)
    if stop_all:
        printinfo('all devices stopped')
    return


@usercommand
@helparglist('dev, ...')
@spmsyntax(Multi(Dev(Readable)))
def reset(*devlist):
    """Reset the given device(s).

    This can restore communication with the device, re-set a positioning fault
    or make a reference drive (only for devices where this cannot lead to
    crashes, such as slits).

    Examples:

    >>> reset(ss1)        # reset a single device
    >>> reset(ss1, ss2)   # reset multiple devices
    """
    for dev in devlist:
        dev = session.getDevice(dev, Readable)
        status = dev.reset()
        dev.log.info('reset done, status is now %s' % formatStatus(status))


@usercommand
@spmsyntax(AnyDev, DevParam, Bare)
def set(dev, parameter, value):  # pylint: disable=W0622
    """Set a the parameter of the device to a new value.

    The following commands are equivalent:

    >>> set(phi, 'speed', 50)

    >>> phi.speed = 50
    """
    dev = session.getDevice(dev)
    prevalue = getattr(dev, parameter)
    setattr(dev, parameter, value)
    if not dev.parameters[parameter].chatty:  # if yes, we already got a message
        dev.log.info('%s set to %r (was %r)' %
                     (parameter, getattr(dev, parameter), prevalue))


@usercommand
@spmsyntax(AnyDev, DevParam)
def get(dev, parameter):
    """Return the value of a parameter of the device.

    A parameter value can also be read using attribute syntax,
    i.e. ``dev.param``.

    Examples:

    >>> get(phi, 'speed')
    >>> print phi.speed
    """
    value = getattr(session.getDevice(dev), parameter)
    dev.log.info('parameter %s is %s' % (parameter, value))


@usercommand
@helparglist('parameter, ...')
@spmsyntax(Multi(String))
def getall(*names):
    """List the given parameters for all existing devices that have them.

    Example:

    >>> getall('offset')

    lists the offset for all devices with an "offset" parameter.
    """
    items = []
    for name, dev in sorted(iteritems(session.devices),
                            key=lambda nd: nd[0].lower()):
        pvalues = []
        for param in names:
            if param in dev.parameters:
                pvalues.append(repr(getattr(dev, param)))
            else:
                pvalues.append(None)
        if any(v is not None for v in pvalues):
            items.append([name] + list(map(str, pvalues)))
    printTable(('device',) + names, items, printinfo)


@usercommand
@spmsyntax(String, Bare)
def setall(param, value):
    """Set the given parameter to the given value for all devices that have it.

    Example:

    >>> setall('offset', 0)

    set the offset for all devices to zero.
    """
    for dev in itervalues(session.devices):
        if param not in dev.parameters:
            continue
        prevalue = getattr(dev, param)
        setattr(dev, param, value)
        dev.log.info('%s set to %r (was %r)' % (param, value, prevalue))


@usercommand
@helparglist('[dev, ...]')
@spmsyntax(Multi(AnyDev))
def info(*devlist):
    """Print general information of the given device or all devices.

    Information is the device value, status and any other parameters that are
    marked as "interesting" by giving them a category.

    Examples:

    >>> info()           # show all information
    >>> info(Sample)     # show information relevant to the Sample object
    """
    if not devlist:
        devlist = [dev for dev in itervalues(session.devices)
                   if not dev.lowlevel]
    bycategory = {}
    for dev in devlist:
        for category, key, value in dev.info():
            bycategory.setdefault(category, []).append(
                (str(dev), key + ':', value))
    for catname, catinfo in INFO_CATEGORIES:
        if catname not in bycategory:
            continue
        printinfo(catinfo)
        printinfo('=' * len(catinfo))
        printTable(None, sorted(bycategory[catname]), printinfo, minlen=8)
        printinfo()


@usercommand
@helparglist('dev[, reason]')
@spmsyntax(Dev(Moveable), reason=String)
def fix(dev, reason=''):
    """Fix a device, i.e. prevent movement until `release()` is called.

    You can give a reason that is displayed when movement is attempted.
    Example:

    >>> fix(phi, 'will drive into the wall')
    """
    dev = session.getDevice(dev, Moveable)
    if dev.fix(reason):
        dev.log.info(reason and 'now fixed: ' + reason or 'now fixed')


@usercommand
@helparglist('dev, ...')
@spmsyntax(Multi(Dev(Moveable)))
def release(*devlist):
    """Release one or more devices, i.e. undo the effect of `fix()`.

    Example:

    >>> release(phi)
    """
    if not devlist:
        raise UsageError('at least one device argument is required')
    for dev in devlist:
        dev = session.getDevice(dev, Moveable)
        if dev.release():
            dev.log.info('released')


@hiddenusercommand
@helparglist('dev, ...')
@spmsyntax(Multi(Dev(Moveable)))
def unfix(*devlist):
    """Same as `release()`."""
    return release(*devlist)


@usercommand
@helparglist('dev, value[, newvalue]')
@spmsyntax(Dev(HasOffset), Bare)
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
    dev.log.info('adjusted to %s, new offset is %.3f' %
                 (dev.format(value, unit=True), dev.offset))


@usercommand
@helparglist('dev, ...')
@spmsyntax(Multi(AnyDev))
def version(*devlist):
    """List version info of the device(s).
    If no device is given, the version of nicos-core is printed."""
    if devlist:
        for dev in devlist:
            dev = session.getDevice(dev, Device)
            versions = dev.version()
            dev.log.info('relevant versions for this device:')
            printTable(('module/component', 'version'), versions, printinfo)
    else:
        printinfo('NICOS version: %s (rev %s)' %
                  (nicos_version, nicos_revision))


@usercommand
@helparglist('dev[, key][, fromtime]')
@spmsyntax(AnyDev, String)
def history(dev, key='value', fromtime=None, totime=None):
    """Print history of a device parameter.

    The optional argument *key* selects a parameter of the device.  "value" is
    the main value, and "status" is the device status.

    *fromtime* and *totime* are eithernumbers giving **hours** in the past, or
    otherwise strings with a time specification (see below).  The default is to
    list history of the last hour for "value" and "status", or from the last day
    for other parameters.  For example:

    >>> history(mth)              # show value of mth in the last hour
    >>> history(mth, 48)          # show value of mth in the last two days
    >>> history(mtt, 'offset')    # show offset of mth in the last day

    Examples for time specification:

    >>> history(mth, '1 day')                  # allowed: d/day/days
    >>> history(mth, 'offset', '1 week')       # allowed: w/week/weeks
    >>> history(mth, 'speed', '30 minutes')    # allowed: m/min/minutes

    >>> history(mth, 'speed', '2012-05-04 14:00')    # from that date/time on
    >>> history(mth, 'speed', '14:00', '17:00')      # between 14h and 17h today
    >>> history(mth, 'speed', '2012-05-04', '2012-05-08')  # between two days
    """
    # support calling history(dev, -3600)
    if isinstance(key, string_types):
        try:
            key = parseDateString(key)
        except ValueError:
            pass
    if isinstance(key, number_types):
        totime = fromtime
        fromtime = key
        key = 'value'
    if key not in ('value', 'status') and fromtime is None:
        fromtime = -24
    # Device.history() accepts number of hours only when negative (anything
    # > 10000 is taken to be a Unix timestamp)
    if isinstance(fromtime, number_types) and 0 < fromtime < 10000:
        fromtime = -fromtime
    if isinstance(totime, number_types) and 0 < totime < 10000:
        totime = -totime
    # history() already accepts strings as fromtime and totime arguments
    hist = session.getDevice(dev, Device).history(key, fromtime, totime)
    entries = []
    ltime = time.localtime
    ftime = time.strftime
    for t, v in hist:
        entries.append((ftime('%Y-%m-%d %H:%M:%S', ltime(t)), repr(v)))
    printTable(('timestamp', 'value'), entries, printinfo)


@usercommand
@helparglist('[dev, ...]')
@spmsyntax(Multi(Dev(HasLimits)))
def limits(*devlist):
    """Print the limits of the device(s), or all devices if none are given.

    These are the absolute limits (``dev.abslimits``) and user limits
    (``dev.userlimits``).  The absolute limits cannot be set by the user and
    the user limits obviously cannot go beyond them.

    Example:

    >>> limits(phi)    # shows the absolute and user limits of phi

    To set userlimits, use one of these commands:

    >>> phi.userlimits = (low, high)
    >>> set(phi, 'userlimits', (low, high))

    To reset the userlimits to the maximum allowed range (given by the
    abslimits parameter), use:

    >>> resetlimits(phi)
    """
    if not devlist:
        devlist = [session.devices[dev] for dev in session.explicit_devices
                   if isinstance(session.devices[dev], HasLimits)]
    for dev in devlist:
        try:
            dev = session.getDevice(dev, HasLimits)
        except UsageError:
            dev.log.warning('device has no limits')
            continue
        dev.log.info('limits for this device:')
        if isinstance(dev, HasOffset):
            printinfo('       absolute limits (physical): %8s --- %8s %s' %
                      (dev.format(dev.absmin), dev.format(dev.absmax),
                       dev.unit))
            printinfo('   user limits (including offset): %8s --- %8s %s' %
                      (dev.format(dev.usermin), dev.format(dev.usermax),
                       dev.unit))
            printinfo('                current offset: %8s %s' %
                      (dev.format(dev.offset), dev.unit))
            printinfo('        => user limits (physical): %8s --- %8s %s' %
                      (dev.format(dev.usermin + dev.offset),
                       dev.format(dev.usermax + dev.offset), dev.unit))
        else:
            printinfo('   absolute limits: %8s --- %8s %s' %
                      (dev.format(dev.absmin), dev.format(dev.absmax),
                       dev.unit))
            printinfo('       user limits: %8s --- %8s %s' %
                      (dev.format(dev.usermin), dev.format(dev.usermax),
                       dev.unit))


@usercommand
@helparglist('dev, ...')
@spmsyntax(Multi(Dev(HasLimits)))
def resetlimits(*devlist):
    """Reset the user limits for the device(s) to the allowed maximum range.

    The following commands are **not** necessarily equivalent:

    >>> resetlimits(phi)

    >>> phi.userlimits = phi.abslimits

    because the user limits are given in terms of the "logical" value, i.e.
    taking the device's offset into account, while the absolute limits are
    given in terms of the "physical" value.
    """
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
@spmsyntax(Dev(CanReference))
def reference(dev, *args):
    """Do a reference drive of the device, if possible.

    How the reference drive is done depends on the device settings.
    Example:

    >>> reference(phi)
    """
    try:
        dev = session.getDevice(dev, CanReference)
    except UsageError:
        printerror('%s has no reference function' % dev)
        return
    newpos = dev.reference(*args)
    dev.log.info('reference drive complete, position is now ' +
                 dev.format(newpos, unit=True))


@usercommand
@spmsyntax(AnyDev)
def ListParams(dev):
    """List all parameters of the device.

    Example:

    >>> ListParams(phi)
    """
    dev = session.getDevice(dev, Device)
    dev.log.info('Device parameters:')
    items = []
    aliasdev = getattr(dev, 'alias', None)
    if aliasdev is not None:
        aliasdev = session.getDevice(aliasdev, Device)
        items.append((dev.name + '.alias',
                      '-> ' + aliasdev.name, '', 'yes', 'string',
                      'Aliased device, parameters of that device follow'))
        dev = aliasdev
    devunit = getattr(dev, 'unit', '')
    for name, info in sorted(iteritems(dev.parameters)):
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
        if isinstance(info.type, type):
            ptype = info.type.__name__
        else:
            ptype = info.type.__doc__ or '?'
        items.append((name, vstr, unit, settable, ptype, info.description))
    printTable(('name', 'value', 'unit', 'r/w?', 'value type', 'description'),
               items, printinfo)


@usercommand
@spmsyntax(AnyDev)
def ListMethods(dev):
    """List user-callable methods for the device.

    Example:

    >>> ListMethods(phi)
    """
    dev = session.getDevice(dev, Device)
    items = []
    listed = builtins.set()

    def _list(cls):
        if cls in listed:
            return
        listed.add(cls)
        for name, (args, doc, mcls, is_user) in sorted(iteritems(cls.methods)):
            if cls is mcls and is_user:
                items.append((dev.name + '.' + name + args, cls.__name__, doc))
        for base in cls.__bases__:
            if issubclass(base, Device):
                _list(base)
    _list(dev.__class__)
    dev.log.info('Device methods:')
    printTable(('method', 'from class', 'description'), items, printinfo)


@usercommand
@spmsyntax()
def ListDevices():
    """List all currently created devices.

    Example:

    >>> ListDevices()
    """
    printinfo('All created devices:')
    items = []
    for devname in sorted(session.explicit_devices, key=lambda d: d.lower()):
        dev = session.devices[devname]
        items.append((dev.name, dev.__class__.__name__, dev.description))
    printTable(('name', 'type', 'description'), items, printinfo)
