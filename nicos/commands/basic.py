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

"""Module for basic user commands."""

import io
import os
import sys
import time
import inspect
import traceback
from os import path

from nicos import session
from nicos.core import requires, Device, Readable, ModeError, NicosError, \
    UsageError
from nicos.core.spm import spmsyntax, AnyDev, Bool, Num, Multi, Oneof, \
    String, SetupName, DeviceName
from nicos.core.sessions.utils import EXECUTIONMODES
from nicos.utils import formatDuration, printTable
from nicos.devices.notifiers import Mailer
from nicos.commands import usercommand, hiddenusercommand, helparglist
from nicos.commands.output import printinfo, printwarning, printexception, printerror
from nicos.core import SIMULATION, MASTER, MAINTENANCE, ADMIN
from nicos.pycompat import builtins, exec_, iteritems
from nicos.core.utils import checkUserLevel


CO_DIVISION = 0x2000


__all__ = [
    'help', 'dir', 'ListCommands', 'sleep',
    'NewSetup', 'AddSetup', 'RemoveSetup', 'ListSetups',
    '_Restart', 'Keep',
    'CreateDevice', 'RemoveDevice', 'CreateAllDevices',
    'NewExperiment', 'FinishExperiment', 'AddUser', 'NewSample',
    'Remark', 'SetMode', 'SetSimpleMode',
    'sync', 'ClearCache', 'UserInfo', '_RunScript', '_RunCode', 'run', 'sim',
    'notify', 'SetMailReceivers', '_trace', 'timer',
    'LogEntry', '_LogAttach',
]


# -- help and introspection ----------------------------------------------------

@usercommand
@helparglist('[object]')
def help(obj=None):  # pylint: disable=W0622
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

builtins.__orig_dir = builtins.dir


@hiddenusercommand
@helparglist('[object]')
def dir(obj=None):  # pylint: disable=W0622
    """Show all public attributes for the given object."""
    if obj is None:
        return sorted(sys._getframe(1).f_locals)
    return [name for name in builtins.__orig_dir(obj)
            if not name.startswith(('_', 'do'))]


@usercommand
def ListCommands():
    """List all available commands.

    Example:

    >>> ListCommands()
    """
    printinfo('Available commands:')
    items = []
    for name, obj in session.getExportedObjects():
        if hasattr(obj, 'is_usercommand'):
            real_func = getattr(obj, 'real_func', obj)
            if getattr(real_func, 'is_hidden', False):
                continue
            if real_func.__name__ != name:
                # it's an alias, don't show it again
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
@spmsyntax(Num)
def sleep(secs):
    """Sleep for a given number of seconds.

    This is different from Python's `time.sleep()` in that it allows breaking
    and stopping the sleep, and supports simulation mode.  Fractional values are
    supported.

    Examples:

    >>> sleep(10)     # sleep for 10 seconds
    >>> sleep(0.5)    # sleep for half a second
    """
    if session.mode == SIMULATION:
        session.clock.tick(secs)
        return
    MAX_INTERVAL = 5
    # partition the whole preset time in slices of MAX_INTERVAL
    full, fraction = divmod(secs, MAX_INTERVAL)
    intervals = [MAX_INTERVAL] * int(full)
    printinfo('sleeping for %.1f seconds...' % secs)
    if fraction:
        intervals.append(fraction)
    session.beginActionScope('Sleeping')
    try:
        for interval in intervals:
            session.breakpoint(2)  # allow break and continue here
            time.sleep(interval)
    finally:
        session.endActionScope()


# -- other basic commands ------------------------------------------------------

@usercommand
@helparglist('[setup, ...]')
@spmsyntax(Multi(SetupName('all')))
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
    if current_mode == MASTER:
        # need to refresh master status
        session.setMode(MASTER)


@usercommand
@helparglist('setup, ...')
@spmsyntax(Multi(SetupName('unloaded')))
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
@spmsyntax(Multi(SetupName('loaded')))
def RemoveSetup(*setupnames):
    """Remove the given setups from the currently loaded ones.

    Example:

    >>> RemoveSetup('gaussmeter')

    will re-load all current setups except for "gaussmeter".
    """
    current = session.explicit_setups[:]
    original = current[:]
    for setupname in setupnames:
        if setupname not in session.loaded_setups:
            printwarning('%r is not a loaded setup, ignoring' % setupname)
            continue
        try:
            current.remove(setupname)
        except ValueError:
            printwarning('the setup %r cannot be unloaded on its own '
                         'because another setup includes it' % setupname)
    if current == original:
        return
    NewSetup(*current)


@usercommand
@spmsyntax(listall=Bool)
def ListSetups(listall=False):
    """Print a list of setups.

    Example:

    >>> ListSetups()

    To list also low-level and simulation setups:

    >>> ListSetups(True)
    """
    printinfo('Available setups:')
    items = []
    for name, info in iteritems(session.getSetupInfo()):
        if info is None:
            items.append((name, '', '<could not be read, check syntax>', ''))
            continue
        if info['group'] == 'special':
            continue
        if info['group'] in ('simulated', 'lowlevel') and not listall:
            continue
        items.append((name, name in session.loaded_setups and 'yes' or '',
                      info['description'],
                      ', '.join(sorted(info['devices']))))
    items.sort()
    printTable(('name', 'loaded', 'description', 'devices'), items, printinfo)


@usercommand
def _Restart():
    """Restart the NICOS process.  Use with caution."""
    import atexit
    import signal

    @atexit.register
    def restart_nicos():  # pylint: disable=W0612
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
@spmsyntax(Multi(DeviceName))
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
@spmsyntax(Multi(AnyDev))
def RemoveDevice(*devnames):
    """Remove all given devices from the currently loaded setup.

    "Remove" means that the device is unloaded and will be unavailable until it
    is created again using `CreateDevice`.  Examples:

    >>> RemoveDevice(stx)         # destroy "stx" device
    >>> RemoveDevice(stx, sty)    # destroy two devices by name
    """
    if not devnames:
        raise UsageError('At least one device is required')
    for devname in devnames:
        if isinstance(devname, Device):
            devname = devname.name
        session.destroyDevice(devname)


@usercommand
@helparglist('lowlevel=False')
def CreateAllDevices(**kwargs):
    """Try to create all possible devices in the current setup.

    This is useful when a setup failed to load many devices, and another attempt
    should be made.  Example:

    >>> CreateAllDevices()

    Note: Devices that are marked as lowlevel will not be automatically created,
    unless you set the lowlevel flag like:

    >>> CreateAllDevices(lowlevel=True)
    """
    lowlevel = kwargs.get('lowlevel', False)
    if lowlevel and not checkUserLevel(ADMIN):
        printerror('Creating all lowlevel devices is only allowed for admin users')
        lowlevel = False

    session.startMultiCreate()
    try:
        for devname, (_, devconfig) in iteritems(session.configured_devices):
            if devconfig.get('lowlevel', False) and not lowlevel:
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
    if session.mode == SIMULATION:
        return
    session.experiment.new(proposal, title, localcontact, user, **parameters)


@usercommand
@helparglist('...')
def FinishExperiment(*args, **kwargs):
    """Finish the current experiment.

    Which parameters are accepted depends on the individual instrument.
    """
    if session.mode == SIMULATION:
        return
    session.experiment.finish(*args, **kwargs)


@hiddenusercommand
@helparglist('name, email[, affiliation]')
def AddUser(name, email=None, affiliation=None):
    """Add a new user to the experiment.

    Example:

    >>> AddUser('F. User', 'friendlyuser@frm2.tum.de', 'FRM II')
    """
    if session.mode == SIMULATION:
        return
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
    session.experiment.newSample(name, parameters)


@usercommand
@spmsyntax(String)
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
@spmsyntax(Oneof(*EXECUTIONMODES))
@requires(level='admin')
def SetMode(mode):
    """Set the execution mode.

    Valid modes are 'master', 'slave', 'simulation' and 'maintenance'.

    * 'master' mode is for normal operation.  Only one copy of the instrument
      software can be in master mode at the same time.

    * 'slave' mode is for secondary copies of the software.  They can only read
      the instrument status, but not move devices or set parameters.

    * 'simulation' mode is for complete simulation of the instrument.  When
      switching to simulation mode, the current state of the instrument is
      taken as the basis of the simulation.  No hardware communication is
      possible in simulation mode.

      'simulation' does a non-physical emulation by running all the instrument
      specific code with virtualized devices.  Any problems which would appear
      runnig the same commands in 'master' mode (with ideal hardware) can be
      spotted by the user, such as devices moving out of limits, failing
      calculations, or invalid parameters.

      Furthermore, the ranges of all devices which are moved are recorded and
      the required time to run a command or script is estimated from device
      properties ('speed', 'ramp', 'accel').

      It is currently not implemented to switch back: use the `sim()` command
      for doing one-off simulations.

    * 'maintenance' mode is for instrument scientists only.

    Example:

    >>> SetMode('slave')    # e.g. to let another master take over
    ...
    >>> SetMode('master')   # switch back to master in this copy
    """
    if mode == 'sim':
        mode = SIMULATION
    elif mode == 'maint':
        mode = MAINTENANCE
    try:
        session.setMode(mode)
    except ModeError:
        printexception()


@usercommand
@spmsyntax(Bool)
def SetSimpleMode(enable):
    """Enable or disable Simple Parameter Mode.  Example:

    >>> SetSimpleMode(True)

    In Simple mode, commands are entered without parentheses and commas
    separating the parameters.
    """
    session.setSPMode(enable)
    if enable:
        printinfo('Simple parameter mode is now enabled. '
                  'Use "SetSimpleMode false" to disable.')
    else:
        printinfo('Simple parameter mode is now disabled. '
                  'Use "SetSimpleMode(True)" to enable.')


@usercommand
def sync():
    """Synchronize simulation copy with master copy.

    This will fetch the current setups and state of the actual instrument and
    apply it to the simulated devices in the current NICOS instance.  New setups
    will be loaded, and the current values and parameters of simulated devices
    will be updated.  Example:

    >>> sync()
    """
    session.simulationSync()


@usercommand
@helparglist('dev, ...')
@spmsyntax(Multi(AnyDev))
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


@hiddenusercommand
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
    fn = filename
    if not path.isabs(fn):
        fn = path.normpath(path.join(session.experiment.scriptpath, fn))
    # does the file exist?
    if fn.endswith(('.py', '.txt')) and path.isfile(fn):
        return fn
    if path.isfile(fn + '.py'):
        return fn + '.py'
    if path.isfile(fn + '.txt'):
        return fn + '.txt'
    # file does not exist; does it already have an extension?
    if fn.endswith(('.py', '.txt')):
        return fn
    # add an extension; the default depends on the current mode
    if session._spmode:
        return fn + '.txt'
    return fn + '.py'


class _ScriptScope(object):
    def __init__(self, filename, code):
        self.filename = filename
        self.code = code

    def __enter__(self):
        session.beginActionScope(self.filename)
        if session.experiment and session.mode in (MASTER, SIMULATION):
            session.experiment.scripts += [self.code]
        session.elog_event('scriptbegin', self.filename)

    def __exit__(self, *args):
        session.endActionScope()
        if session.experiment and session.mode in (MASTER, SIMULATION):
            session.experiment.scripts = session.experiment.scripts[:-1]
        session.elog_event('scriptend', self.filename)


@usercommand
def _RunScript(filename, statdevices, debug=False):
    fn = _scriptfilename(filename)
    if not path.isfile(fn) and os.access(fn, os.R_OK):
        raise UsageError('The file %r does not exist or is not readable' % fn)
    if session.mode == SIMULATION:
        starttime = session.clock.time
        for dev in statdevices:
            if not isinstance(dev, Readable):
                printwarning('unable to collect statistics on %r' % dev)
                continue
            dev._sim_min = None
            dev._sim_max = None
    printinfo('running user script: ' + fn)
    try:
        fp = io.open(fn, 'r', encoding='utf-8')
    except Exception as e:
        if session.mode == SIMULATION:
            session.log.exception('Simulation: error opening script')
            return
        raise NicosError('cannot open script %r: %s' % (filename, e))
    with fp:
        code = fp.read()
        # quick guard against self-recursion
        if session.experiment and session.experiment.scripts and \
                code.strip() == session.experiment.scripts[-1].strip():
            raise NicosError('script %r would call itself, aborting' % filename)
        compiler = lambda src: compile(src + '\n', fn, 'exec', CO_DIVISION)
        compiled = session.scriptHandler(code, fn, compiler)
        with _ScriptScope(path.basename(fn), code):
            try:
                exec_(compiled, session.namespace, session.local_namespace)
            except Exception:
                if debug:
                    traceback.print_exc()
                raise
    printinfo('finished user script: ' + fn)
    if session.mode == SIMULATION:
        printinfo('simulated minimum runtime: ' +
                  formatDuration(session.clock.time - starttime))
        for dev in statdevices:
            if not isinstance(dev, Readable):
                continue
            printinfo('%s: min %s, max %s, last %s %s' % (
                dev.name, dev.format(dev._sim_min), dev.format(dev._sim_max),
                dev.format(dev._sim_value), dev.unit))


@usercommand
def _RunCode(code, debug=False):
    if session.mode == SIMULATION:
        starttime = session.clock.time
    try:
        exec_(code, session.namespace, session.local_namespace)
    except Exception:
        if debug:
            traceback.print_exc()
        raise
    if session.mode == SIMULATION:
        printinfo('simulated minimum runtime: ' +
                  formatDuration(session.clock.time - starttime))


@usercommand
def run(filename):
    """Run a script file given by file name.

    If the file name is not absolute, it is relative to the experiment script
    directory.

    Examples:

    >>> run('night_16jul')              # run file in the current script dir
    >>> run('/data/scripts/maint/vanadium')     # run with complete filename
    """
    _RunScript(filename, ())


@usercommand
@helparglist('filename_or_code, ...')
def sim(what, *devices, **kwargs):
    """Run code or a script file in simulation mode.

    If the file name is not absolute, it is relative to the experiment script
    directory.

    For script files, position statistics will be collected for the given list
    of devices:

    >>> sim('testscript', T)

    will simulate the 'testscript.py' user script.

    Simulation mode does a non-physical emulation by running all the instrument
    specific code with virtualized devices.  Any problems which would appear
    runnig the same commands in 'master' mode (with ideal hardware) can be
    spotted by the user, such as devices moving out of limits, failing
    calculations, or invalid parameters.

    Furthermore, the ranges of all devices which are moved are recorded and
    the required time to run a command or script is estimated from device
    properties ('speed', 'ramp', 'accel').

    Example with running code directly:

    >>> sim('move(mono, 1.55); read(mtt)')
    """
    debug = bool(kwargs.get('debug', False))
    fn = _scriptfilename(what)
    if not path.isfile(fn) and not what.endswith(('.py', '.txt')):
        try:
            compile(what + '\n', 'exec', 'exec')
        except Exception:
            raise NicosError('Argument is neither a script file nor valid code')
        session.runSimulation('_RunCode(%r, %s)' % (what, debug))
        return
    if session.mode == SIMULATION:
        return _RunScript(what, devices)
    session.runSimulation('_RunScript(%r, [%s], %s)' %
                          (what, ', '.join(dev.name for dev in devices), debug))


@usercommand
@helparglist('[subject, ]bodytext')
def notify(*args):
    """Send a message via email and/or SMS.

    The receivers of email messages can be selected by `SetMailReceivers()`.

    Usage is one of these two:

    >>> notify('some text')
    >>> notify('subject', 'some text')
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


@hiddenusercommand
def _LogAttach(description, paths, names):
    """Attach one or more files to the electronic logbook.

    The file *paths* should be temporary file names accessible from the machine
    on which the electronic logbook daemon runs (i.e. on a common network
    share).  They will be moved to the logbook using the given *names*.

    This is intended to be used from the NICOS GUI, from the respective dialogs.
    """
    session.elog_event('attachment', (description, paths, names))
