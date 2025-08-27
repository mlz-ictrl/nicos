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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

"""Module for simple device-related user commands."""

import ast
import builtins
import sys
import time

from nicos import __version__ as nicos_revision, nicos_version, session
from nicos.commands import helparglist, hiddenusercommand, parallel_safe, \
    usercommand
from nicos.commands.basic import sleep
from nicos.core import INFO_CATEGORIES, SIMULATION, AccessError, CanDisable, \
    Device, DeviceAlias, DeviceMixinBase, HasLimits, HasOffset, Measurable, \
    Moveable, NicosTimeoutError, Readable, UsageError, Waitable, formatStatus, \
    multiWait
from nicos.core.errors import NicosError
from nicos.core.status import BUSY, OK
from nicos.devices.abstract import CanReference, MappedMoveable
from nicos.protocols.daemon import BREAK_AFTER_STEP
from nicos.utils import createThread, number_types, parseDateString, \
    printTable, tupelize
from nicos.utils.timer import Timer

__all__ = [
    'move', 'drive', 'maw', 'switch', 'wait', 'read', 'status', 'stop',
    'reset', 'set', 'get', 'getall', 'setall', 'info', 'fix', 'release',
    'unfix', 'adjust', 'version', 'history', 'limits', 'resetlimits',
    'reference', 'ListParams', 'ListMethods', 'ListDevices', 'waitfor',
    'waitfor_stable', 'enable', 'disable', 'rmove', 'rmaw',
]


def _devposlist(dev_pos_list, cls):
    if not dev_pos_list:
        raise UsageError('at least one device and position must be given')
    if len(dev_pos_list) % 2 != 0:
        raise UsageError('a position must be given for every device')
    return [(session.getDevice(dev, cls), pos) for (dev, pos) in
            tupelize(dev_pos_list)]


def _basemove(dev_pos_list, waithook=None, poshook=None):
    """Core move function.

    Options:

    *waithook*: a waiting function that gets the list of started devices
    *poshook*: gets device and requested pos, returns modified position
    """
    movelist = []
    errors = []

    for dev, pos in _devposlist(dev_pos_list, Moveable):
        try:
            if poshook:
                pos = poshook(dev, pos)
            pos = dev._check_start(pos)
            if pos is not Ellipsis:
                movelist.append((dev, pos))
        except (NicosError, ValueError, TypeError):
            errors.append((dev, sys.exc_info()))

    if errors:
        for (dev, exc_info) in errors[:-1]:
            dev.log.error(exc_info=exc_info)
        raise errors[-1][1][1]

    devs = []
    for (dev, pos) in movelist:
        dev.log.info('moving to %s', dev.format(pos, unit=True))
        dev._start_unchecked(pos)
        devs.append(dev)
    if waithook:
        waithook(devs)


def _wait_hook(devs):
    """Default wait hook"""
    values = multiWait(devs)
    for dev in devs:
        dev.log.info('at %20s %s', dev.format(values[dev]), dev.unit)


def _rmove_poshook(dev, delta):
    """Pos hook for relative motions"""
    if dev.doStatus(0)[0] == BUSY:
        raise UsageError('Device %r is busy' % dev)
    if isinstance(dev, MappedMoveable):
        raise UsageError('Relative motion on mapped device %s is undefined' %
                         dev)
    curpos = dev.read(0)
    # if the target is reached (within precision), use it as the base for
    # the relative movement to avoid accumulating small errors
    curpos = dev.target if dev.isAtTarget(curpos) else curpos
    if isinstance(curpos, str):
        raise UsageError('Device %s cannot be used with relative movement' %
                         dev)
    try:
        return curpos + delta
    except Exception:
        raise UsageError('Device %s cannot be used with relative movement or '
                         'wrong delta type %r' % (dev, delta)) from None


@usercommand
@helparglist('dev1, pos1, ...')
@parallel_safe
def move(*dev_pos_list):
    """Start moving one or more devices to a new position.

    This command will return immediately without waiting for the movement to
    finish.  For "move and wait", see `maw()`.

    The command can be used multiple times to move devices in parallel.
    Examples:

    >>> move(dev1, 10)    # start device1
    >>> move(dev2, -3)    # start device2

    However, in this case a shorter version is available:

    >>> move(dev1, 10, dev2, -3)   # start two devices "in parallel"

    .. note::

       There is no collision detection and no guarantee of synchronicity of
       the movements.  The devices are started quickly one after the other.

    After starting devices it is often required to wait until the movements
    are finished.  This can be done with the `wait()` command:

    >>> wait(dev1, dev2)          # now wait for all of them

    Again, there is a shorter version available for the whole sequence:

    >>> maw(dev1, 10, dev2, -3)   # move devices in parallel and wait for both
    """
    _basemove(dev_pos_list)


@usercommand
@helparglist('dev, pos, ...')
def rmove(*dev_pos_list):
    """Move one or more devices by a relative amount.

    The new target position is calculated from the device's current target
    position (if known and reached), or the current actual position.

    This command will return immediately without waiting for the movement to
    finish.  For "rmove and wait", see `rmaw()`.

    Examples:

    >>> rmove(dev1, 10)    # start dev1 moving 10 units in the `+` direction
    >>> rmove(dev1, 10, dev2, -3)    # start both dev1 and dev2

    For further help see also `move()`.
    """
    _basemove(dev_pos_list, poshook=_rmove_poshook)


@hiddenusercommand
@helparglist('dev, pos, ...')
@parallel_safe
def drive(*dev_pos_list):
    """Move one or more devices to a new position.  Same as `move()`."""
    move(*dev_pos_list)


@usercommand
@helparglist('dev, pos, ...')
def maw(*dev_pos_list):
    """Move one or more devices to a new position and wait for them.

    The command is a combination of the `move()` and `wait()` commands.  After
    starting the movement of the device(s) the command waits until motion of
    the device(s) is completed.

    A typical application is a sequence of movements, or waiting for a certain
    device (e.g. temperature) to arrive at its target setpoint.

    >>> maw(dev1, 10)  # move a device to a new position and wait

    This is the shorter version of the following commands:

    >>> move(dev1, 10)
    >>> wait(dev1)

    The command can also be used with multiple devices.  Examples:

    >>> maw(dev1, 10, dev2, -3)    # move two devices in parallel and wait

    .. note::

        The command will wait until **all** devices have finished their
        movement.
    """
    _basemove(dev_pos_list, waithook=_wait_hook)


@usercommand
@helparglist('dev, delta, ...')
def rmaw(*dev_pos_list):
    """Move one or more devices by relative amounts and wait for them.

    The command is a combination of the `rmove()` and `wait()` commands.  After
    starting the movement of the device(s) the command waits until motion of
    the device(s) is completed. Example:

    >>> rmaw(dev1, 10)  # move dev1 10 units in the `+` direction and wait

    This is the shorter version of the following commands:

    >>> rmove(dev1, 10)
    >>> wait(dev1)

    The command can also be used with multiple devices.  Examples:

    >>> rmaw(dev1, 10, dev2, -3)    # move two devices in parallel and wait

    For further help see also `maw()`.
    """
    _basemove(dev_pos_list, poshook=_rmove_poshook, waithook=_wait_hook)


@hiddenusercommand
@helparglist('dev, pos, ...')
def switch(*dev_pos_list):
    """Move one or more devices to a new position and wait until motion
    of all devices is completed.  Same as `maw()`."""
    maw(*dev_pos_list)


@usercommand
@helparglist('dev, ...')
def wait(*devlist):
    """Wait until motion/action of one or more devices is complete.

    This command can wait until a device, a list of devices or all devices have
    finished their movement or action, i.e. the status of the devices is no
    longer "busy".

    The "busy" status is device specific, but in general a moveable device,
    started by the `move()` command, is going to the target, while a detector
    device, e.g. started by the `count()` command, is counting.

    The following example waits for all devices, which can be used to ensure
    that no device is moving or counting before the next step starts.

    >>> wait()

    The next example waits for the T (typically the sample temperature) and B
    (typically the magnetic field):

    >>> wait(T, B)    # wait for T and B devices

    Sometimes the user wants to wait an additional time after all given devices
    left the "busy" state. This can be given by a number (the unit is seconds).
    The next example waits until T leaves the "busy" state and thereafter 60
    seconds before the next command is executed.

    >>> wait(T, 60)   # wait for the T device, then another 60 seconds

    The same can be done with the following sequence:

    >>> wait(T)
    >>> sleep(60)

    .. note::
        The difference is that this version can be interrupted between the
        `wait()` and `sleep()` commands.
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
            dev.log.info('at %20s %s', dev.format(value), dev.unit)


@usercommand
@helparglist('dev, condition, [timeout]')
def waitfor(dev, condition, timeout=86400):
    """Wait for a device until a condition is fulfilled.

    Convenience function to avoid writing code like this:

    >>> while not motor.read() < 10:
    ...     sleep(0.3)

    which now can be written as:

    >>> waitfor(motor, '< 10')

    The supported conditions are [#]_:

    - '<', '<=', '==', '!=', '>=', '>' with a value
    - 'is False', 'is True', 'is None'
    - 'in list', where list could be a Python list or tuple

    An optional timeout value can be added, which denominates the maximum time
    the command will wait (in seconds).  If the timeout value is reached, an
    error will be raised.  The default timeout value is 86400 seconds (1 day).
    Example:

    >>> waitfor(T, '< 10', timeout=3600)

    Will wait a maximum of 1 hour for T to get below 10.

    .. note::

       In contrast to the `wait()` command this command will not only wait
       until the target is reached.  You may define also conditions which
       represent intermediate states of a movement or you may wait on
       external trigger signals and so on.

    .. [#] The device value, determined by ``dev.read()``, will be added in
       front of the condition, so the resulting conditions is:

        >>> dev.read() < 10

       The condition parameter will be given as a simple comparison to
       the value of the device.
    """
    dev = session.getDevice(dev, Readable)
    full_condition = '_v %s' % condition

    try:
        ast.parse(full_condition)
    except Exception:
        raise UsageError('Could not parse condition %r' % condition) from None

    if session.mode == SIMULATION:
        return
    cond_fulfilled = False

    def check(tmr):
        nonlocal cond_fulfilled

        session.breakpoint(BREAK_AFTER_STEP)  # allow break and continue here
        cond_fulfilled = eval(full_condition, {}, {'_v': dev.read(0)})
        if cond_fulfilled:
            session.log.info("Waiting for '%s %s' finished", dev, condition)
            tmr.stop()

    session.beginActionScope('Waiting until %s %s' % (dev, condition))
    try:
        tmr = Timer(timeout if timeout else 86400)  # max wait time 1 day
        tmr.wait(dev._base_loop_delay * 3, check)
    finally:
        if not cond_fulfilled:
            raise NicosTimeoutError(dev, "Waiting for '%s %s' timed out" %
                                    (dev, condition))
        session.endActionScope()


@usercommand
@helparglist('device, target, accuracy, time_stable, [timeout]')
def waitfor_stable(device, target, accuracy, time_stable, timeout=3600):
    """Wait for the device to be within a certain range of the target value
    for a defined continuous number of seconds.

    If the device takes too long to stabilise then the action will timeout.

    Example:

    >>> waitfor_stable(dev1, 10, 1, 30, 600)

    will wait until the device position is between 9 and 11 for a continous
    period of 30 seconds, but will exit after 10 minutes if
    stability is not reached.

    .. note::

       The default timeout is an hour (3600 s).
    """
    if session.mode == SIMULATION:
        session.clock.tick(time_stable)
        return

    dev = session.getDevice(device)
    if time_stable >= timeout:
        raise UsageError('The timeout has to be greater than the stable time')

    in_range_tmr = Timer()
    in_range_tmr.stop()  # Timer starts automatically
    cond = f"'{dev} is stable at {target} (+/-{accuracy}) for {time_stable} s'"
    cond_fulfilled = False

    def check(tmr, target, accuracy, time_stable):
        nonlocal cond_fulfilled

        session.breakpoint(BREAK_AFTER_STEP)  # allow break and continue here

        if abs(target - dev.read(0)) <= accuracy:
            if not in_range_tmr.is_running():
                in_range_tmr.start(time_stable)
                session.log.info('%s is within range, waiting %s seconds for '
                                 'it to stabilise', device, time_stable)
        else:
            if in_range_tmr.is_running():
                session.log.info('%s is no longer in range', device)
            in_range_tmr.stop()

        cond_fulfilled = bool(
            in_range_tmr.is_running() and
            in_range_tmr.remaining_time() <= dev._base_loop_delay)

        if cond_fulfilled:
            session.log.info('Waiting for %s finished', cond)
            in_range_tmr.stop()
            tmr.stop()

    session.beginActionScope(f'Waiting until {cond}')
    try:
        # max wait time 1 hour if not set
        tmr = Timer(timeout if timeout else 3600)
        tmr.wait(dev._base_loop_delay, check, (target, accuracy, time_stable))
    finally:
        if not cond_fulfilled:
            raise NicosTimeoutError(dev, f'Waiting for {cond} timed out.')
        session.endActionScope()


@usercommand
@helparglist('[dev, ...]')
@parallel_safe
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
                dev.log.info('at %20s %-5s  (target: %20s %s)',
                             dev.format(value), unit, dev.format(target), unit)
            else:
                dev.log.info('at %20s %-5s', dev.format(value), unit)
        else:
            dev.log.info('at %20s %-5s', dev.format(value), unit)


@usercommand
@helparglist('[dev, ...]')
@parallel_safe
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
                dev.log.info('status is %s', formatStatus(status))
            else:
                dev.log.warning('status is %s', formatStatus(status))


@usercommand
@helparglist('[dev, ...]')
@parallel_safe
def stop(*devlist):
    """Stop one or more or all moving devices.

    If no device is given, stop all stoppable devices in parallel.

    Examples:

    >>> stop(phi)       # stop the phi device
    >>> stop(phi, psi)  # stop the phi and psi devices
    >>> stop()          # stop all devices

    .. note::

       A device can be configured to ignore the `stop()` call (stop all
       devices) by setting the
       `~nicos.core.device.Moveable.ignore_general_stop` device parameter to
       ``True``.

       However, if the device is stopped explicitly via `stop(dev)`, it will
       still stop.
    """

    def stopdev(dev):
        try:
            dev.stop()
            if not stop_all or dev in stoplist:
                dev.log.info('stopped')
        except AccessError:
            # do not warn about devices we cannot access if they were not
            # explicitly selected
            pass
        except Exception:
            dev.log.warning('error while stopping', exc=1)
        finally:
            finished.append(dev)

    stop_all = not devlist

    if stop_all:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname],
                                 (Moveable, Measurable))]
        stoplist = {dev for dev in devlist
                    if session.cache.get_explicit(dev, 'status',
                                                  (None,))[2][0] == BUSY}
        skipset = {dev for dev in stoplist
                   if isinstance(dev, Moveable) and dev.ignore_general_stop}
        devlist = [dev for dev in stoplist if dev not in skipset]
    else:
        stoplist = ()
        skipset = ()

    finished = []
    for dev in devlist:
        dev = session.getDevice(dev)
        createThread('device stopper %s' % dev, stopdev, (dev,))
    while len(finished) != len(devlist):
        session.delay(Device._base_loop_delay)
    if stop_all:
        if skipset:
            # TODO: it would be nice to let here a popup window appear
            # in the GUI, where the skipped devices are shown and with
            # buttons to stop the skipped devices individually
            aliases = {}
            for dev in list(skipset):
                if isinstance(dev, DeviceAlias):
                    aliases.setdefault(dev.alias, []).append(dev.name)
                    skipset.discard(dev)

            session.log.warning('all devices stopped, except:')
            session.log.warning(' ')
            stopargs = []
            for dev in skipset:
                if dev.name in aliases:
                    name = f"{dev.name} ({', '.join(aliases[dev.name])})"
                    stopargs.append(aliases[dev.name][0])
                else:
                    name = dev.name
                    stopargs.append(name)
                session.log.warning('%s is still moving from %s to %s %s',
                                 name, dev.format(dev.read(0)),
                                 dev.format(dev.target), dev.unit)
            session.log.warning(' ')
            session.log.warning('these devices are configured to ignore "stop all"')
            session.log.warning('if you really want to stop them, '
                             'you may use stop(%s)', ', '.join(stopargs))
        else:
            session.log.info('all devices stopped')


@usercommand
@helparglist('[dev, ...]')
@parallel_safe
def finish(*devlist):
    """Finish data acquisition for one or more detectors.

    If not device is given, finish all running detectors.

    Examples:

    >>> finish()
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices
                   if isinstance(session.devices[devname], Measurable)]
    for dev in devlist:
        dev.finish()
        dev.log.info('finished')


@usercommand
@helparglist('dev, ...')
@parallel_safe
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
        dev.log.info('reset done, status is now %s', formatStatus(status))


@usercommand
@parallel_safe
def set(dev, parameter, value):  # pylint: disable=redefined-builtin
    """Set a parameter of the device to a new value.

    The following commands are equivalent:

    >>> set(phi, 'speed', 50)

    >>> phi.speed = 50
    """
    dev = session.getDevice(dev)
    try:
        paramconfig = dev._getParamConfig(parameter)
    except KeyError:
        dev.log.error('device has no parameter %r', parameter)
        return
    prevalue = getattr(dev, parameter)
    setattr(dev, parameter, value)
    # if yes, we already got a message
    if not paramconfig.chatty:
        dev.log.info('%s set to %r (was %r)',
                     parameter, getattr(dev, parameter), prevalue)


@usercommand
@parallel_safe
def get(dev, parameter):
    """Print the value of a parameter of the device.

    The parameter value can also be get using attribute syntax,
    i.e. ``dev.param``, to use it programmatically.

    Examples:

    >>> get(phi, 'speed')
    >>> print(phi.speed * 2)
    """
    dev = session.getDevice(dev)
    value = getattr(dev, parameter)
    dev.log.info('parameter %s is %s', parameter, value)


@usercommand
@helparglist('parameter, ...')
@parallel_safe
def getall(*names):
    """List the given parameters for all existing devices that have them.

    Example:

    >>> getall('offset')

    lists the offset for all devices with an "offset" parameter.
    """
    items = []
    for name, dev in sorted(session.devices.items(),
                            key=lambda nd: nd[0].lower()):
        pvalues = []
        for param in names:
            if param in dev.parameters:
                pvalues.append(repr(getattr(dev, param)))
            else:
                pvalues.append(None)
        if any(v is not None for v in pvalues):
            items.append([name] + list(map(str, pvalues)))
    printTable(('device',) + names, items, session.log.info)


@usercommand
@parallel_safe
def setall(param, value):
    """Set the given parameter to the given value for all devices that have it.

    Example:

    >>> setall('offset', 0)

    set the offset for all devices to zero.
    """
    for dev in session.devices.values():
        if param not in dev.parameters:
            continue
        prevalue = getattr(dev, param)
        try:
            setattr(dev, param, value)
        except Exception:
            dev.log.error('could not set %s', param, exc=1)
        else:
            dev.log.info('%s set to %r (was %r)', param, value, prevalue)


@usercommand
@helparglist('[dev, ...]')
@parallel_safe
def info(*devlist):
    """Print general information of the given device or all devices.

    Information is the device value, status and any other parameters that are
    marked as "interesting" by giving them a category.

    Examples:

    >>> info()           # show all information
    >>> info(Sample)     # show information relevant to the Sample object
    """
    if not devlist:
        devlist = [session.devices[devname]
                   for devname in session.explicit_devices]
    bycategory = {}
    for dev in devlist:
        for key, info in dev.info():
            bycategory.setdefault(info.category, []).append(
                (str(dev), key + ':', info.strvalue + ' ' + info.unit))
    for catname, catinfo in INFO_CATEGORIES:
        if catname not in bycategory:
            continue
        session.log.info(catinfo)
        session.log.info('=' * len(catinfo))
        printTable(None, sorted(bycategory[catname]), session.log.info,
                   minlen=8)
        session.log.info()


@usercommand
@helparglist('dev[, reason]')
@parallel_safe
def fix(dev, reason=''):
    """Fix a device, i.e. prevent movement until `release()` is called.

    You can give a reason that is displayed when movement is attempted.
    Example:

    >>> fix(phi, 'will drive into the wall')
    """
    if isinstance(reason, Device):
        raise UsageError('only one device can be given to fix()')
    dev = session.getDevice(dev, Moveable)
    if dev.fix(reason):
        dev.log.info(reason and 'now fixed: ' + reason or 'now fixed')


@usercommand
@helparglist('dev, ...')
@parallel_safe
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
@parallel_safe
def unfix(*devlist):
    """Same as `release()`."""
    return release(*devlist)


@usercommand
@helparglist('dev, ...')
@parallel_safe
def disable(*devlist):
    """Disable one or more devices.

    The exact meaning depends on the device hardware, and not all devices
    can be disabled.  For power supplies, this might switch the output off.

    Example:

    >>> disable(phi)
    """
    for dev in devlist:
        dev = session.getDevice(dev, CanDisable)
        dev.disable()
        dev.log.info('now disabled')


@usercommand
@helparglist('dev, ...')
@parallel_safe
def enable(*devlist):
    """Enable one or more devices.

    The exact meaning depends on the device hardware, and not all devices
    can be disabled.  For power supplies, this might switch the output on.

    Example:

    >>> enable(phi, psi)
    """
    for dev in devlist:
        dev = session.getDevice(dev, CanDisable)
        dev.enable()
        dev.log.info('now enabled')


@usercommand
@helparglist('dev, value[, newvalue]')
@parallel_safe
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
        value, newvalue = dev.read(0), value
    dev.doAdjust(value, newvalue)
    dev.log.info('adjusted to %s, new offset is %.3f',
                 dev.format(newvalue, unit=True), dev.offset)


@usercommand
@helparglist('dev, ...')
@parallel_safe
def version(*devlist):
    """List version info of the device(s).

    If no device is given, the version of nicos-core is printed.
    """
    if devlist:
        for dev in devlist:
            dev = session.getDevice(dev, Device)
            versions = dev.version()
            dev.log.info('relevant versions for this device:')
            printTable(('module/component', 'version'), versions,
                       session.log.info)
    else:
        session.log.info('NICOS version: %s (rev %s)', nicos_version,
                         nicos_revision)


@usercommand
@helparglist('dev[, key][, fromtime][, totime][, interval]')
@parallel_safe
def history(dev, key='value', fromtime=None, totime=None, interval=None):
    """Print history of a device parameter.

    The optional argument *key* selects a parameter of the device.  "value" is
    the main value, and "status" is the device status.

    *fromtime* and *totime* are eithernumbers giving **hours** in the past, or
    otherwise strings with a time specification (see below).  The default is to
    list history of the last hour for "value" and "status", or from the last
    day for other parameters.

    *interval* specifies required minimum time between two adjacent data points.

    For example:

    >>> history(mth)              # show value of mth in the last hour
    >>> history(mth, 48)          # show value of mth in the last two days
    >>> history(mtt, 'offset')    # show offset of mth in the last day

    Examples for time specification:

    >>> history(mth, '1 day')                  # allowed: d/day/days
    >>> history(mth, 'offset', '1 week')       # allowed: w/week/weeks
    >>> history(mth, 'speed', '30 minutes')    # allowed: m/min/minutes

    >>> history(mth, 'speed', '2012-05-04 14:00')  # from that date/time on
    >>> history(mth, 'speed', '14:00', '17:00')    # between 14h and 17h today
    >>> history(mth, 'speed', '2012-05-04', '2012-05-08')  # between two days

    Example for interval specification. Setting 10 seconds as the minumum
    interval between two adjacent data points:

    >>> history(mth, 'speed', '2012-05-04', '2012-05-08', 10) # in [seconds]

    """
    # support calling history(dev, -3600)
    if isinstance(key, str):
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
    hist = session.getDevice(dev, Device).history(key, fromtime, totime,
                                                  interval)
    entries = []
    ltime = time.localtime
    ftime = time.strftime
    for t, v in hist:
        entries.append((ftime('%Y-%m-%d %H:%M:%S', ltime(t)), repr(v)))
    printTable(('timestamp', 'value'), entries, session.log.info)


@usercommand
@helparglist('[dev, ...]')
@parallel_safe
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
            session.log.info(
                '       absolute limits (physical): %8s --- %8s %s',
                dev.format(dev.absmin), dev.format(dev.absmax),
                dev.unit)
            session.log.info(
                '   user limits (including offset): %8s --- %8s %s',
                dev.format(dev.usermin), dev.format(dev.usermax),
                dev.unit)
            session.log.info(
                '                current offset: %8s %s',
                dev.format(dev.offset), dev.unit)
            session.log.info(
                '        => user limits (physical): %8s --- %8s %s',
                dev.format(dev.usermin + dev.offset),
                dev.format(dev.usermax + dev.offset), dev.unit)
        else:
            session.log.info('   absolute limits: %8s --- %8s %s',
                             dev.format(dev.absmin), dev.format(dev.absmax),
                             dev.unit)
            session.log.info('       user limits: %8s --- %8s %s',
                             dev.format(dev.usermin), dev.format(dev.usermax),
                             dev.unit)


@usercommand
@helparglist('dev, ...')
@parallel_safe
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
            dev.log.info('limits reset to absolute limits, new range: '
                         '%8s --- %8s %s',
                         dev.format(dev.userlimits[0]),
                         dev.format(dev.userlimits[1]), dev.unit)
        else:
            dev.log.info('limits kept at: '
                         '%8s --- %8s %s',
                         dev.format(dev.userlimits[0]),
                         dev.format(dev.userlimits[1]), dev.unit)


@usercommand
def reference(dev, *args):
    """Do a reference drive of the device, if possible.

    How the reference drive is done depends on the device settings.
    Example:

    >>> reference(phi)
    """
    try:
        dev = session.getDevice(dev, CanReference)
    except UsageError:
        session.log.error('%s has no reference function', dev)
        return
    newpos = dev.reference(*args)
    dev.log.info('reference drive complete, position is now %s',
                 dev.format(newpos, unit=True))


@usercommand
@parallel_safe
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
    for name, info in sorted(dev.parameters.items()):
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
               items, session.log.info)


@usercommand
@parallel_safe
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
        for name, (args, doc, mcls, is_user) in sorted(cls.methods.items()):
            if cls is mcls and is_user:
                items.append((dev.name + '.' + name + args, cls.__name__, doc))
        for base in cls.__bases__:
            if issubclass(base, (Device, DeviceMixinBase)):
                _list(base)
    _list(dev.__class__)
    dev.log.info('Device methods:')
    printTable(('method', 'from class', 'description'), items,
               session.log.info)


@usercommand
@parallel_safe
def ListDevices():
    """List all currently created devices.

    Example:

    >>> ListDevices()
    """
    session.log.info('All created devices:')
    items = []
    for devname in sorted(session.explicit_devices, key=lambda d: d.lower()):
        dev = session.devices[devname]
        items.append((dev.name, dev.__class__.__name__, dev.description))
    printTable(('name', 'type', 'description'), items, session.log.info)
