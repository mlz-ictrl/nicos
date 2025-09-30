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
#
# *****************************************************************************

"""Module for basic user commands."""

import builtins
import os
import sys
import time
import traceback
from collections import defaultdict
from os import path

from nicos import session
from nicos.commands import helparglist, hiddenusercommand, parallel_safe, \
    usercommand
from nicos.core import ADMIN, MAINTENANCE, MASTER, SIMULATION, Device, \
    ModeError, NicosError, Readable, UsageError, requires
from nicos.devices.notifiers import Mailer
from nicos.protocols.daemon import BREAK_AFTER_STEP
from nicos.utils import LOCALE_ENCODING, fixupScript, formatArgs, \
    formatDuration, printTable, reexecProcess, resolveClasses
from nicos.utils.timer import Timer

__all__ = [
    'help', 'dir', 'ListCommands', 'sleep',
    'NewSetup', 'AddSetup', 'RemoveSetup', 'ListSetups',
    '_Restart', 'Keep',
    'CreateDevice', 'RemoveDevice', 'CreateAllDevices',
    'NewExperiment', 'FinishExperiment', 'AddUser', 'ListUsers',
    'Remark', 'SetMode',
    'sync', 'ClearCache', 'ClearAllCache', 'UserInfo', '_RunScript', '_RunCode',
    'run', 'sim', 'notify', 'SetMailReceivers', 'ListMailReceivers',
    'SetDataReceivers', 'ListDataReceivers', '_trace', 'timer',
    'LogEntry', 'HideLog', '_LogAttach', '_LogAttachImage',
    'SetErrorAbort', 'pause', 'userinput', 'abort',
]


# -- help and introspection ---------------------------------------------------

@usercommand
@helparglist('[object]')
@parallel_safe
def help(obj=None):  # pylint: disable=redefined-builtin
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
@parallel_safe
def dir(obj=None):  # pylint: disable=redefined-builtin
    """Show all public attributes for the given object."""
    if obj is None:
        return sorted(sys._getframe(1).f_locals)
    return [name for name in builtins.__orig_dir(obj)
            if not name.startswith(('_', 'do'))]


@usercommand
@parallel_safe
def ListCommands():
    """List all available commands.

    Example:

    >>> ListCommands()
    """
    session.log.info('Available commands:')
    items = []
    for name, obj in session.getExportedObjects():
        if getattr(obj, 'is_usercommand', False):
            real_func = getattr(obj, 'real_func', obj)
            if getattr(real_func, 'is_hidden', False):
                continue
            if real_func.__name__ != name:
                # it's an alias, don't show it again
                continue
            if hasattr(real_func, 'help_arglist'):
                argspec = '(%s)' % real_func.help_arglist
            else:
                argspec = formatArgs(real_func)
            docstring = real_func.__doc__ or ' '
            signature = real_func.__name__ + argspec
            if len(signature) > 50:
                signature = signature[:47] + '...'
            if not real_func.__name__.startswith('_'):
                items.append((signature, docstring.splitlines()[0]))
    items.sort()
    printTable(('name', 'description'), items, session.log.info)


@usercommand
def sleep(secs):
    """Sleep for a given number of seconds.

    This is different from Python's `time.sleep()` in that it allows breaking
    and stopping the sleep, and supports dry run mode.  Fractional values are
    supported.

    Examples:

    >>> sleep(10)     # sleep for 10 seconds
    >>> sleep(0.5)    # sleep for half a second
    """
    if secs > 1:
        session.log.info('sleeping for %.1f seconds...', secs)
    else:
        session.log.debug('sleeping for %.1f seconds...', secs)

    if session.mode == SIMULATION:
        session.clock.tick(secs)
        return

    def f_notify(tmr):
        session.breakpoint(BREAK_AFTER_STEP)  # allow break and continue here
        session.action('%s left' % formatDuration(tmr.remaining_time()))

    session.beginActionScope('Sleeping')
    session.action('%s left' % formatDuration(secs))
    try:
        tmr = Timer(secs)
        tmr.wait(interval=1.0, notify_func=f_notify)
    finally:
        session.endActionScope()


# -- other basic commands -----------------------------------------------------

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

    see also: `AddSetup`, `RemoveSetup`, `ListSetups`
    """
    current_mode = session.mode
    # reload current setups if none given
    update_aliases = True
    if not setupnames:
        update_aliases = False
        setupnames = session.explicit_setups
    # refresh setup files first
    session.readSetups()
    session.checkSetupCompatibility(setupnames, set())
    session.unloadSetup()
    try:
        session.startMultiCreate()
        try:
            session.loadSetup(setupnames, update_aliases=update_aliases)
        finally:
            session.endMultiCreate()
    except Exception:
        session.log.warning('could not load new setup, falling back to '
                            'startup setup', exc=1)
        session.unloadSetup()
        session.loadSetup('startup')
    if current_mode == MASTER:
        # need to refresh master status
        session.setMode(MASTER)


@usercommand
@helparglist('setup, ...')
def AddSetup(*setupnames):
    """Load the given setups additional to the current one.

    Example:

    >>> AddSetup('gaussmeter')

    will load the "gaussmeter" setup in addition to the current setups.

    You can use `ListSetups()` to find out which setups are available.

    see also: `NewSetup`, `RemoveSetup`, `ListSetups`
    """
    if not setupnames:
        ListSetups()
        return
    session.readSetups()
    session.checkSetupCompatibility(setupnames, session.loaded_setups)
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

    see also: `NewSetup`, `AddSetup`, `ListSetups`
    """
    current = session.explicit_setups[:]
    original = current[:]
    for setupname in setupnames:
        if setupname not in session.loaded_setups:
            session.log.warning('%r is not a loaded setup, ignoring',
                                setupname)
            continue
        if session._setup_info[setupname]['group'] == 'basic':
            session.log.error('basic setups cannot be removed -- use '
                              'NewSetup() to change setups instead')
            return
        try:
            current.remove(setupname)
        except ValueError:
            session.log.warning('the setup %r cannot be unloaded on its own '
                                'because another setup includes it', setupname)
    if current == original:
        return
    NewSetup(*current)


@usercommand
@parallel_safe
def ListSetups(listall=False):
    """Print a list of setups.

    Example:

    >>> ListSetups()

    To list also low-level and simulation setups:

    >>> ListSetups(True)

    see also: `NewSetup`, `AddSetup`, `RemoveSetup`
    """
    session.log.info('Available setups:')
    items = []
    for name, info in session.getSetupInfo().items():
        if info is None:
            items.append((name, '', '<could not be read, check syntax>', ''))
            continue
        if info['group'] in ('special', 'configdata'):
            continue
        if info['group'] == 'lowlevel' and not listall:
            continue
        items.append((name, name in session.loaded_setups and 'yes' or '',
                      info['description'],
                      ', '.join(sorted(info['devices']))))
    items.sort()
    printTable(('name', 'loaded', 'description', 'devices'), items,
               session.log.info)


@hiddenusercommand
@parallel_safe
def _Restart():
    """Restart the NICOS process.  Use with caution."""
    exp = session.experiment
    if exp and exp.hasProposalFinishThreads():
        raise NicosError('Cannot restart because there is at least one '
                         'proposal which is currently finishing.')

    import atexit
    import signal

    @atexit.register
    def restart_nicos():  # pylint: disable=unused-variable
        reexecProcess()
    os.kill(os.getpid(), signal.SIGTERM)


@hiddenusercommand
@parallel_safe
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

    CreateDevice can also be used to make non-visible devices accessible in the
    user namespace.

    see also: `CreateAllDevices`, `RemoveDevice`
    """
    for devname in devnames:
        if not isinstance(devname, str):
            raise UsageError('CreateDevice() arguments must be strings')
        session.createDevice(devname, explicit=True)
        session.kickDevicePoller(devname)


@usercommand
@helparglist('devname, ...')
def RemoveDevice(*devnames):
    """Remove all given devices from the currently loaded setup.

    "Remove" means that the device is unloaded and will be unavailable until it
    is created again using `CreateDevice`.  Examples:

    >>> RemoveDevice(stx)         # destroy "stx" device
    >>> RemoveDevice(stx, sty)    # destroy two devices by name

    see also: `CreateDevice`, `CreateAllDevices`
    """
    if not devnames:
        raise UsageError('At least one device is required')
    for devname in devnames:
        if isinstance(devname, Device):
            devname = devname.name
        session.destroyDevice(devname)


@usercommand
def CreateAllDevices(lowlevel=False):
    """Try to create all possible devices in the current setup.

    This is useful when a setup failed to load many devices, and another
    attempt should be made.  Example:

    >>> CreateAllDevices()

    Note: Devices that are marked as invisible in the user namespace will not
    be automatically created, unless you set the lowlevel flag like:

    >>> CreateAllDevices(lowlevel=True)

    see also: `CreateDevice`, `RemoveDevice`
    """
    if lowlevel and not session.checkUserLevel(ADMIN):
        session.log.error('Creating all lowlevel devices is only allowed '
                          'for admin users')
        lowlevel = False

    session.startMultiCreate()
    try:
        for devname, (_, devconfig) in session.configured_devices.items():
            if 'namespace' not in devconfig.get('visibility', ('namespace,')) \
               and not lowlevel:
                continue
            existed_already = devname in session.devices
            try:
                session.createDevice(devname, explicit=True)
                if not existed_already:
                    session.kickDevicePoller(devname)
            except NicosError:
                session.log.exception('error creating %s', devname)
    finally:
        session.endMultiCreate()


@usercommand
@helparglist('proposal, [title, localcontact, user, ...]')
def NewExperiment(proposal, title='', localcontact='', user='', **parameters):
    """Start a new experiment with the given proposal number and title.

    You should also give an argument for the local contact and the primary user.
    More users can be added later with `AddUser`.  Example:

    >>> NewExperiment(541, 'Spin waves', 'L. Contact', 'F. User <user@abc.de>')

    When configured, proposal information will be automatically filled in from
    the proposal database.

    see also: `FinishExperiment`
    """
    if session.mode == SIMULATION:
        return
    session.experiment.new(proposal, title, localcontact, user, **parameters)


@usercommand
def FinishExperiment():
    """Finish the current experiment.

    see also: `NewExperiment`
    """
    if session.mode == SIMULATION:
        return
    session.experiment.finish()


@hiddenusercommand
@helparglist('name, [email, affiliation]')
def AddUser(name, email=None, affiliation=None):
    """Add a new user to the experiment.

    Example:

    >>> AddUser('F. User', 'friendlyuser@frm2.tum.de', 'FRM II')
    """
    if session.mode == SIMULATION:
        return
    session.experiment.addUser(name, email, affiliation)


@usercommand
@parallel_safe
def ListUsers():
    """List the current users of the experiment.

    Example:

    >>> ListUsers()
    """
    session.log.info('Current users:')
    items = []
    for user in session.experiment.propinfo['users']:
        items.append((user['name'], user.get('email', ''),
                      user.get('affiliation', '')))
    items.sort()
    printTable(('name', 'email', 'affiliation'), items, session.log.info)


@usercommand
@parallel_safe
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


@hiddenusercommand
def SetMode(mode):
    """Set the execution mode.

    Valid modes are 'master', 'slave', 'simulation' and 'maintenance'.

    * 'master' mode is for normal operation.  Only one copy of the instrument
      software can be in master mode at the same time.

    * 'slave' mode is for secondary copies of the software.  They can only read
      the instrument status, but not move devices or set parameters.

    * 'simulation' mode is for complete simulation of the instrument.  When
      switching to dry-run/simulation mode, the current state of the instrument
      is taken as the basis of the run.  No hardware communication is possible
      in this mode.

      'simulation' does a non-physical emulation by running all the instrument
      specific code with virtualized devices.  Any problems which would appear
      runnig the same commands in 'master' mode (with ideal hardware) can be
      spotted by the user, such as devices moving out of limits, failing
      calculations, or invalid parameters.

      Furthermore, the ranges of all devices which are moved are recorded and
      the required time to run a command or script is estimated from device
      properties ('speed', 'ramp', 'accel').

      .. note:: It is currently not implemented to switch back: use the `sim()`
         command for doing one-off dry runs.

    * 'maintenance' mode is for instrument scientists only.

      .. note:: Be aware, that switching back to any other mode isn't supported

    Example:

    >>> SetMode('slave')    # e.g. to let another master take over
    ...
    >>> SetMode('master')   # switch back to master in this copy
    """
    if mode == 'sim':
        mode = SIMULATION
    elif mode == 'maint':
        mode = MAINTENANCE
    if mode == MAINTENANCE:
        # switching to maintenance mode is dangerous since two parallel
        # sessions can execute active commands
        session.checkAccess({'level': ADMIN})
    try:
        session.setMode(mode)
    except ModeError:
        session.log.exception()


@usercommand
def sync():
    """Synchronize dry-run/simulation copy with master copy.

    This will fetch the current setups and state of the actual instrument and
    apply it to the simulated devices in the current NICOS instance.  New
    setups will be loaded, and the current values and parameters of simulated
    devices will be updated.  Example:

    >>> sync()
    """
    session.simulationSync()


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

    Clearing the cache of a device means:

    - Parameters whose value is only stored in the cache (such as e.g. the
      offset parameter) return their initial value given in a setup file (if
      one was given) or their default value if queried (e.g. 0 for the offset).
    - Values which have a corresponding ``doRead`` method use it to obtain a
      new value. Functionally, this is equal to read the value with
      ``maxage=0``.

    After the parameter has been read / written to, the newly obtained / given
    value is used to populate the cache again.
    """
    if not devnames:
        raise UsageError('At least one device name is required')
    for devname in devnames:
        if isinstance(devname, Device):
            devname = devname.name
        session.cache.clear(devname)
        session.log.info('cleared cached information for %s', devname)


@hiddenusercommand
@requires(level=ADMIN,
          helpmsg='Clear all cached information is only allowed for admin users')
def ClearAllCache():
    """Clear all cached information for **ALL** devices

    This command can be used to "reset" the cache entirely by deleting the
    cached values for all parameters of all devices. This means that parameters
    only stored in the cache (such as e.g. offsets) are lost and can only be
    obtained again from the logs.

    Clearing the cache of a device means:

    - Parameters whose value is only stored in the cache (such as e.g. the
      offset parameter) return their initial value given in a setup file (if
      one was given) or their default value if queried (e.g. 0 for the offset).
    - Values which have a corresponding ``doRead`` method use it to obtain a
      new value. Functionally, this is equal to read the value with
      ``maxage=0``.

    After the parameter has been read / written to, the newly obtained / given
    value is used to populate the cache again.

    **Use with caution!**
    """
    session.cache.clear_all()
    session.log.info('cleared ALL cached information - you probably want '
                     'to restart the session now')

class _Scope:
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
    return fn + '.py'


class _ScriptScope:
    def __init__(self, filename, code):
        self.filename = filename
        self.code = code

    def __enter__(self):
        session.beginActionScope(self.filename)
        if session.experiment and session.mode in (MASTER, SIMULATION):
            session.experiment.scripts += [self.code]
        session.elogEvent('scriptbegin', self.filename)

    def __exit__(self, *args):
        session.endActionScope()
        if session.experiment and session.mode in (MASTER, SIMULATION):
            session.experiment.scripts = session.experiment.scripts[:-1]
        session.elogEvent('scriptend', self.filename)


@hiddenusercommand
def _RunScript(filename, statdevices, debug=False):
    fn = _scriptfilename(filename)
    if not path.isfile(fn) and os.access(fn, os.R_OK):
        raise UsageError('The file %r does not exist or is not readable' % fn)
    if session.mode == SIMULATION:
        starttime = session.clock.time
        for dev in statdevices:
            if not isinstance(dev, Readable):
                session.log.warning('unable to collect statistics on %r', dev)
                continue
            dev._sim_min = None
            dev._sim_max = None
    session.log.info('running user script: %s', fn)
    try:
        with open(fn, 'r', encoding=LOCALE_ENCODING) as fp:
            code = fp.read()
    except Exception as e:
        if session.mode == SIMULATION:
            session.log.exception('Dry run: error opening script')
            return
        raise NicosError('cannot open script %r: %s' % (filename, e)) from e
    # guard against bare excepts
    code = fixupScript(code)
    # quick guard against self-recursion
    if session.experiment and session.experiment.scripts and \
            code.strip() == session.experiment.scripts[-1].strip():
        raise NicosError('script %r would call itself, aborting' %
                         filename)

    compiled = compile(code + '\n', fn, 'exec')
    with _ScriptScope(path.basename(fn), code):
        try:
            exec(compiled, session.namespace)
        except Exception:
            if debug:
                traceback.print_exc()
            raise
    session.log.info('finished user script: %s', fn)
    if session.mode == SIMULATION:
        session.log.info('simulated minimum runtime: %s',
                         formatDuration(session.clock.time - starttime,
                                        precise=False))
        for dev in statdevices:
            if not isinstance(dev, Readable):
                continue
            session.log.info('%s: min %s, max %s, last %s %s',
                             dev.name,
                             dev.format(dev._sim_min),
                             dev.format(dev._sim_max),
                             dev.format(dev._sim_value), dev.unit)


@hiddenusercommand
def _RunCode(code, debug=False):
    if session.mode == SIMULATION:
        starttime = session.clock.time
    code = fixupScript(code)
    try:
        exec(code, session.namespace)
    except Exception:
        if debug:
            traceback.print_exc()
        raise
    if session.mode == SIMULATION:
        session.log.info('simulated minimum runtime: %s',
                         formatDuration(session.clock.time - starttime,
                                        precise=False))


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
    """Run code or a script file in dry run mode.

    If the file name is not absolute, it is relative to the experiment script
    directory.

    For script files, position statistics will be collected for the given list
    of devices:

    >>> sim('testscript', T)

    will simulate the 'testscript.py' user script.

    Dry run mode does a non-physical emulation by running all the instrument
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
        except Exception as e:
            raise NicosError('Argument is neither a script file nor valid '
                             'code') from e
        session.runSimulation('_RunCode(%r, %s)' % (what, debug))
        return
    if session.mode == SIMULATION:
        return _RunScript(what, devices)
    session.runSimulation('_RunScript(%r, [%s], %s)' %
                          (what, ', '.join(dev.name for dev in devices),
                           debug))


@usercommand
@helparglist('[subject, ]bodytext')
@parallel_safe
def notify(*args):
    """Send a message via a notification system (email, SMS, Slack, or others).

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
        raise UsageError("Usage: notify('text') or notify('subject', 'text')")


@usercommand
@helparglist('email, ...')
@parallel_safe
def SetMailReceivers(*emails):
    """Set a list of email addresses for notifications.

    These addresses will be notified on unhandled errors, and when the
    `notify()` command is used.

    Example:

    >>> SetMailReceivers('user@example.com', 'responsible@frm2.tum.de')

    see also: `ListMailReceivers`
    """
    emails = list(emails)
    ok = False
    exp = session.experiment
    propinfo = dict(exp.propinfo)
    propinfo['notif_emails'] = emails
    exp._setROParam('propinfo', propinfo)
    for notifier in session.notifiers:
        if isinstance(notifier, Mailer) and not notifier.private:
            ok = True
            notifier.receivers = emails
    if not ok:
        session.log.warning('general email notification is not configured '
                            'in this setup')
    else:
        ListMailReceivers()


@usercommand
@parallel_safe
def ListMailReceivers():
    """List all mail addresses for notifications.

    Example:

    >>> ListMailReceivers()

    see also: `SetMailReceivers`
    """
    session.log.info('Email addresses for notifications:')
    items = []
    for notifier, recipients in _listReceivers(Mailer).items():
        for rec in recipients:
            items.append((notifier,) + rec)
    printTable(('mailer', 'email address', 'info'), sorted(items),
               session.log.info)


def _listReceivers(classes, includeprivate=False):
    """Return a dictionary containing ``{notifier_name: [(address, type)]}``.

    Only considers notifiers that are instances of the given *classes*.
    """
    result = defaultdict(list)
    classes = resolveClasses(classes)

    for notifier in session.notifiers:
        if isinstance(notifier, classes) and \
           (includeprivate or not notifier.private):
            for addr in notifier.receivers:
                result[notifier.name].append((addr, 'receiver'))
            for addr, level in notifier.copies:
                result[notifier.name].append((addr, 'copies (%s)' % level))
    return result


@usercommand
@helparglist('email, ...')
@parallel_safe
def SetDataReceivers(*emails):
    """Set a list of email addresses for data retrieval.

    These addresses will get an email after `FinishExperiment()` with
    their experimental data.

    Example:

    >>> SetDataReceivers('pi@example.com', 'user@example.com')

    see also: `ListDataReceivers`
    """
    exp = session.experiment
    if not exp.mailserver or not exp.mailsender:
        session.log.warning('experimental data retrieval by email has not been '
                            'configured in this setup')
    else:
        propinfo = dict(exp.propinfo)
        propinfo['data_emails'] = list(emails)
        exp._setROParam('propinfo', propinfo)
        if emails:
            session.log.info('data retrieval email will be sent to %s',
                             ', '.join(emails))
        else:
            session.log.info('no data retrieval emails will be sent')


@usercommand
@parallel_safe
def ListDataReceivers():
    """List email addresses to which experimental data will be sent.

    Data is sent once when a proposal is finished.  See also
    `SetDataReceivers`.

    Example:

    >>> ListDataReceivers()

    see also: `SetDataReceivers`
    """
    session.log.info('Email addresses the data will be sent to:')
    propinfo = dict(session.experiment.propinfo)
    items = set()
    for addr in propinfo.get('data_emails', ()):
        items.add((addr,))
    printTable(('email address', ), sorted(items), session.log.info)


@usercommand
def _trace():
    if session._lastUnhandled:
        session.log.info(''.join(
            traceback.format_exception(*session._lastUnhandled)))
    else:
        session.log.info('No previous traceback.')


class timer:
    is_userobject = True

    def __enter__(self):
        self.starttime = time.time()

    def __exit__(self, *args):
        duration = time.time() - self.starttime
        session.log.info('Elapsed time: %.3f s', duration)


timer = timer()


@usercommand
@parallel_safe
def LogEntry(entry):
    """Make a free-form entry in the electronic logbook.

    The entry will be processed as Markdown markup.

    Note: on the command line, you can also call this function by entering a
    Python comment.  I.e., these two commands are equivalent at the command
    line:

    >>> LogEntry('improved sample holder')

    >>> # improved sample holder
    """
    session.elogEvent('entry', entry)


@usercommand
@parallel_safe
def HideLog(hidden):
    """Make new entries to the electronic log hidden by default.

    This is meant to be active during recording of less important events.
    """
    session.experiment.elog_hidden = hidden


@hiddenusercommand
@parallel_safe
def _LogAttach(description, paths, names):
    """Attach one or more files to the electronic logbook.

    The file *paths* should be temporary file names accessible from the machine
    on which the electronic logbook daemon runs (i.e. on a common network
    share).  They will be moved to the logbook using the given *names*.

    This is intended to be used from the NICOS GUI, from the respective
    dialogs.
    """
    session.elogEvent('attachment', (description, paths, names))


@hiddenusercommand
@parallel_safe
def _LogAttachImage(description, paths, extensions, names):
    """Attach an image to the electronic logbook.

    The same image, may be sent in different formats, e.g. png and svg.
    The elog handler can use one or multiple files, e.g. skip unsupported file
    formats.

    The file *paths* should be temporary file names accessible from the machine
    on which the electronic logbook daemon runs (i.e. on a common network
    share).  They will be moved to the logbook using the given *names* with
    their corresponding filename **extensions**.

    This is intended to be used from the NICOS GUI, from the respective
    dialogs.
    """
    session.elogEvent('image', (description, paths, extensions, names))


@usercommand
@parallel_safe
def SetErrorAbort(abort):
    """Set behavior on unhandled errors in commands.

    If *abort* is True, abort script and notify.

    If it is False, report the error, notify and continue with the next
    command.
    """
    session.experiment.errorbehavior = abort and 'abort' or 'report'


@usercommand
def pause(prompt='Script paused by pause() command.'):
    """Pause the script until a user confirms continuation.

    The *prompt* text is shown to the user, with the choice to continue or
    abort the script.

    Any connected client with the same or higher user level as the one
    executing the script can do this, in first come, first served fashion.
    """
    session.pause(prompt)


@usercommand
@helparglist('[prompt, [validator, [default]]]')
def userinput(prompt='The script requests user input:',
              validator=str, default=Ellipsis):
    """Pause the script and ask for input, which is returned.

    The *prompt* text is shown to the user, with the choice to enter a value
    or abort the script.

    For advanced users: If *validator* is given, it restricts the choices
    accordingly; you can use any validator from `nicos.core.params`.  The
    *default*, if given, is pre-filled in the input field.  Without a default,
    this command will raise an error in dry-run mode.

    Any connected client with the same or higher user level as the one
    executing the script can do this, in first come, first served fashion.

    Examples:

    >>> dist = userinput('How far (in cm) is the sample from the detector?',
    ...                  float, 15)

    >>> from nicos.core.params import oneof
    >>> if userinput('How do you want to continue:',
    ...              oneof('measure', 'calibrate')) == 'measure':
    ...     ...
    """
    result = session.userinput(prompt, validator, default)
    if result is Ellipsis:
        raise NicosError('no input provided to userinput(), cannot continue')
    return result


@usercommand
@helparglist('[message]')
def abort(message=None):
    """Abort any running script with a given message."""
    if message:
        session.log.warning('Aborting script: %s', message)
    session.abortScript()
