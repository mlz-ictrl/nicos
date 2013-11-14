#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""Devices performing an unlocking/locking sequence upon moving"""

import time
import threading

from nicos.core import Param, Override, none_or, anytype, status, \
     NicosError, MoveError, ConfigurationError, ProgrammingError
from nicos.core.device import Moveable, Readable, Measurable, DeviceMixinBase
from nicos.devices.generic import MultiSwitcher, Switcher, ManualMove, \
     VirtualMotor


class LockerMixin(DeviceMixinBase):
    """ Mixin performing an unlock/lock sequence upon moving

    Uses another attached device which acts as a locker.
    Before own movement, locker is maw'ed to the unlockvalue.
    After we have reached our target, the locker is set to the
    value before the movement started or to the lockvalue if not None.
    """

    attached_devices = {
        'lock'     : (Moveable, 'The lock which needs to have a certain value '
                      'to allow movement'),
    }

    parameters = {
        'unlockvalue' : Param('The value for the lock to unlock the moveable',
                              mandatory=True, type=anytype),
        'keepfixed'   : Param('Boolean: Fix devices if not moving?',
                              default=False, type=bool),
        'lockvalue'   : Param('Value for the lock after movement, default None '
                              'goes to previous value',
                              default=None, type=none_or(anytype)),
    }

    _mystatus = (status.OK, 'idle')
    _mystatmaster = None
    _mythread = None
    _mystopflag = False

    def _set_mystatus(self, newstatus=status.OK, newstatusstring='unknown',
                      device=None):
        self._mystatus = (newstatus, newstatusstring)
        self.log.debug(self._mystatus[1])
        if self._cache:
            self._cache.put(self, 'status', self._mystatus,
                            time.time(), self.maxage)
        self._mystatmaster = device

    def _seq_thread(self, target, lockvalue):
        l = self._adevs['lock']

        try:
            if self.keepfixed:
                self._set_mystatus(status.BUSY, 'releasing lock %s' % l)
                l.release()
            if l.fixed:
                raise MoveError(self, 'lockdevice %s is still fixed!' % l)

            if self._mystopflag:
                return

            self._set_mystatus(status.BUSY, 'unlocking %s' % l, l)
            l.start(self.unlockvalue)
            l.wait()

            if self._mystopflag:
                return

            if self.keepfixed:
                self._set_mystatus(status.BUSY, 'fixing lock')
                l.fix('fixed by %s' % self.name)

            if self._mystopflag:
                return

            self._set_mystatus(status.BUSY, 'moving subdevice to target %s' %
                               self.format(target), self)
            Moveable.start(self, target)
            self.doWait(self)

            if self._mystopflag:
                return

            # if the above step raises, it may be unsafe to move the lock!
            if self.keepfixed:
                self._set_mystatus(status.BUSY, 'releasing lock %s' % l)
                l.release()
            if l.fixed:
                raise MoveError(self, 'lockdevice %s is still fixed!' % l)

            if self._mystopflag:
                return

            self._set_mystatus(status.BUSY, 'locking %s' % l, l)
            l.start(lockvalue)
            l.wait()

            if self._mystopflag:
                return

            if self.keepfixed:
                self._set_mystatus(status.BUSY, 'fixing lock')
                l.fix('fixed by %s' % self.name)

            self._set_mystatus(status.OK, 'idle')
            self.log.debug('done')
        except NicosError:
            self._set_mystatus(status.ERROR, 'error upon ' + self._mystatus[1],
                               self._mystatmaster)
            self.log.error(self._mystatus[1], exc=1)
            raise
        finally:
            self._mythread = None
            self._mystopflag = False

    def start(self, target):
        # start is correct here!
        if self._mythread is not None:
            raise MoveError(self, "Can not start device, it is still moving!")
        l = self._adevs['lock']
        # check configurable parameters before starting the thread
        if not self.isAllowed(target)[0]:
            Moveable.start(self, target) # -> shall raise right Error
        if not l.isAllowed(self.unlockvalue)[0]:
            raise ConfigurationError(self, 'illegal unlockvalue %r for device '
                                           '%s' % (self.unlockvalue, l))
        lockvalue = self.lockvalue if self.lockvalue is not None else l.read(0)
        if not l.isAllowed(lockvalue)[0]:
            raise ConfigurationError(self, 'illegal lockvalue %r for device '
                                           '%s' % (lockvalue, l))

        self._mystopflag = False
        self._mythread = threading.Thread(target=self._seq_thread,
                                          args=(target, lockvalue))
        self._mythread.setDaemon(True)
        self._mythread.start()

    move = start

    def wait(self):
        # wait is correct here!
        if self._mythread:
            self._mythread.join()
            self._mythread = None # should be done by the thread itself already
        return Moveable.wait(self)

    def status(self, maxage=0):
        # status is correct here!
        # if our thread is not running, behave 'normal'
        if self._mythread is None:
            return Readable.status(self, maxage)
        # sequence is running, check status
        res = self._mystatmaster.doStatus(maxage)
        s = self._mystatus
        if res[0] < s[0]:
            res = s
        if self._cache:
            self._cache.put(self, 'status', res, time.time(), self.maxage)
        return res

    def stop(self):
        Moveable.stop(self)
        self._adevs['lock'].stop()
        if self._mystatmaster is not None or self._mythread is not None:
            self._set_mystatus(status.NOTREACHED, 'operation interrupted')
        self._mystopflag = True

    def reset(self):
        self._set_mystatus(status.OK, 'idle')
        Moveable.reset(self)


class SequencerMixin(DeviceMixinBase):
    """Mixin performing a given sequence to reach a certain value
    """
    parameters = {
        '_seq_status' : Param('status of the current executes sequence, '
                              'or (100, idle)?', settable=True,
                              mandatory=False, userparam=False,
                              default=(status.OK, 'idle'), type=tuple),
    }

    parameter_overrides = {
        'unit' : Override(mandatory=False, default=''),
    }

    #~ _seq_status = (status.OK, 'idle')
    _seq_statmaster = None
    _seq_thread = None
    _seq_stopflag = False
    _honor_stopflag = True      # may be needed to be false in special cases....

    hardware_access = False

    def _set_seq_status(self, newstatus=status.OK, newstatusstring='unknown',
                      device=None):
        self._seq_status = (newstatus, newstatusstring)
        self.log.debug(self._seq_status[1])
        if self._cache:
            self._cache.put(self, 'status', self._seq_status,
                            time.time(), self.maxage)
        self._seq_statmaster = device

    def _startSequence(self, sequence):
        # check sequence
        seq_ok = True
        for i, step in enumerate(sequence):
            for d, v in step.iteritems():
                if not callable(v) and not d.isAllowed(v):
                    seq_ok = False
                    self.log.error('Error in step %d of sequence, can\'t move '
                                   '%s to %r here.' % (i, d.name, v))
        if not seq_ok:
            raise ConfigurationError(self, 'invalid sequence')

        if self._seq_thread:
            raise ProgrammingError(self, 'sequence is still running!')

        # debug hint:
        if self.loglevel == 'debug':
            self.log.debug('generated Sequence is:')
            for i, step in enumerate(sequence):
                self.log.debug('GenSeq %d of %d:' % (i + 1, len(sequence)))
                for d, v in step.iteritems():
                    if callable(v):
                        self.log.debug(' - call %r (%r)' % (v, d))
                    else:
                        self.log.debug(' - maw(%r, %r)' % (d, v))


        self.BlockingSequence(sequence)

    def BlockingSequence(self, sequence):
        """does a blocking sequence.

        Default is to start a thread which then performs the sequence in a
        'non blocking' way (meaning, if you overwrite doBlockingSequence,
        device.start will return after the sequence is finished)
        """
        self._seq_stopflag = False
        self._seq_thread = threading.Thread(target=self.Sequence,
                                          args=(sequence,))
        self._seq_thread.setDaemon(True)
        self._seq_thread.start()

    def Sequence(self, sequence):
        """performs the 'non-blocking' sequence

        and runs normally in a separate thread.
        If you overwrite this, device.start will return immediately and
        not block until the sequence is finished.
        """
        self._sequence_running = True
        try:
            for i, step in enumerate(sequence):
                self.log.debug('Sequence: step %d of %d' % (i + 1, len(sequence)))
                # start movement
                for d, v in step.iteritems():
                    if callable(v):
                        self.log.debug('calling %r(%r)' % (v, d), d)
                        try:
                            v(d)
                        except NicosError, e:
                            self.log.error(self, e, exc=1)
                    else:
                        self._set_seq_status(status.BUSY,
                                             'moving %s to %r' % (d, v), d)
                        d.start(v)
                # wait
                for d, v in step.iteritems():
                    if self._seq_stopflag and self._honor_stopflag:
                        for d in step:
                            self._set_seq_status(status.BUSY,
                                                 'stopping %s' % d.name, d)
                            d.stop()
                        return
                    # only wait if not fixed to avoid annoying warnings...
                    if not d.fixed:
                        self._set_seq_status(status.BUSY,
                                             'waiting for %s -> %s' % (d.name, v), d)
                        d.wait()
                if self._seq_stopflag and self._honor_stopflag:
                    return

            self._set_seq_status(status.OK, 'idle')
            self.log.debug('done')

        except NicosError:
            self._set_seq_status(status.ERROR, 'error upon ' + self._seq_status[1],
                               self._seq_statmaster)
            self.log.error(self._seq_status[1], exc=1)
            raise
        finally:
            self._seq_thread = None
            self._seq_stopflag = False
            self._sequence_running = False


    def doWait(self):
        if self._seq_thread:
            self._seq_thread.join()

    def doStatus(self, maxage=0):
        return self._seq_status

    def doStop(self):
        if self._seq_statmaster is not None or self._seq_thread is not None:
            self._set_seq_status(status.NOTREACHED,
                                 'operation interrupted at:' + self._seq_status[1])
        self._seq_stopflag = True

    def doReset(self):
        self._set_seq_status(status.OK, 'idle')


class BaseSequencer(SequencerMixin, Moveable):
    """Moveable performing a sequence to reach a certain value

    classes deriving from this need to implement a
    _generateSequence(self, target) method which returns the required sequence
    and a doRead. doStatus may need to be overriden in special cases.
    """
    def doStart(self, target):
        if self._seq_thread is not None:
            raise MoveError(self, "Can not start device, it is still moving!")
        self._startSequence(self._generateSequence(target))

    def _generateSequence(self, target):
        """returns a device and target specific sequence

        a sequence is a list of steps (dicts of devices to values or callables)
        if a value is a callable, it will be called with the device and the
        target(s) of the device in this order.
        """
        raise NotImplementedError('put a proper _generateSequence '
                                  'implementation here!')


class SequenceMeasurable(SequencerMixin, Measurable):
    """Measurable performing a sequence around measuring.

    classes deriving from this need to implement a
    _generateSequence(self, target) method which returns the required sequence
    and a doRead. doStatus may need to be overriden in special cases.
    """
    def doStart(self, *args, **kwargs):
        if self._seq_thread is not None:
            raise MoveError(self, "Can not start device, it is still moving!")
        self._startSequence(self._generateSequence(*args, **kwargs))

    def _generateSequence(self, *args, **kwargs):
        """returns a device and target specific sequence

        a sequence is a list of steps (dicts of devices to values or callables)
        if a value is a callable, it will be called with the device and the
        target(s) of the device in this order.
        """
        raise NotImplementedError('put a proper _generateSequence '
                                  'implementation here!')


class LockedDevice(BaseSequencer):
    attached_devices = {
        'device' : (Moveable, 'Moveable device which is protected by the lock'),
        'lock'   : (Moveable, 'The lock, protecting the device'),
    }

    parameters = {
        'unlockvalue' : Param('The value for the lock to unlock the moveable',
                              mandatory=True, type=anytype),
        'keepfixed'   : Param('Boolean: Fix devices if not moving?',
                              default=False, type=bool),
        'lockvalue'   : Param('Value for the lock after movement, default None '
                              'goes to previous value',
                              default=None, type=none_or(anytype)),
    }

    def _generateSequence(self, target, *args, **kwargs):
        device = self._adevs['device']
        lock = self._adevs['lock']
        seq = []

        if self.keepfixed:
            # release lock first
            seq.append({lock:lambda dev: dev.release()})

        # now move lock to unlockvalue
        seq.append({lock:self.unlockvalue})

        if self.keepfixed:
            # fix lock again
            seq.append({lock:lambda dev: dev.fix('fixed unless %s moves' % self)})

        seq.append({device:target})

        if self.keepfixed:
            # release lock again
            seq.append({lock:lambda dev: dev.release()})

        # now move lock to lockvalue
        seq.append({lock:self.lockvalue or lock.target or lock.doRead(0)})

        if self.keepfixed:
            # fix lock again
            seq.append({lock:lambda dev: dev.fix('fixed unless %s moves' % self)})

        return seq

    def doRead(self, maxage=0):
        return self._adevs['device'].read(maxage)

    def doStatus(self, maxage=0):
        """returns highest statusvalue"""
        dev_st = self._adevs['device'].status(maxage)
        lock_st = self._adevs['lock'].status(maxage)
        if dev_st[0] > max(lock_st[0], self._seq_status[0]):
            self._seq_status = dev_st
        elif lock_st[0] > max(self._seq_status[0], dev_st[0]):
            self._seq_status = lock_st
        return self._seq_status

    def doIsAllowed(self, target):
        return self._adevs['device'].isAllowed(target)


class LockedSwitcher(LockerMixin, Switcher):
    pass


class LockedMultiSwitcher(LockerMixin, MultiSwitcher):
    pass


class LockedManualMove(LockerMixin, ManualMove):
    """ does not work as expected
    as ManualMove does no correct status/wait
    Kept here as a hint for further bugfixing.
    """
    pass


class LockedVirtualMotor(LockerMixin, VirtualMotor):
    pass

