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

"""Module for basic user commands."""

from __future__ import with_statement

__version__ = "$Revision$"

import os
import sys
import time
import shutil
import inspect
import traceback
import __builtin__
from os import path

from nicos import session
from nicos.core import Device, AutoDevice, Readable, ModeError, NicosError, \
     UsageError
from nicos.utils import formatDuration, printTable
from nicos.notify import Mailer, SMSer
from nicos.commands import usercommand, hiddenusercommand, helparglist
from nicos.commands.output import printinfo, printwarning, printerror, \
     printexception

CO_DIVISION = 0x2000


# -- help and introspection ----------------------------------------------------

@usercommand
@helparglist('[object]')
def help(obj=None): #pylint: disable=W0622
    """Show help for a command, for a device or for any other object.

    For commands, the command help and usage will be shown.  For devices, the
    device help, parameters and special commands will be shown.

    Examples:

    >>> help()            # show list of commands
    >>> help(det)         # show help on the "det" device
    >>> help(move)        # show help on the "move" command

    If the given object is not a special NICOS object, the standard Python help
    is invoked.
    """
    session.showHelp(obj)

__builtin__.__orig_dir = __builtin__.dir

@hiddenusercommand
@helparglist('[object]')
def dir(obj=None): #pylint: disable=W0622
    """Show all public attributes for the given object."""
    if obj is None:
        return sorted(sys._getframe(2).f_locals)
    return [name for name in __builtin__.__orig_dir(obj)
            if not name.startswith(('_', 'do'))]

@usercommand
def listcommands():
    """List all available commands.

    Example:

    >>> listcommands()
    """
    printinfo('Available commands:')
    items = []
    for obj in session.getExportedObjects():
        if hasattr(obj, 'is_usercommand'):
            real_func = getattr(obj, 'real_func', obj)
            if real_func.is_hidden:
                continue
            if hasattr(real_func, 'help_arglist'):
                argspec = '(%s)' % real_func.help_arglist
            else:
                argspec = inspect.formatargspec(*inspect.getargspec(real_func))
            docstring = real_func.__doc__ or ' '
            signature = real_func.__name__ + argspec
            if len(signature) > 50:
                signature = signature[:47] + '...'
            if not real_func.__name__.startswith('_'):
                items.append((signature, docstring.splitlines()[0]))
    items.sort()
    printTable(('name', 'description'), items, printinfo)

@usercommand
def sleep(secs):
    """Sleep for a given number of seconds.

    This is different from Python's `time.sleep()` in that it allows breaking
    and stopping the sleep, and supports simulation mode.  Fractional values are
    supported.

    Examples:

    >>> sleep(10)     # sleep for 10 seconds
    >>> sleep(0.5)    # sleep for half a second
    """
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
@helparglist('[setup, ...]')
def NewSetup(*setupnames):
    """Load the given setups instead of the current one.

    Example:

    >>> NewSetup('tas', 'psd')

    will clear the current setup and load the "tas" and "psd" setups at the
    same time.

    Without arguments, the current setups are reloaded.  Example:

    >>> NewSetup()

    You can use `ListSetups()` to find out which setups are available.
    """
    current_mode = session.mode
    # reload current setups if none given
    if not setupnames:
        setupnames = session.explicit_setups
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
@helparglist('setup, ...')
def AddSetup(*setupnames):
    """Load the given setups additional to the current one.

    Example:

    >>> AddSetup('gaussmeter')

    will load the "gaussmeter" setup in addition to the current setups.

    You can use `ListSetups()` to find out which setups are available.
    """
    if not setupnames:
        ListSetups()
        return
    session.readSetups()
    session.startMultiCreate()
    try:
        session.loadSetup(setupnames)
    finally:
        session.endMultiCreate()

@usercommand
@helparglist('setup, ...')
def RemoveSetup(*setupnames):
    """Remove the given setups from the currently loaded ones.

    Example:

    >>> RemoveSetup('gaussmeter')

    will re-load all current setups except for "gaussmeter".
    """
    current = session.explicit_setups[:]
    original = current[:]
    for setupname in setupnames:
        try:
            current.remove(setupname)
        except ValueError:
            printwarning('the setup %r is not currently explicitly loaded' %
                         setupname)
    if current == original:
        return
    NewSetup(*current)

@usercommand
def ListSetups():
    """Print a list of all known setups.

    Example:

    >>> ListSetups()
    """
    printinfo('Available setups:')
    items = []
    for name, info in session.getSetupInfo().iteritems():
        if info['group'] == 'special':
            continue
        items.append((name, info['description'],
                      ', '.join(sorted(info['devices']))))
    items.sort()
    printTable(('name', 'description', 'devices'), items, printinfo)

@usercommand
def _Restart():
    """Restart the NICOS process.  Use with caution."""
    import atexit, signal
    @atexit.register
    def restart_nicos():
        os.execv(sys.executable, [sys.executable] + sys.argv)
    os.kill(os.getpid(), signal.SIGTERM)

@hiddenusercommand
def Keep(name, obj):
    """Export the given *obj* into the NICOS namespace under the *name*.

    This makes the given name read-only, so that the object cannot be
    overwritten by accident.
    """
    session.export(name, obj)

@usercommand
@helparglist('devname, ...')
def CreateDevice(*devnames):
    """Create all given devices.

    Examples:

    >>> CreateDevice('det')                 # create "det" device
    >>> CreateDevice('stx', 'sty', 'stz')   # create all of "stx", "sty", "stz"

    CreateDevice can also be used to make lowlevel devices accessible in the
    user namespace.
    """
    for devname in devnames:
        session.createDevice(devname, explicit=True)

@usercommand
@helparglist('devname, ...')
def DestroyDevice(*devnames):
    """Destroy all given devices.

    "Destroy" means that the device is unloaded and will be unavailable until it
    is created again using `CreateDevice`.  Examples:

    >>> DestroyDevice(stx)         # destroy "stx" device
    >>> DestroyDevice(stx, sty)    # destroy two devices by name
    """
    if not devnames:
        raise UsageError('At least one device is required')
    for devname in devnames:
        if isinstance(devname, Device):
            devname = devname.name
        session.destroyDevice(devname)

@usercommand
def CreateAllDevices():
    """Try to create all possible devices in the current setup.

    This is useful when a setup failed to load many devices, and another attempt
    should be made.  Example:

    >>> CreateAllDevices()

    Note: Devices that are marked as lowlevel will not be automatically created.
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
@helparglist('proposal, title, localcontact, ...')
def NewExperiment(proposal, title='', localcontact='', user='', **parameters):
    """Start a new experiment with the given proposal number and title.

    You should also give a argument for the local contact and the primary user.
    More users can be added later with `AddUser`.  Example:

    >>> NewExperiment(5401, 'Spin waves', 'L. Contact', 'F. User <user@abc.de>')

    When configured, proposal information will be automatically filled in from
    the proposal database.
    """
    session.experiment.new(proposal, title, localcontact, user, **parameters)

@usercommand
@helparglist('...')
def FinishExperiment(*args, **kwargs):
    """Finish the current experiment.

    Which parameters are accepted depends on the individual instrument.
    """
    session.experiment.finish(*args, **kwargs)

@usercommand
@helparglist('name, email[, affiliation]')
def AddUser(name, email=None, affiliation=None):
    """Add a new user to the experiment.

    Example:

    >>> AddUser('F. User', 'friendlyuser@frm2.tum.de', 'FRM II')
    """
    session.experiment.addUser(name, email, affiliation)

@usercommand
@helparglist('name, ...')
def NewSample(name, **parameters):
    """Start a new sample with the given sample name.

    Example:

    >>> NewSample('D2O')

    Other parameters can be given, depending on the parameters of the sample
    object.  For example, for triple-axis spectrometers, the following command
    is valid:

    >>> NewSample('Cr', lattice=[2.88, 2.88, 2.88], angles=[90, 90, 90])
    """
    session.experiment.sample.samplename = name
    for param, value in parameters.iteritems():
        setattr(session.experiment.sample, param, value)

@usercommand
def Remark(remark):
    """Change the data file remark about instrument configuration.

    The current "remark" is saved in the data file, so you can use it to record
    sections of an experiment or changes to instrumental setup that are not
    otherwise visible in the NICOS devices.

    The change of the remark is also prominently put as a heading in the
    electronic logbook.

    Examples:

    >>> Remark('plexiglass in beam')      # replace remark
    >>> Remark('')                        # remove current remark
    """
    session.experiment.remark = remark

@usercommand
def Remember(what):
    """Add a message to remember at the next experiment change.

    When `FinishExperiment` or `NewExperiment` is next called, all messages
    given during the current experiment using Remember() will be displayed.
    This is intended for the instrument responsible to remember undoing
    temporary setup changes and the like.

    Example:

    >>> Remember('reset translation offset to zero')
    """
    rtime = time.strftime('(%m/%d %H:%M) ')
    session.experiment.remember += [rtime + what]

@usercommand
def SetMode(mode):
    """Set the execution mode.

    Valid modes are 'master', 'slave', 'simulation' and 'maintenance'.

    * 'master' mode is for normal operation.  Only one copy of the instrument
      software can be in master mode at the same time.

    * 'slave' mode is for secondary copies of the software.  They can only read
      the instrument status, but not move devices or set parameters.

    * 'simulation' mode is for complete simulation of the instrument.  When
      switching to simulation mode, the current state of the instrument is taken
      as the basis of the simulation.  No hardware communication is possible in
      simulation mode.

      It is not possible to switch back: use the `Simulate()` command for doing
      one-off simulations.

    * 'maintenance' mode is for instrument scientists only.

    Example:

    >>> SetMode('slave')    # e.g. to let another master take over
    ...
    >>> SetMode('master')   # switch back to master in this copy
    """
    if mode == 'sim':
        mode = 'simulation'
    elif mode == 'maint':
        mode = 'maintenance'
    try:
        session.setMode(mode)
    except ModeError:
        printexception()


@usercommand
@helparglist('dev, ...')
def ClearCache(*devnames):
    """Clear all cached information for the given device(s).

    This can be used when a device has been reconfigured in the setup and all
    parameters should be read from the setup file on the next loading of the
    setup.  Example:

    >>> ClearCache('om', 'phi')
    >>> NewSetup()

    will clear cache information for devices "om" and "phi" and then reload the
    current setup.
    """
    if not devnames:
        raise UsageError('At least one device name is required, use '
                         'ClearCache(\'*\') to clear everything')
    if devnames == ('*',):
        session.cache.clear_all()
        printinfo('cleared ALL cached information - you probably want to '
                  'restart the session now')
        return
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
def UserInfo(info):
    """Return an object for use in "with" that adds status information.

    Example use:

    >>> with UserInfo('Qscan around (1,1,0)'):
    ...     qscan(...)

    During the execution of the "with" block, the info 'Qscan around (1,1,0)'
    will be displayed in the "current status" of the instrument.
    """
    return _Scope(info)


def _scriptfilename(filename):
    fn = path.normpath(path.join(session.experiment.scriptdir, filename))
    if not fn.endswith('.py'):
        fn += '.py'
    return fn


@usercommand
def Edit(filename):
    """Edit the script file given by file name.

    If the file name is not absolute, it is relative to the experiment script
    directory.

    Examples:

    >>> Edit('night_16jul')       # edit file in the current script dir
    >>> Edit('/data/scripts/maint/vanadium')     # edit by complete filename

    The editor is given by the ``EDITOR`` environment variable, which can be
    conveniently set in the nicos.conf file.
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


class _ScriptScope(object):
    def __init__(self, filename, code):
        self.filename = filename
        self.code = code
    def __enter__(self):
        session.beginActionScope(self.filename)
        if session.experiment and session.mode == 'master':
            session.experiment.scripts += [self.code]
        session.elog_event('scriptbegin', self.filename)
    def __exit__(self, *args):
        session.endActionScope()
        if session.experiment and session.mode == 'master':
            session.experiment.scripts = session.experiment.scripts[:-1]
        session.elog_event('scriptend', self.filename)


@usercommand
def _RunScript(filename, statdevices, debug=False):
    fn = _scriptfilename(filename)
    if not path.isfile(fn) and os.access(fn, os.R_OK):
        raise UsageError('The file %r does not exist or is not readable' % fn)
    if session.mode == 'simulation':
        starttime = session.clock.time
        for dev in statdevices:
            if not isinstance(dev, Readable):
                printwarning('unable to collect statistics on %r' % dev)
                continue
            dev._sim_min = None
            dev._sim_max = None
    printinfo('running user script: ' + fn)
    with open(fn, 'r') as fp:
        code = unicode(fp.read(), 'utf-8')
        compiled = compile(code + '\n', fn, 'exec', CO_DIVISION)
        with _ScriptScope(path.basename(fn), code):
            try:
                exec compiled in session.namespace, session.local_namespace
            except Exception:
                if debug:
                    traceback.print_exc()
                raise
    printinfo('finished user script: ' + fn)
    if session.mode == 'simulation':
        printinfo('simulated minimum runtime: ' +
                  formatDuration(session.clock.time - starttime))
        for dev in statdevices:
            if not isinstance(dev, Readable):
                continue
            printinfo('%s: min %s, max %s, last %s' % (
                dev.name, dev.format(dev._sim_min), dev.format(dev._sim_max),
                dev.format(dev._sim_value)))


@usercommand
def _RunCode(code, debug=False):
    if session.mode == 'simulation':
        starttime = session.clock.time
    try:
        exec code in session.namespace, session.local_namespace
    except Exception:
        if debug:
            traceback.print_exc()
        raise
    if session.mode == 'simulation':
        printinfo('simulated minimum runtime: ' +
                  formatDuration(session.clock.time - starttime))


@usercommand
def Run(filename):
    """Run a script file given by file name.

    If the file name is not absolute, it is relative to the experiment script
    directory.

    Examples:

    >>> Run('night_16jul')              # run file in the current script dir
    >>> Run('/data/scripts/maint/vanadium')     # run with complete filename
    """
    _RunScript(filename, ())


@usercommand
@helparglist('filename_or_code, ...')
def Simulate(what, *devices, **kwargs):
    """Run code or a script file in simulation mode.

    If the file name is not absolute, it is relative to the experiment script
    directory.

    For script files, position statistics will be collected for the given list
    of devices:

    >>> Simulate('testscript', T)

    will simulate the 'test.py' user script and print out minimum/maximum/
    last value of T during the run.

    Example with running code directly:

    >>> Simulate('move(mono, 1.55); read(mtt)')
    """
    debug = bool(kwargs.get('debug', False))
    fn = _scriptfilename(what)
    if not path.isfile(fn) and not what.endswith('.py'):
        try:
            compile(what + '\n', 'exec', 'exec')
        except Exception:
            raise NicosError('Argument is neither a script file nor valid code')
        session.forkSimulation('_RunCode(%r, %s)' % (what, debug))
        return
    if session.mode == 'simulation':
        return _RunScript(what, devices)
    session.forkSimulation('_RunScript(%r, [%s], %s)' %
        (what, ', '.join(dev.name for dev in devices), debug))


@usercommand
@helparglist('[subject, ]bodytext')
def Notify(*args):
    """Send a message via email and/or SMS.

    The receivers of the message can be selected by `SetMailReceivers()` and
    `SetSMSReceivers()`.  Usage is one of these two:

    >>> Notify('some text')
    >>> Notify('subject', 'some text')
    """
    if len(args) == 1:
        # use first line of text as subject
        text, = args
        session.notify(text.splitlines()[0], text, important=False)
    elif len(args) == 2:
        subject, text = args
        session.notify(subject, text, important=False)
    else:
        raise UsageError("Usage: Notify('text') or Notify('subject', 'text')")


@usercommand
@helparglist('email, ...')
def SetMailReceivers(*emails):
    """Set a list of email addresses for notifications.

    These addresses will be notified on unhandled errors, and when the
    `Notify()` command is used.

    Example:

    >>> SetMailReceivers('user@example.com', 'responsible@frm2.tum.de')
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
@helparglist('phonenumber, ...')
def SetSMSReceivers(*numbers):
    """Set a list of mobile phone numbers for notifications.

    These numbers will be notified on unhandled errors, and when the `Notify()`
    command is used.

    Note that all those phone numbers have to be registered with the IT
    department before they can be used.

    Example:

    >>> SetSMSReceivers('01712345678')
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
@helparglist('filename, name')
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


class timer(object):
    is_userobject = True
    def __enter__(self):
        self.starttime = time.time()
    def __exit__(self, *args):
        duration = time.time() - self.starttime
        printinfo('Elapsed time: %.3f s' % duration)

timer = timer()


@usercommand
def LogEntry(entry):
    """Make a free-form entry in the electronic logbook.

    The entry will be processed as Creole markup.

    Note: on the command line, you can also call this function by entering a
    Python comment.  I.e., these two commands are equivalent at the command
    line:

    >>> LogEntry('improved sample holder')

    >>> # improved sample holder
    """
    session.elog_event('entry', entry)


@usercommand
@helparglist('description, paths[, names]')
def LogAttach(description, paths, names=None):
    """Attach one or more files to the electronic logbook.

    The file *paths* must be accessible from the machine on which the electronic
    logbook daemon runs (i.e. on a common network share).  They will be renamed
    using the given *names*, if given, otherwise the current names are used.

    Examples:

    >>> LogAttach('quick fit of peak', '/tmp/peakfit.png', 'peak_100.png')
    >>> LogAttach('calibrations', ['/tmp/cal1.dat', '/tmp/cal2.dat'])

    In the NICOS GUI, the respective dialog can be used to easily add files to
    the logbook.
    """
    if isinstance(paths, basestring):
        paths = [paths]
    if isinstance(names, basestring):
        names = [names]
    if names is None:
        names = [path.basename(f) for f in paths]
    session.elog_event('attachment', (description, paths, names))
