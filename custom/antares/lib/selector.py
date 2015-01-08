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

"""Astrium selector device."""

from math import pi, tan, radians
from time import time as currenttime, sleep

from IO import StringIO

from nicos.core import status, Moveable, Readable, HasLimits, Override, Param, \
    CommunicationError, HasPrecision, InvalidValueError, MoveError
from nicos.devices.taco.core import TacoDevice

FSEP = '#'   # separator for fields in reply
VSEP = '='   # separator for name and value in field


class SelectorState(TacoDevice, Readable):
    """
    Read status from selector
    """

    taco_class = StringIO

    def doRead(self, maxage=0):
        st = self._taco_guard(self._dev.communicate, 'N#SOS#STATE ')
        vals = st.split(FSEP)
        ret = {}
        for val in vals:
            if VSEP in val:
                vv = val.split(VSEP)
                ret[vv[0].strip()] = vv[1].strip()
        return ret


class AstriumSelector(TacoDevice, HasLimits, HasPrecision, Moveable):
    """
    Device object for an Astrium NVS via TCP.
    """
    taco_class = StringIO

    parameters = {
        'timeout': Param('Timeout for reaching desired speed', type=float, unit='s',
                         settable=True),
        'commdelay': Param('Time between host communication tries', type=float,
                         unit='s', settable=True, default=5),
        'maxtries': Param('Maximum tries for setting a new speed', type=int,
                         settable=True, default=20),
    }

    parameter_overrides = {
        'unit':  Override(mandatory=False, default='rpm'),
    }

    attached_devices = {
        'statedev': (SelectorState, 'the device to get all values from'),
    }

    valuetype = int

    def doInit(self, mode):
        pass

    def doReset(self):
        pass

    def doRead(self, maxage=0):
        st = self._adevs['statedev'].read(10)
        return int(st['ASPEED'])

    def doStatus(self, maxage=0):
        st = self._adevs['statedev'].read(10)['STATE']
        # manual specifies 'IDL', actual reply is 'IDLING'
        if st.startswith('IDL'):
            return status.BUSY, 'idle'
        elif st.startswith('BRA'):
            return status.ERROR, 'braking'
        elif st.startswith('INA'):
            return status.ERROR, 'inactive'
        elif st.startswith('CONT'):
            return status.OK, 'speed controlled'
        raise CommunicationError(self, 'state not in reply from selector or invalid')

    def doStart(self, value):
        for _i in range(self.maxtries):
            try:
                ret = self._taco_guard(self._dev.communicate, 'N#SOS#SPEED %05d' % value)
            except CommunicationError:
                sleep(self.commdelay)
            else:
                vals = [v.split(VSEP) for v in ret.split(FSEP)]
                for vv in vals:
                    if vv[0] == 'NCCEPT':
                        raise InvalidValueError(self, 'speed %d not accepted by selector' % value)
                    if vv[0].strip() == 'RSPEED':
                        if len(vv) > 1 and int(vv[1]) == value:
                            return
                        self.log.debug('requested speed not correct: %r' % vv)
                        break
                sleep(self.commdelay)
        raise CommunicationError(self, 'selector did not execute speed request')

    def doWait(self):
        inittime = currenttime()
        while currenttime() < inittime + self.timeout:
            if abs(self.read() - self.target) < self.precision:
                return
        raise MoveError(self, 'selector did not reach %d rpm in %s seconds' %
                        (self.target, self.timeout))


class SelectorValue(Readable):
    """
    Read a value from the selector

    this class uses cached values from the state device
    """

    parameters = {
        'valuename': Param('Name of the value to read', mandatory=True, type=str),
    }

    attached_devices = {
        'statedev': (SelectorState, 'the device to get all values from'),
    }

    def doRead(self, maxage=0):
        st = self._adevs['statedev'].read(10)  # <-- this is intended
        try:
            return float(st[self.valuename])
        except ValueError:
            return st[self.valuename]

    def doStatus(self, maxage=0):
        return status.OK, ''


class SelectorLambda(Moveable):

    parameters = {
        'twistangle': Param('Twist angle', default=23.5, unit='deg'),
        'length':     Param('Length', default=0.25, unit='m'),
        'beamcenter': Param('Beam center', default=0.115, unit='m'),
        'maxspeed':   Param('Max speed', default=21000, unit='rpm'),
    }

    attached_devices = {
        'seldev' : (AstriumSelector, 'the selector device'),
    }

    hardware_access = False

    def doRead(self, maxage=0):
        spd = self._adevs['seldev'].read(maxage)
        ang = 0
        v0 = 3955.98
        lambda0 = self.twistangle * 60 * v0 / (360 * self.length * self.maxspeed)
        A = 2 * self.beamcenter * pi / (60 * v0)
        ret = (tan(radians(ang)) + (A * self.maxspeed * lambda0)) / \
            (-A**2 * self.maxspeed * lambda0 * tan(radians(ang)) + A)
        return ret / spd

    def doStart(self, value):
        ang = 0
        v0 = 3955.98
        lambda0 = self.twistangle * 60 * v0 / (360 * self.length * self.maxspeed)
        A = 2 * self.beamcenter * pi / (60 * v0)
        ret = (tan(radians(ang)) + (A * self.maxspeed * lambda0)) / \
            (-A**2 * self.maxspeed * lambda0 * tan(radians(ang)) + A)
        self.log.debug('moving selector to %f' % (ret / value))
        self._adevs['seldev'].start(ret / value)

    def doStatus(self, maxage=0):
        return self._adevs['seldev'].status(maxage)

    def doWait(self):
        self._adevs['seldev'].wait()
