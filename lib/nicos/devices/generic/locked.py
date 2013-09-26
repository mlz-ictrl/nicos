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

from nicos.core import Param, none_or, anytype, status, \
     NicosError, MoveError, ConfigurationError
from nicos.core.device import Readable, Moveable, DeviceMixinBase
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
            self.wait()

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
        self._mythread.run()

    move = start

    def doWait(self):
        if self._mythread:
            self._mythread.join()

    def status(self, maxage=0):
        if self._mythread is None:
            return Readable.status(self, maxage)
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

    def doReset(self):
        self._set_mystatus(status.OK, 'idle')


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

class LockedDevice(LockerMixin, Moveable):
    attached_devices = {
        'moveable' : (Moveable, 'The device without the locking feature.'),
    }

    def doStart(self, target):
        return self._adevs['moveable'].start(target)

    def doIsAllowed(self, target):
        return self._adevs['moveable'].isAllowed(target)

    def doRead(self, maxage=0):
        return self._adevs['moveable'].read(maxage)

    def doStop(self):
        return self._adevs['moveable'].stop()

    def doStatus(self, maxage=0):
        return self._adevs['moveable'].status(maxage)
