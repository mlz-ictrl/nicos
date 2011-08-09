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

"""Module for basic user commands."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import time
import shutil
import inspect
import traceback
import __builtin__
from os import path

from nicos import session
from nicos.utils import formatDocstring, formatDuration, printTable
from nicos.device import Device, AutoDevice, Readable
from nicos.errors import ModeError, NicosError, UsageError
from nicos.notify import Mailer, SMSer
from nicos.sessions import EXECUTIONMODES
from nicos.commands import usercommand
from nicos.commands.output import printinfo, printwarning, printerror, \
     printexception

CO_DIVISION = 0x2000


# -- help and introspection ----------------------------------------------------

@usercommand
def help(obj=None):
    """Show help for a command or other object."""
    if obj is None:
        listcommands()
    elif isinstance(obj, Device):
        printinfo('%s is a device of class %s.' %
                  (obj.name, obj.__class__.__name__))
        if obj.description:
            printinfo('Device description: %s' % obj.description)
        if obj.__class__.__doc__:
            lines = obj.__class__.__doc__.strip().splitlines()
            printinfo('Device class description: ' + lines[0])
            for line in lines[1:]:
                printinfo(line)
        from nicos.commands.device import listmethods, listparams
        listmethods(obj)
        listparams(obj)
    elif not inspect.isfunction(obj):
        __builtin__.help(obj)
    else:
        # for functions, print arguments and docstring
        real_func = getattr(obj, 'real_func', obj)
        argspec = inspect.formatargspec(*inspect.getargspec(real_func))
        printinfo('Usage: ' + real_func.__name__ + argspec)
        for line in formatDocstring(real_func.__doc__ or '', '   '):
            printinfo(line)

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
    if session.mode == 'simulation':
        session.clock.tick(secs)
        return
    MAX_INTERVAL = 5
    # partition the whole preset time in slices of MAX_INTERVAL
    full, fraction = divmod(secs, MAX_INTERVAL)
    intervals = [MAX_INTERVAL] * int(full)
    printinfo('sleeping for %.1f seconds...' % secs)
    if fraction:
        intervals.append(fraction)
    for interval in intervals:
        session.breakpoint(2) # allow break and continue here
        time.sleep(interval)


# -- other basic commands ------------------------------------------------------

@usercommand
def NewSetup(*setupnames):
    """Load the given setup instead of the current one."""
    current_mode = session.mode
    # refresh setup files first
    session.readSetups()
    session.unloadSetup()
    try:
        session.startMultiCreate()
        try:
            session.loadSetup(setupnames)
        finally:
            session.endMultiCreate()
    except Exception:
        printexception()
        session.loadSetup('startup')
    if current_mode == 'master':
        # need to refresh master status
        SetMode('master')

@usercommand
def AddSetup(*setupnames):
    """Load the given setup additional to the current one."""
    session.readSetups()
    session.startMultiCreate()
    try:
        session.loadSetup(setupnames)
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
            except NicosError:
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
def ClearCache(*devnames):
    """Clear all local cached information for a given device."""
    for devname in devnames:
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


def _scriptfilename(filename):
    fn = path.normpath(path.join(session.experiment.scriptdir, filename))
    if not fn.endswith('.py'):
        fn += '.py'
    return fn


@usercommand
def Edit(filename):
    """Edit the script file given by file name.  If the file name is not
    absolute, it is relative to the experiment script directory.

    The editor is given by the EDITOR environment variable.
    """
    if 'EDITOR' not in os.environ:
        printerror('no EDITOR environment variable is set, cannot edit')
        return
    fn = _scriptfilename(filename)
    printinfo('starting editor...')
    os.system('$EDITOR "%s"' % fn)
    reply = raw_input('<R>un or <S>imulate the script? ')
    if reply.upper() == 'R':
        Run(filename)
    elif reply.upper() == 'S':
        Simulate(filename)


@usercommand
def _RunScript(filename, statdevices):
    fn = _scriptfilename(filename)
    if not path.isfile(fn) and os.access(fn, os.R_OK):
        raise UsageError('The file %r does not exist or is not readable' % fn)
    if session.mode == 'simulation':
        starttime = session.clock.time
        for dev in statdevices:
            if not isinstance(dev, Readable):
                raise UsageError('unable to collect statistics on %r' % dev)
            dev._sim_min = None
            dev._sim_max = None
    printinfo('running user script: ' + fn)
    with open(fn, 'r') as fp:
        code = unicode(fp.read(), 'utf-8')
        compiled = compile(code, fn, 'exec', CO_DIVISION)
        with _Scope(fn):
            exec compiled in session.getLocalNamespace(), session.getNamespace()
    printinfo('finished user script: ' + fn)
    if session.mode == 'simulation':
        printinfo('simulated minimum runtime: ' +
                  formatDuration(session.clock.time - starttime))
        for dev in statdevices:
            printinfo('%s: min %s, max %s, last %s' % (
                dev.name, dev.format(dev._sim_min), dev.format(dev._sim_max),
                dev.format(dev._sim_value)))


@usercommand
def Run(filename):
    """Run a script file given by file name.  If the file name is not absolute,
    it is relative to the experiment script directory.
    """
    _RunScript(filename, ())


@usercommand
def Simulate(filename, *devices):
    """Run a script file in simulation mode.  If the file name is not absolute,
    it is relative to the experiment script directory.

    Position statistics will be collected for the given list of devices:
        Simulate('test', T)
    will simulate the 'test.py' user script and print out minimum/maximum/
    last value of T during the run.

    If the session is already in simulation mode, this is the same as Run().
    """
    if session.mode == 'simulation':
        return _RunScript(filename, devices)
    session.forkSimulation('_RunScript(%r, [%s])' %
                           (filename, ', '.join(dev.name for dev in devices)))


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
        if session.instrument is None:
            f.write('    instrument = None,\n')
        else:
            f.write('    instrument = %r,\n' % session.instrument.name)
        if session.experiment is None:
            f.write('    experiment = None,\n')
        else:
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
                if session.mode == 'simulation':
                    value = dev._sim_value
                else:
                    value = dev.read()
                f.write('_SimulationRestore(%r, %r)\n' % (dev.name, value))
        f.write('"""\n')

@usercommand
def _SimulationRestore(devname, value):
    """Restore value of a device in a simulation setup.

    This needs to be a usercommand because it is executed in the user namespace,
    but by prefixing the name with an underscore it is hidden from the user.
    """
    printinfo('Setting simulated value of device %s to %r' % (devname, value))
    session.getDevice(devname)._sim_value = value


@usercommand
def _trace():
    if session._lastUnhandled:
        printinfo(''.join(traceback.format_exception(*session._lastUnhandled)))
    else:
        printinfo('No previous traceback.')
