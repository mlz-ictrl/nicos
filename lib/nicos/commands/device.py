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

"""Module for simple device-related user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicos import session
from nicos.utils import printTable
from nicos.device import Device, Moveable, Measurable, Readable, \
     HasOffset, HasLimits
from nicos.errors import NicosError, UsageError
from nicos.status import statuses
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

    This can be used with multiple devices like this:
       move(dev1, pos1, dev2, pos2, ...)
    """
    for dev, pos in _devposlist(dev_pos_list, Moveable):
        dev.log.info('moving to', dev.format(pos), dev.unit)
        dev.move(pos)

@usercommand
def drive(*dev_pos_list):
    """Move one or more devices to a new position.  Same as "move".

    This can be used with multiple devices like this:
       drive(dev1, pos1, dev2, pos2, ...)
    """
    return move(*dev_pos_list)

@usercommand
def maw(*dev_pos_list):
    """Move one or more devices to a new position and wait until motion
    of all devices is completed.

    This can be used with multiple devices like this:
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
    of all devices is completed.  Same as "maw".

    This can be used with multiple devices like this:
       switch(dev1, pos1, dev2, pos2, ...)
    """
    maw(*dev_pos_list)

@usercommand
def wait(*devlist):
    """Wait until motion of one or more devices is complete, or device is
    out of "busy" status.  A time in seconds can also be used to wait the
    given number of seconds.

    Example:
        wait(T, 60)
    waits for the T device, and then another 60 seconds.
    """
    if not devlist:
        devlist = [session.devices[devname] for devname in session.explicit_devices
                   if isinstance(session.devices[devname], (Moveable, Measurable))]
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
    """Read the position (or value) of one or more devices, or if no device
    is given, all existing devices.
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
        else:
            dev.log.info('at %20s %s' % (dev.format(value), dev.unit))

def _formatStatus(status):
    const, message = status
    const = statuses.get(const, str(const))
    return const + (message and ': ' + message or '')

@usercommand
def status(*devlist):
    """Read the status of one or more devices, or if no device is given,
    all existing devices.
    """
    if not devlist:
        devlist = [session.devices[devname] for devname in session.explicit_devices
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
    """Stop one or more devices, or if no device is given,
    all startable devices.
    """
    if not devlist:
        devlist = [session.devices[devname] for devname in session.explicit_devices
                   if isinstance(session.devices[devname], (Moveable, Measurable))]
    for dev in devlist:
        dev = session.getDevice(dev, (Moveable, Measurable))
        try:
            dev.stop()
        except NicosError:
            dev.log.exception('error stopping device')
        else:
            dev.log.info('stopped')

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

@usercommand
def get(dev, parameter):
    """Return the value of a parameter of the device."""
    value = getattr(session.getDevice(dev), parameter)
    dev.log.info('parameter %s is %s' % (parameter, value))

@usercommand
def fix(*devlist):
    """Fix one or more devices, i.e. prevent movement until release()."""
    if not devlist:
        raise UsageError('at least one device argument is required')
    for dev in devlist:
        dev = session.getDevice(dev, Moveable)
        dev.fix()
        dev.log.info('fixed')

@usercommand
def release(*devlist):
    """Release one or more devices, i.e. undo the effect of fix()."""
    if not devlist:
        raise UsageError('at least one device argument is required')
    for dev in devlist:
        dev = session.getDevice(dev, Moveable)
        dev.release()
        dev.log.info('released')

@usercommand
def adjust(dev, value):
    """Adjust the offset of the device so that read() returns the given value.
    """
    dev = session.getDevice(dev, HasOffset)
    diff = dev.read() - value
    dev.offset += diff

@usercommand
def version(*devlist):
    """List version info of the device(s)."""
    for dev in devlist:
        dev = session.getDevice(dev, Device)
        versions = dev.version()
        dev.log.info('Relevant versions for this device:')
        printTable(('module/component', 'version'), versions, printinfo)

@usercommand
def limits(*devlist):
    """Print the limits of the device."""
    for dev in devlist:
        dev = session.getDevice(dev, HasLimits)
        dev.log.info('Limits for this device:')
        printinfo('absolute minimum: %s %s' % (dev.format(dev.absmin), dev.unit))
        printinfo('    user minimum: %s %s' % (dev.format(dev.usermin), dev.unit))
        printinfo('    user maximum: %s %s' % (dev.format(dev.usermax), dev.unit))
        printinfo('absolute maximum: %s %s' % (dev.format(dev.absmax), dev.unit))

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
        items.append((name, vstr, unit, settable, info.description))
    printTable(('name', 'value', 'unit', 'r/w?', 'description'),
               items, printinfo)

@usercommand
def listmethods(dev):
    """List user-callable methods for the device."""
    dev = session.getDevice(dev, Device)
    items = []
    def _list(cls):
        for name, (args, doc) in sorted(cls.commands.iteritems()):
            items.append((name + args, cls.__name__, doc))
        for base in cls.__bases__:
            if issubclass(base, Device):
                _list(base)
    _list(dev.__class__)
    dev.log.info('Device methods:')
    printTable(('method', 'from class', 'description'), items, printinfo)

@usercommand
def ListDevices():
    """List all currently created devices."""
    printinfo('All created devices:')
    items = []
    for devname in sorted(session.explicit_devices):
        dev = session.devices[devname]
        items.append((dev.name, dev.__class__.__name__, dev.description))
    printTable(('name', 'type', 'description'), items, printinfo)
