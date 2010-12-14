#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Iseg high voltage power supply device classes
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Iseg high voltage power supply device classes."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import serial
import threading
from time import sleep, time

from IO import StringIO

from nicm import status
from nicm.utils import intrange, listof
from nicm.device import Device, Readable, Moveable, Switchable, Param
from nicm.errors import NicmError, CommunicationError
from nicm.taco.base import TacoDevice


class IsegConnector(object):
    """Abstract base class for devices that contain an iseg HVPS."""

    def lockChannel(self, channel):
        pass

    def unlockChannel(self):
        pass

    def communicate(self, msg, rlen):
        raise NotImplementedError


class StandaloneIseg(TacoDevice, Device, IsegConnector):
    taco_class = StringIO

    # no locking/unlocking needed

    def doReadUnit(self):
        return ''   # XXX

    def communicate(self, msg, rlen):
        # must send and read back each character individually
        # rlen is ignored since we really wait until everything is transmitted
        for c in msg:
            self._taco_guard(self._dev.write, c)
            while 1:
                sleep(0.003)
                cr = self._taco_guard(self._dev.read)
                if cr:
                    if cr != c:
                        raise NicmError('communication problem in echo')
                    break
        self._taco_guard(self._dev.write, '\r\n')
        sleep(0.01)
        s = ''
        while s.count('\n') != 2:
            s += self._taco_guard(self._dev.read)
            time.sleep(0.003)
        return s.strip('\r\n') # discard newlines


class IsegHV(Moveable):
    """
    iseg HVPS (standalone or inside a Toni crate).
    The cratechannel parameter is irrelevant for a standalone HVS.
    The isegchannel parameter must be 1 for a HVS with only one output.
    """
    attached_devices = {
        'crate': IsegConnector,
    }

    parameters = {
        'cratechannel': Param('Channel of the HV if in Toni crate',
                              type=intrange(0, 2), mandatory=True),
        'isegchannel':  Param('Channel of the Iseg HV (1 = A, 2 = B)',
                              type=intrange(1, 3), mandatory=True),
        # XXX ramp as a parameter
    }

    states = {'ON ': status.OK,
              'OFF': status.ERROR,
              'MAN': status.ERROR,
              'ERR': status.ERROR,
              'INH': status.ERROR,
              'QUA': status.ERROR,
              'L2H': status.BUSY,
              'H2L': status.BUSY,
              'LAS': status.BUSY,
              'TRP': status.ERROR,}

    def doInit(self):
        crate = self._adevs['crate']
        crate.lockChannel(self.cratechannel)
        try:
            resp = crate.communicate('#', 15)
            if resp.count(';') not in (2, 3):
                # hash is "info" command; it returns a string in the form
                # "deviceid;version;Umax;Imax" -- however, the Toni crate
                # truncates the response so that there are only two ';' left
                raise CommunicationError('communication problem with HV supply')
            crate.communicate('W=001', 0)  # set write delay to minimum
        finally:
            crate.unlockChannel()

    def doStart(self, value):
        crate = self._adevs['crate']
        crate.lockChannel(self.cratechannel)
        try:
            crate.communicate('D%d=%04d' % (self.isegchannel, value), 0)
            resp = crate.communicate('G%d' % self.isegchannel, 6)
            # return message is the status
            if resp[:3] != ('S%d=' % self.isegchannel):
                raise NicmError('could not set voltage: %r' % resp)
            if resp[3:] not in self.states or \
                   self.states[resp[3:]] not in (status.OK, status.BUSY):
                if resp[3:] == 'MAN':
                    raise NicmError('could not set voltage, voltage control '
                                    'switched to manual')
                elif resp[3:] == 'OFF':
                    raise NicmError('could not set voltage, device off')
                raise NicmError('could not set voltage: error %r' % resp[3:])
        finally:
            crate.unlockChannel()

    def doRead(self):
        crate = self._adevs['crate']
        crate.lockChannel(self.cratechannel)
        try:
            resp = crate.communicate('U%d' % self.isegchannel, 5)
            if not resp or resp[0] not in '+-':
                raise NicmError('invalid voltage readout %r' % resp)
            return int(resp)
        finally:
            crate.unlockChannel()

    def doStatus(self):
        crate = self._adevs['crate']
        crate.lockChannel(self.cratechannel)
        try:
            resp = crate.communicate('S%d' % self.isegchannel, 6)
            if resp[:3] != ('S%d=' % self.isegchannel):
                raise NicmError('invalid status readout %r' % resp)
            return self.states[resp[3:]]
        finally:
            crate.unlockChannel()

    def doWait(self):
        crate = self._adevs['crate']
        while 1:
            crate.lockChannel(self.cratechannel)
            try:
                resp = crate.communicate('S%d' % self.isegchannel, 6)
                if resp[3:] == 'ON ':
                    return
                elif resp[3:] not in ('L2H', 'H2L'):
                    raise NicmError('device in error status: %s' % resp[3:])
            finally:
                crate.unlockChannel()

    def _ramp(self):
        crate = self._adevs['crate']
        crate.lockChannel(self.cratechannel)
        try:
            resp = crate.communicate('V%d' % self.isegchannel, 3)
            return int(resp)
        finally:
            crate.unlockChannel()

    def _setramp(self, ramp):
        assert 1 <= ramp <= 255
        crate = self._adevs['crate']
        crate.lockChannel(self.cratechannel)
        try:
            resp = crate.communicate('V%d=%03d' % (self.isegchannel, ramp), 0)
            self.printinfo('set ramp to %d V/s' % ramp)
        finally:
            crate.unlockChannel()

    def _storeramp(self):
        crate = self._adevs['crate']
        crate.lockChannel(self.cratechannel)
        try:
            crate.communicate('A%d=01' % self.isegchannel, 0)
            self.printinfo('ramp stored to EEPROM')
        finally:
            crate.unlockChannel()
