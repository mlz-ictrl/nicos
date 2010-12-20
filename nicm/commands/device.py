#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS device-related user commands
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

"""Module for simple device-related user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicm import nicos
from nicm.utils import printTable
from nicm.device import Device, Startable, Moveable, Readable, HasOffset
from nicm.errors import NicmError, UsageError
from nicm.status import statuses
from nicm.commands import usercommand
from nicm.commands.output import printinfo


def _devposlist(dev_pos_list, cls):
    devlist = []
    poslist = []
    if len(dev_pos_list) == 0:
        raise UsageError('at least one device and position must be given')
    if len(dev_pos_list) % 2 != 0:
        raise UsageError('a position must be given for every device')
    for i in range(len(dev_pos_list)):
        if i % 2 == 0:
            devlist.append(nicos.getDevice(dev_pos_list[i], cls))
            poslist.append(dev_pos_list[i+1])
    return zip(devlist, poslist)

@usercommand
def move(*dev_pos_list):
    """Move one or more devices to a new position.

    This can be used with multiple devices like this:
       move(dev1, pos1, dev2, pos2, ...)
    """
    for dev, pos in _devposlist(dev_pos_list, Moveable):
        dev.printinfo('moving to', dev.format(pos), dev.unit)
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
        dev.printinfo('moving to', dev.format(pos), dev.unit)
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
    out of "busy" status.
    """
    if not devlist:
        devlist = [nicos.devices[devname] for devname in nicos.explicit_devices
                   if isinstance(nicos.devices[devname], Startable)]
    for dev in devlist:
        dev = nicos.getDevice(dev, Startable)
        dev.printinfo('waiting for device')
        value = dev.wait()
        if value:
            dev.printinfo('at %20s %s' % (dev.format(value), dev.unit))

@usercommand
def read(*devlist):
    """Read the position (or value) of one or more devices, or if no device
    is given, all existing devices.
    """
    if not devlist:
        devlist = [nicos.devices[devname] for devname in nicos.explicit_devices
                   if isinstance(nicos.devices[devname], Readable)]
    for dev in devlist:
        dev = nicos.getDevice(dev, Readable)
        try:
            value = dev.read()
        except NicmError:
            dev.printexception('error reading device')
        else:
            dev.printinfo('at %20s %s' % (dev.format(value), dev.unit))

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
        devlist = [nicos.devices[devname] for devname in nicos.explicit_devices
                   if isinstance(nicos.devices[devname], Readable)]
    for dev in devlist:
        dev = nicos.getDevice(dev, Readable)
        try:
            status = dev.status()
        except NicmError:
            dev.printexception('error reading status')
        else:
            dev.printinfo('status is %s' % _formatStatus(status))

@usercommand
def stop(*devlist):
    """Stop one or more devices, or if no device is given,
    all startable devices.
    """
    if not devlist:
        devlist = [nicos.devices[devname] for devname in nicos.explicit_devices
                   if isinstance(nicos.devices[devname], Startable)]
    for dev in devlist:
        dev = nicos.getDevice(dev, Startable)
        try:
            dev.stop()
        except NicmError:
            dev.printexception('error stopping device')
        else:
            dev.printinfo('stopped')

@usercommand
def reset(dev):
    """Reset the given device."""
    dev = nicos.getDevice(dev, Readable)
    status = dev.reset()
    dev.printinfo('reset done, status is now %s' % _formatStatus(status))

@usercommand
def set(dev, parameter, value):
    """Set a the parameter of the device to a new value."""
    nicos.getDevice(dev).setPar(parameter, value)

@usercommand
def get(dev, parameter):
    """Return the value of a parameter of the device."""
    value = nicos.getDevice(dev).getPar(parameter)
    dev.printinfo('parameter %s is %s' % (parameter, value))

@usercommand
def fix(*devlist):
    """Fix one or more devices, i.e. prevent movement until release()."""
    if not devlist:
        raise UsageError('at least one device argument is required')
    for dev in devlist:
        dev = nicos.getDevice(dev, Startable)
        dev.fix()
        dev.printinfo('fixed')

@usercommand
def release(*devlist):
    """Release one or more devices, i.e. undo the effect of fix()."""
    if not devlist:
        raise UsageError('at least one device argument is required')
    for dev in devlist:
        dev = nicos.getDevice(dev, Startable)
        dev.release()
        dev.printinfo('released')

@usercommand
def adjust(dev, value):
    """Adjust the offset of the device so that read() returns the given value.
    """
    dev = nicos.getDevice(dev, HasOffset)
    diff = dev.read() - value
    dev.offset += diff

@usercommand
def version(dev):
    """List version info of the device."""
    dev = nicos.getDevice(dev, Device)
    versions = dev.version()
    dev.printinfo('Relevant versions for this device:')
    printTable(('module/component', 'version'), versions, printinfo)

@usercommand
def listparams(dev):
    """List all parameters of the device."""
    dev = nicos.getDevice(dev, Device)
    dev.printinfo('Parameters of this device:')
    items = []
    for name, info in sorted(dev.parameters.iteritems()):
        try:
            value = dev.getPar(name)
        except Exception:
            value = '<could not get value>'
        unit = (info.unit or '').replace('main', dev.unit)
        items.append((name, str(value), unit, info.description))
    printTable(('name', 'value', 'unit', 'description'), items, printinfo)

@usercommand
def listdevices():
    """List all currently created devices."""
    printinfo('All created devices:')
    items = []
    for devname in sorted(nicos.explicit_devices):
        dev = nicos.devices[devname]
        items.append((dev.name, dev.__class__.__name__, dev.description))
    printTable(('name', 'type', 'description'), items, printinfo)
