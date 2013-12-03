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

from nicos.core import Param, Override, none_or, anytype, tupleof, status, \
    NicosError, MoveError, ConfigurationError, ProgrammingError
from nicos.core.device import Moveable, DeviceMixinBase


class SequencerMixin(DeviceMixinBase):
    """Mixin performing a given sequence to reach a certain value.

    Usually, it is fine to derive from `BaseSequencer`.
    """
    parameters = {
        '_seq_status' : Param('status of the currently executed sequence, '
                              'or (100, idle)?', settable=True,
                              mandatory=False, userparam=False,
                              default=(status.OK, 'idle'),
                              type=tupleof(int, str)),
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
            self.log.debug('generated sequence is:')
            for i, step in enumerate(sequence):
                self.log.debug('GenSeq %d of %d:' % (i + 1, len(sequence)))
                for d, v in step.iteritems():
                    if callable(v):
                        self.log.debug(' - call %r (%r)' % (v, d))
                    else:
                        self.log.debug(' - maw(%r, %r)' % (d, v))

        self._asyncSequence(sequence)

    def _asyncSequence(self, sequence):
        """Performs the sequence in a thread."""
        self._seq_stopflag = False
        self._seq_thread = threading.Thread(target=self._sequence,
                                          args=(sequence,))
        self._seq_thread.setDaemon(True)
        self._seq_thread.start()

    def _sequence(self, sequence):
        """Performs the sequence."""
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
                        except NicosError:
                            self.log.exception('error in step %d, call to %r failed'%(i, v))
                            # XXX: just log, or raise as well?
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
    """Moveable performing a sequence to reach a certain value.

    Classes deriving from this need to implement this method:

    .. automethod:: _generateSequence(target)

    Also, a `doRead()` method must be implemented.  `doStatus()` may need to be
    overridden in special cases.
    """

    def doStart(self, target):
        if self._seq_thread is not None:
            raise MoveError(self, 'Cannot start device, it is still moving!')
        self._startSequence(self._generateSequence(target))

    def _generateSequence(self, target):
        """Return the target-specific sequence as a list of steps.

        Each step is a dictionary, with the keys being device objects and the
        value being either a value to move it to, or a callable which is called
        with the device as an argument.

        After each step, each device that has been started is waited for, and the
        next step begins.
        """
        raise NotImplementedError('put a proper _generateSequence '
                                  'implementation here!')


class LockedDevice(BaseSequencer):
    """A "locked" device, where each movement of the underlying device must be
    surrounded by moving another device (the "lock") to some value and back
    after the movement of the main device.

    The "lock" is moved to the `unlockvalue` before moving the main device.
    After the main device has moved successfully, the lock is moved either back to its
    previous value, or if `lockvalue` is not ``None``, to the `lockvalue`.

    If an error occurs while moving the main device, the lock is not moved back
    to "locked" position.  The error must be resolved first to restore integrity
    of the device arrangement.
    """

    attached_devices = {
        'device' : (Moveable, 'Moveable device which is protected by the lock'),
        'lock'   : (Moveable, 'The lock, protecting the device'),
    }

    parameters = {
        'unlockvalue' : Param('The value for the lock to unlock the moveable',
                              mandatory=True, type=anytype),
        'keepfixed'   : Param('Whether to fix lock device if not moving',
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
            seq.append({lock: lambda dev: dev.release()})

        # now move lock to unlockvalue
        seq.append({lock: self.unlockvalue})

        if self.keepfixed:
            # fix lock again
            seq.append({lock: lambda dev: dev.fix('fixed unless %s moves' % self)})

        seq.append({device: target})

        if self.keepfixed:
            # release lock again
            seq.append({lock: lambda dev: dev.release()})

        # now move lock to lockvalue
        seq.append({lock: self.lockvalue or lock.target or lock.doRead(0)})

        if self.keepfixed:
            # fix lock again
            seq.append({lock: lambda dev: dev.fix('fixed unless %s moves' % self)})

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
