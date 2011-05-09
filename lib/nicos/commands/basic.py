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

from __future__ import with_statement

"""Module for basic user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import time
import shutil
import inspect
import __builtin__
from os import path

from nicos import session
from nicos.utils import formatDocstring, formatDuration, printTable
from nicos.device import Device, AutoDevice, Readable
from nicos.errors import ModeError, NicosError, UsageError
from nicos.notify import Mailer, SMSer
from nicos.sessions import EXECUTIONMODES
from nicos.commands import usercommand
from nicos.commands.output import printinfo, printexception, printwarning


# -- help and introspection ----------------------------------------------------

@usercommand
def help(obj=None):
    """Show help for a command or other object."""
    if obj is None:
        listcommands()
    elif isinstance(obj, Device):
        printinfo('%s is a device of class %s.' % (obj.getPar('name'),
                                                   obj.__class__.__name__))
        printinfo('Its description is: %s.' % obj.getPar('description'))
    elif not inspect.isfunction(obj):
        __builtin__.help(obj)
    else:
        # for functions, print arguments and docstring
        real_func = getattr(obj, 'real_func', obj)
        argspec = inspect.formatargspec(*inspect.getargspec(real_func))
        printinfo('Usage: ' + real_func.__name__ + argspec)
        printinfo(formatDocstring(real_func.__doc__ or '', '   '))

__builtin__.__orig_dir = dir

@usercommand
def dir(obj=None):
    """Show all public attributes for the given object."""
    if obj is None:
        return __builtin__.__orig_dir()
    return [name for name in __builtin__.__orig_dir(obj)
            if not name.startswith(('_', 'do'))]

@usercommand
def listcommands():
    """List all available commands."""
    printinfo('Available commands:')
    items = []
    for obj in session.getExportedObjects():
        if hasattr(obj, 'is_usercommand'):
            real_func = getattr(obj, 'real_func', obj)
            argspec = inspect.formatargspec(*inspect.getargspec(real_func))
            docstring = real_func.__doc__ or ' '
            if not real_func.__name__.startswith('_'):
                items.append((real_func.__name__ + argspec,
                              docstring.splitlines()[0]))
    items.sort()
    printTable(('name', 'description'), items, printinfo)

@usercommand
def sleep(secs):
    """Sleep for a given number of seconds."""
    time.sleep(secs)   # XXX make this an interruptible sleep?


# -- other basic commands ------------------------------------------------------

@usercommand
def NewSetup(setupname):
    """Load the given setup instead of the current one."""
    current_mode = session.mode
    # refresh setup files first
    session.readSetups()
    session.unloadSetup()
    try:
        session.startMultiCreate()
        try:
            session.loadSetup(setupname)
        finally:
            session.endMultiCreate()
    except Exception:
        printexception()
        session.loadSetup('startup')
    if current_mode == 'master':
        # need to refresh master status
        SetMode('master')

@usercommand
def AddSetup(setupname):
    """Load the given setup additional to the current one."""
    session.readSetups()
    session.startMultiCreate()
    try:
        session.loadSetup(setupname)
    finally:
        session.endMultiCreate()

@usercommand
def ListSetups():
    """Print a list of all known setups."""
    printinfo('Available setups:')
    items = []
    for name, info in session.getSetupInfo().iteritems():
        if info['group'] == 'special':
            continue
        items.append((name, info['name'], ', '.join(sorted(info['devices']))))
    items.sort()
    printTable(('name', 'description', 'devices'), items, printinfo)

@usercommand
def Keep(name, object):
    """Export the given object into the NICOS namespace."""
    session.export(name, object)

@usercommand
def CreateDevice(*devnames):
    """Create all given devices."""
    for devname in devnames:
        session.createDevice(devname, explicit=True)

@usercommand
def DestroyDevice(*devnames):
    """Destroy all given devices."""
    for devname in devnames:
        if isinstance(devname, Device):
            devname = devname.name
        session.destroyDevice(devname)

@usercommand
def CreateAllDevices():
    """Create all devices in the current setup that are not marked as
    lowlevel devices.
    """
    session.startMultiCreate()
    try:
        for devname, (_, devconfig) in session.configured_devices.iteritems():
            if devconfig.get('lowlevel', False):
                continue
            try:
                session.createDevice(devname, explicit=True)
            except NicosError, err:
                printexception('error creating %s' % devname)
    finally:
        session.endMultiCreate()

@usercommand
def NewExperiment(proposal, title='', **kwds):
    """Start a new experiment with the given proposal number and title."""
    session.experiment.new(proposal, title, **kwds)

@usercommand
def AddUser(name, email, affiliation=None):
    """Add a new user to the experiment."""
    session.experiment.addUser(name, email, affiliation)

@usercommand
def NewSample(name):
    """Start a new sample with the given sample name."""
    session.experiment.sample.samplename = name

@usercommand
def Remark(remark):
    """Change the remark about instrument configuration saved to the
    data files.
    """
    session.experiment.remark = remark

@usercommand
def SetMode(mode):
    """Set the execution mode.

    Valid modes are: """
    try:
        session.setMode(mode)
    except ModeError:
        printexception()

SetMode.__doc__ += ', '.join(EXECUTIONMODES)


@usercommand
def ClearCache(devname):
    """Clear all local cached information for a given device."""
    if isinstance(devname, Device):
        devname = devname.name
    session.cache.clear(devname)
    printinfo('cleared cached information for %s' % devname)


class _Scope(object):
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        session.beginActionScope(self.name)
    def __exit__(self, *args):
        session.endActionScope()

@usercommand
def UserInfo(name):
    """Return an object that can be used like this:

    with UserInfo('Qscan around (1,1,0)'):
        qscan(...)
    """
    return _Scope(name)


@usercommand
def Run(filename):
    """Run a script file given by file name.  If the file name is not absolute,
    it is relative to the experiment script directory.
    """
    fn = path.normpath(path.join(session.experiment.scriptdir, filename))
    if not path.isfile(fn) and os.access(fn, os.R_OK):
        raise UsageError('The file %r does not exist or is not readable' % fn)
    starttime = session.clock.time
    printinfo('running user script: ' + fn)
    with open(fn, 'r') as fp:
        code = unicode(fp.read(), 'utf-8')
        with _Scope(fn):
            exec code in session.getLocalNamespace(), session.getNamespace()
    printinfo('finished user script: ' + fn)
    if session.mode == 'simulation':
        printinfo('simulated minimum runtime: ' +
                  formatDuration(session.clock.time - starttime))
    # XXX add device minimum/maximum values


@usercommand
def Notify(*args):
    """Send a message via email and/or SMS to the receivers selected by
    SetMailReceivers and SetSMSReceivers.  Usage is one of these two:

        Notify('some text')
        Notify('subject', 'some text')
    """
    if len(args) == 1:
        # use first line of text as subject
        text, = args
        session.notify(text.splitlines()[0], text)
    elif len(args) == 2:
        subject, text = args
        session.notify(subject, text)
    else:
        raise TypeError("Usage: Notify('text') or Notify('subject', 'text')")


@usercommand
def SetMailReceivers(*emails):
    """Set a list of email addresses that will be notified on unhandled errors,
    and when the Notify() command is used.
    """
    for notifier in session.notifiers:
        if isinstance(notifier, Mailer):
            notifier.receivers = list(emails)
            if emails:
                printinfo('mails will now be sent to ' + ', '.join(emails))
            else:
                printinfo('no email notifications will be sent')
            return
    printwarning('email notification is not configured in this setup')


@usercommand
def SetSMSReceivers(*numbers):
    """Set a list of mobile phone numbers that will be notified on unhandled
    errors, and when the Notify() command is used.

    Note that all those phone numbers have to be registered with the IT
    department before they can be used.
    """
    for notifier in session.notifiers:
        if isinstance(notifier, SMSer):
            notifier.receivers = list(numbers)
            if numbers:
                printinfo('SMS will now be sent to ' + ', '.join(numbers))
            else:
                printinfo('no SMS notifications will be sent')
            return
    printwarning('SMS notification is not configured in this setup')


@usercommand
def SaveSimulationSetup(filename, name=None):
    """Save the whole current setup as a file usable in simulation mode."""
    if path.isfile(filename):
        printwarning('The file %r already exists, making a backup at %r' %
                     (filename, filename + '.bak'))
        shutil.copy(filename, filename + '.bak')
    with open(filename, 'w') as f:
        f.write('name = %r\n\n' % (name or '+'.join(session.explicit_setups)))
        f.write('group = %r\n\n' % 'simulated')
        f.write('sysconfig = dict(\n')
        f.write('    instrument = %r,\n' % session.instrument.name)
        f.write('    experiment = %r,\n' % session.experiment.name)
        f.write('    datasinks = %r,\n' % [s.name for s in session.datasinks])
        f.write(')\n\n')
        f.write('devices = dict(\n')
        for devname, dev in session.devices.iteritems():
            if isinstance(dev, AutoDevice):
                continue
            devcls = dev.__class__.__module__ + '.' + dev.__class__.__name__
            f.write('    %s = device(%r,\n' % (devname, devcls))
            for adevname in dev.attached_devices:
                adev = dev._adevs[adevname]
                if isinstance(adev, list):
                    f.write('        %s = %r,\n' % (
                        adevname, [sdev.name for sdev in adev]))
                else:
                    f.write('        %s = %r,\n' % (
                        adevname, adev and str(adev) or None))
            for param in dev.parameters:
                f.write('        %s = %r,\n' % (param, getattr(dev, param)))
            f.write('    ),\n')
        f.write(')\n\n')
        f.write('startupcode = """\n')
        for dev in session.devices.itervalues():
            if isinstance(dev, Readable) and dev.hardware_access:
                f.write('_SimulationRestore(%r, %r)\n' %
                        (dev.name, dev._sim_value))
        f.write('"""\n')

@usercommand
def _SimulationRestore(devname, value):
    """Restore value of a device in a simulation setup.

    This needs to be a usercommand because it is executed in the user namespace,
    but by prefixing the name with an underscore it is hidden from the user.
    """
    printinfo('Setting simulated value of device %s to %r' % (devname, value))
    session.getDevice(devname)._sim_value = value
