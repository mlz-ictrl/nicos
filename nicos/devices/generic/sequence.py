#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Devices performing an unlocking/locking sequence upon moving."""

import sys
import time
from datetime import timedelta
from time import time as currenttime

from nicos import session
from nicos.core import Attach, Device, DeviceMixinBase, LimitError, \
    Measurable, MoveError, Moveable, NicosError, Override, Param, \
    ProgrammingError, Readable, SIMULATION, anytype, none_or, status, tupleof

from nicos.core.utils import devIter
from nicos.pycompat import reraise
from nicos.utils import createThread


class StopSequence(Exception):
    """Custom exception class to stop a sequence."""


class SequenceItem(object):
    """Base class for actions of a sequence.

    All methods do their Job or raise an NicosError (or a derived Exception)
    on errors. Derived classes need to define their own __init__ and check
    number and names of arguments and call this class' __init__ then.

    Derived Classes/Items are encouraged to also define a __repr__ returning
    a NICOS-command aquivalent to the action performed.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def check(self):
        """Check if the action can be performed.

        This may check arguments/types/... and normally raises an Error if
        something is wrong.
        """

    def run(self):
        """Initate an action, define in derived classes."""

    def retry(self, amount):
        """Retry the start of an already failed action."""
        for _ in range(amount):
            try:
                self.run()
                return
            except Exception:
                pass

    def isCompleted(self):
        """Check for completion of the initiated action.

        Should return True if completed or False if not yet completed,
        allowing a polling mode.
        """
        return True

    def stop(self):
        """Interrupt the action started by run()."""


class SeqDev(SequenceItem):
    """Move the given device to the given target and waits until it is there.

    Also works for Measurables/detectors by supporting keyworded arguments.
    If you want to be able to interrupt the movement, set the keyword argument
    ``stoppable=True`` when calling the constructor.
    """

    def __init__(self, dev, target, stoppable=False):
        SequenceItem.__init__(self, dev=dev, target=target, stoppable=stoppable)

    def check(self):
        res = self.dev.isAllowed(self.target)
        if not res[0]:
            raise LimitError(self.dev, res[1])

    def run(self):
        self.dev.start(self.target)

    def isCompleted(self):
        # dont wait on fixed devices
        if hasattr(self.dev, 'fixed') and self.dev.fixed:
            return True
        done = self.dev.isCompleted()
        if done:
            self.dev.finish()
        return done

    def __repr__(self):
        return '%s -> %s' % (self.dev.name, self.dev.format(self.target))

    def stop(self):
        if self.stoppable:
            self.dev.stop()


class SeqParam(SequenceItem):
    """Set a Parameter of a Device and check its value once."""

    def __init__(self, dev, paramname, value):
        SequenceItem.__init__(self, dev=dev, paramname=paramname, value=value)

    def run(self):
        setattr(self.dev, self.paramname, self.value)
        if not getattr(self.dev, self.paramname) == self.value:
            raise NicosError('Setting Parameter %s of dev %s to %r failed!' % (
                self.paramname, self.dev, self.value))

    def __repr__(self):
        return '%s.%s -> %r' % (self.dev.name, self.paramname, self.value)


class SeqMethod(SequenceItem):
    """Call a method of an object with the given arguments.

    Useful for e.g. fix/release or other usermethods.
    """

    def __init__(self, obj, method, *args, **kwargs):
        SequenceItem.__init__(self, obj=obj, method=method, args=args,
                              kwargs=kwargs)

    def check(self):
        if not hasattr(self.obj, self.method):
            raise AttributeError('method %r.%s does not exist!' %
                                 (self.obj, self.method))

    def run(self):
        getattr(self.obj, self.method)(*self.args)

    def __repr__(self):
        if isinstance(self.obj, Device):
            name = self.obj.name
        else:
            name = repr(self.obj)
        return '%s %s' % (name, self.method)


class SeqCall(SequenceItem):
    """Call a given function with given arguments."""

    def __init__(self, func, *args, **kwargs):
        SequenceItem.__init__(self, func=func, args=args, kwargs=kwargs)

    def run(self):
        self.func(*self.args, **self.kwargs)

    def __repr__(self):
        return '%s' % self.func.__name__


class SeqSleep(SequenceItem):
    """Wait a certain time, given in seconds."""

    def __init__(self, duration, reason=None):
        SequenceItem.__init__(self, duration=duration, reason=reason)
        self.stopflag = False
        self.endtime = 0

    def run(self):
        if self.duration > 3:
            session.beginActionScope(self.reason or 'Sleeping %s (H:M:S)' %
                                     timedelta(seconds=self.duration))
        self.endtime = currenttime() + self.duration

    def isCompleted(self):
        if not self.stopflag and self.endtime > currenttime():
            # arbitrary choice of max 5s
            time.sleep(min(5, self.endtime - currenttime()))
            return False
        if self.duration > 3:
            session.endActionScope()
        return True

    def stop(self):
        self.stopflag = True

    def __repr__(self):
        if self.endtime:
            # already started, __repr__ is used for updating status strings.
            return str(timedelta(
                seconds=round(self.endtime - currenttime())))
        else:
            return '%g s' % self.duration


class SeqNOP(SequenceItem):
    """Do nothing.

    May be needed in cases where _<action>Failed Hooks
    decide upon the step number, what to do.
    """

    def __init__(self):
        SequenceItem.__init__(self)

    def __repr__(self):
        return '---'  # any other NICOS-NOP ?


class SequencerMixin(DeviceMixinBase):
    """Mixin performing a given sequence to reach a certain value.

    The Sequence is a list of :class:`SequenceItems` or tuples of those.
    A SequenceItem provides check, run and isCompleted methods which are
    executed in this order. A tuple of :class:`SequenceItems` gets each of
    those methods called on each member first, then the next method, allowing
    to perform 'parallel' executed actions.

    If some action fail, a ``_<action>Failed`` hook is called.
    If this function raises, the sequence is aborted.
    For other allowed values, see docstring of those methods.

    Usually, it is fine to derive from :class:`BaseSequencer`.
    """

    parameters = {
        '_seq_status': Param('Status of the currently executed sequence, '
                             'or (status.OK, idle)', settable=True,
                             mandatory=False, userparam=False,
                             default=(status.OK, 'idle'), no_sim_restore=True,
                             type=tupleof(int, str)),
    }

    parameter_overrides = {
        'unit': Override(mandatory=False, default=''),
    }

    _seq_thread = None
    _seq_stopflag = False
    _seq_was_stopped = False
    _honor_stop = True      # may be needed to be false in special cases....

    hardware_access = False

    def _set_seq_status(self, newstatus=status.OK, newstatusstring='unknown'):
        """Set the current sequence status."""
        oldstatus = self.status()
        self._seq_status = (newstatus, newstatusstring.strip())
        self.log.debug(self._seq_status[1])
        if self._cache and oldstatus != self._seq_status:
            self._cache.put(self, 'status', self._seq_status,
                            time.time(), self.maxage)

    def _seq_is_running(self):
        return self._seq_thread and self._seq_thread.is_alive()

    def _startSequence(self, sequence):
        """Check and start the sequence."""
        # check sequence
        for i, step in enumerate(sequence):
            if not hasattr(step, '__iter__'):
                step = (step, )
                sequence[i] = step
            for action in step:
                try:
                    action.check()
                except Exception as e:
                    self.log.error('action.check for %r failed with %r',
                                   action, e)
                    self.log.debug('_checkFailed returned %r',
                                   self._checkFailed(i, action,
                                                     sys.exc_info()))
                    # if the above does not raise, consider this as OK

        if self._seq_is_running():
            raise ProgrammingError(self, 'sequence is still running!')

        # debug hint:
        if self.loglevel == 'debug':
            self.log.debug('generated sequence has %d steps:', len(sequence))
            for i, step in enumerate(sequence):
                self.log.debug(' - step %d:', i + 1)
                for action in step:
                    self.log.debug('   - Action: %r', action)

        self._set_seq_status(status.BUSY, '')

        self._asyncSequence(sequence)

    def _asyncSequence(self, sequence):
        """Start a thread to execute the sequence."""
        self._seq_stopflag = False
        self._seq_was_stopped = False
        self._seq_thread = createThread('sequence', self._run, (sequence,))

    def _run(self, sequence):
        """The thread performing the sequence.

        May be overwritten in derived classes needed the status sync between
        poller and daemon but don't want to use the actual sequencing routine.
        """
        try:
            self._sequence(sequence)
        finally:
            self._seq_stopflag = False

    def _sequence(self, sequence):
        """The Sequence 'interpreter', stepping through the sequence."""
        try:
            self.log.debug('Performing Sequence of %d steps', len(sequence))
            for i, step in enumerate(sequence):
                self._set_seq_status(status.BUSY, 'action %d: ' %
                                     (i + 1) + '; '.join(map(repr, step)))
                # start all actions by calling run and if that fails, retry
                for action in step:
                    self.log.debug(' - Action: %r', action)
                    try:
                        action.run()
                    except Exception as e:
                        # if this raises, abort the sequence...
                        self.log.warning('action %d (%r) failed',
                                         i + 1, action, exc=1)
                        code = self._runFailed(i, action, sys.exc_info())
                        self.log.debug('_runFailed returned %r', code)
                        if code:
                            try:
                                action.retry(code)
                            except Exception as e:
                                self.log.debug('action.retry failed with '
                                               '%r', e)
                                ret = self._retryFailed(i, action,
                                                        code, sys.exc_info())
                                self.log.debug('_retryFailed returned %r', ret)

                # wait until all actions are finished
                waiters = set(step)
                while waiters:
                    t = currenttime()
                    self._set_seq_status(status.BUSY, 'waiting: ' +
                                         '; '.join(map(repr, waiters)))
                    for action in list(waiters):
                        try:
                            if action.isCompleted():
                                # wait finished
                                waiters.remove(action)
                        except Exception as e:
                            self.log.debug('action.isCompleted failed with '
                                           '%r', e)
                            # if this raises, abort the sequence...
                            code = self._waitFailed(i, action, sys.exc_info())
                            self.log.debug('_waitFailed returned %r', code)
                            if code:
                                if action.isCompleted():
                                    waiters.remove(action)
                    if self._seq_stopflag:
                        self.log.debug('Stopflag caught!')
                        self._seq_was_stopped = True
                        for dev in waiters:
                            dev.stop()
                        break
                    # 0.1s - code execution time
                    t = .1 - (currenttime() - t)
                    if waiters and t > 0:
                        time.sleep(t)

                # stop if requested
                if self._seq_stopflag:
                    self._seq_was_stopped = True
                    self.log.debug('stopping actions: %s',
                                   '; '.join(map(repr, step)))
                    self._set_seq_status(status.BUSY, 'stopping at step %d: ' %
                                         (i + 1) + '; '.join(map(repr, step)))
                    try:
                        for action in step:
                            failed = []
                            # stop all actions, record errors
                            try:
                                action.stop()
                            except Exception as e:
                                self.log.debug('action.stop failed with '
                                               '%r', e)
                                failed.append((action, e))
                            # signal those errors, captured earlier
                            for ac, e in failed:
                                ret = self._stopFailed(i, ac, sys.exc_info())
                                self.log.debug('_stopFailed returned %r', ret)
                    finally:
                        self._stopAction(i)
                        self._set_seq_status(status.NOTREACHED,
                                             'operation interrupted at step '
                                             '%d: ' % (i + 1) +
                                             '; '.join(map(repr, step)))
                        self.log.debug('stopping finished')
                    break

            if not self._seq_stopflag:
                self.log.debug('Sequence finished')
                self._set_seq_status(status.OK, 'idle')

        except NicosError as e:
            self._set_seq_status(status.ERROR, 'error %s upon ' % e +
                                 self._seq_status[1])
            self.log.error(self._seq_status[1], exc=1)
        except Exception as e:
            self.log.error('%s', e, exc=1)

    def doFinish(self):
        if self._seq_was_stopped:
            raise StopSequence(self, self._seq_status[1])

    def doStatus(self, maxage=0):
        """Return highest statusvalue."""
        stati = [dev.status(maxage)
                 for dev in devIter(self._getWaiters(), Readable)] + \
                [self._seq_status]
        # sort inplace by first element, i.e. status code
        stati.sort(key=lambda st: st[0])
        # select highest (worst) status
        # if no status is 'worse' then _seq_status, this is _seq_status
        _status = stati[-1]
        if self._seq_is_running():
            return max(status.BUSY, _status[0]), _status[1]
        return _status

    def doStop(self):
        if self._honor_stop:
            self._seq_stopflag = True

    def doReset(self):
        if self._seq_is_running():
            self.log.error('cannot reset the device because it is busy, '
                           'please stop it first.')
            return
        self._seq_was_stopped = False
        self._set_seq_status(status.OK, 'idle')

    #
    # Hooks
    #

    def _generateSequence(self, *args, **kwargs):
        """Return the target-specific sequence as a list of steps.

        Each step is a SequenceItem or a tuple thereof.
        SequenceItems (also called actions) are "executed" one after another in
        a "lock-step fashion" while the actions grouped together in a tuple are
        tried to execute in parallel.

        The actual action performed depends on the implementation of the
        `SequenceItem`.

        Default is to raise an `NotImplementedError`
        """
        raise NotImplementedError('put a proper _generateSequence '
                                  'implementation here!')

    def _stopAction(self, nr):
        """Called whenever a running sequence is 'stopped'.

        Stopping of the currently performing actions is automatically done
        before.  If additional actions are required to get the Device into a
        stable state, place them here.

        Default to a NOP.
        """

    def _checkFailed(self, step, action, exc_info):
        """Called whenever an action check failed.

        This may raise an Exception to end the sequence or return
        anything to ignore this.

        Default is to re-raise the given exception.
        """
        reraise(*exc_info)

    def _runFailed(self, step, action, exc_info):
        """Called whenever an action run failed.

        This may raise an Exception to end the sequence or return
        an integer. If that integer is > 0, the actions retry is called.

        Default is to re-raise the given exception.
        """
        reraise(*exc_info)

    def _retryFailed(self, step, action, code, exc_info):
        """Called whenever an actions retry failed.

        This may raise an Exception to end the sequence or return
        anything to ignore this.

        Default is to re-raise the given exception.
        """
        reraise(*exc_info)

    def _waitFailed(self, step, action, exc_info):
        """Called whenever a wait failed.

        This may raise an Exception to end the sequence or return
        anything to ignore this.
        If the returned value evaluates to a boolean True, the wait
        is retried once. If it still fails, the sequence is aborted.

        Default is to re-raise the given exception.
        """
        reraise(*exc_info)

    def _stopFailed(self, step, action, exc_info):
        """Called whenever a stop failed with an exception.

        Default is to re-raise the exception.
        """
        reraise(*exc_info)


class BaseSequencer(SequencerMixin, Moveable):
    """Moveable performing a sequence to reach a certain value.

    Classes deriving from this need to implement this method:

    .. automethod:: _generateSequence(target)

    and define needed attached_devices.

    Also, a `doRead()` method must be implemented.  `doStatus()` may need to be
    overridden in special cases.
    """

    def doStart(self, target):
        """Generate and start a sequence if non is running.

        Just calls ``self._startSequence(self._generateSequence(target))``
        """
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise MoveError(self, 'Cannot start device, sequence is still '
                                      'running (at %s)!' % self._seq_status[1])
        self._startSequence(self._generateSequence(target))


class LockedDevice(BaseSequencer):
    """A "locked" device, where each movement of the underlying device must be
    surrounded by moving another device (the "lock") to some value and back
    after the movement of the main device.

    The "lock" is moved to the `unlockvalue` before moving the main device.
    After the main device has moved successfully, the lock is moved either back
    to its previous value, or if `lockvalue` is not ``None``, to the
    `lockvalue`.

    If an error occurs while moving the main device, the lock is not moved back
    to "locked" position.  The error must be resolved first to restore
    integrity of the device arrangement.
    """

    attached_devices = {
        'device': Attach('Moveable device which is protected by the lock',
                         Moveable),
        'lock': Attach('The lock, protecting the device', Moveable),
    }

    parameters = {
        'unlockvalue': Param('The value for the lock to unlock the moveable',
                             mandatory=True, type=anytype),
        'keepfixed': Param('Whether to fix lock device if not moving',
                           default=False, type=bool),
        'lockvalue': Param('Value for the lock after movement, default None'
                           ' goes to previous value',
                           default=None, type=none_or(anytype)),
    }

    def _generateSequence(self, target, *args, **kwargs):
        device = self._attached_device
        lock = self._attached_lock
        seq = []

        if self.keepfixed:
            # release lock first
            seq.append(SeqMethod(lock, 'release'))

        # now move lock to unlockvalue
        seq.append(SeqDev(lock, self.unlockvalue))

        if self.keepfixed:
            # fix lock again
            seq.append(SeqMethod(lock, 'fix', 'fixed unless %s moves' % self))

        seq.append(SeqDev(device, target))

        if self.keepfixed:
            # release lock again
            seq.append(SeqMethod(lock, 'release'))

        # now move lock to lockvalue
        seq.append(SeqDev(lock,
                          self.lockvalue or lock.target or lock.doRead(0)))

        if self.keepfixed:
            # fix lock again
            seq.append(SeqMethod(lock, 'fix', 'fixed unless %s moves' % self))

        return seq

    def doRead(self, maxage=0):
        return self._attached_device.read(maxage)

    def doIsAllowed(self, target):
        return self._attached_device.isAllowed(target)


class MeasureSequencer(SequencerMixin, Measurable):
    """Measurable performing a sequence necessary for the measurement.

    Classes deriving from this need to implement this method:

    .. automethod:: _generateSequence()

    and define needed attached_devices.

    Also, a `doRead()` method must be implemented.  `doStatus()` may need to be
    overridden in special cases.

    """

    def doStart(self):
        """Generate and start a sequence if non is running.

        Just calls ``self._startSequence(self._generateSequence())``

        """
        if self._seq_is_running():
            if self._mode == SIMULATION:
                self._seq_thread.join()
                self._seq_thread = None
            else:
                raise NicosError(self, 'Cannot start device, it is still busy')
        self._startSequence(self._generateSequence())
