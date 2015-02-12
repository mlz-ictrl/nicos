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
from time import time as currenttime

from IO import StringIO

from nicos.core import status, Moveable, Readable, HasLimits, Override, Param, \
    CommunicationError, HasPrecision, HasTimeout, InvalidValueError, \
    MoveError, listof, limits, HasCommunication
from nicos.devices.taco.core import TacoDevice

FSEP = '#'  # separator for fields in reply ("/" in manual, "#" in reality)
VSEP = '='  # separator for field name and value (":" in manual, "=" in reality)


class SelectorState(TacoDevice, Readable):
    """
    Class for reading out all of the selector state in one go.

    The Astrium selector's network interface is VERY slow.  Requests can take up
    to 2 seconds to complete.  Also, too many requests will cause the LabView
    software to "half-crash" (it still responds to some queries but not all).

    Also, the STATE command delivers all of the state data in the same answer,
    so it would be unnecessary for polling to do that query over and over again.

    Therefore this class does the actual hardware communication and polling,
    while individual values can be configured as SelectorValue devices only
    query the values retrieved by this class.

    Typically you will have one instance of this device in your setup,
    configured as `lowlevel` and with a fairly high `pollinterval` (10 seconds
    appears to be okay.)  Apart from this you can have multiple `SelectorValue`
    devices, each reading out one of the state variables, and one
    `SelectorSpeed` device for reading and controlling the speed.

    Optionally, you can add a `SelectorLambda` device for controlling speed in
    terms of wavelength.
    """

    taco_class = StringIO

    def _parseNVSReply(self, reply):
        """Parse a reply from the NVS LabView software.

        The reply is a header and then list of key-value pairs like
        "N#SOS#ACCEPT#KEY1 = VALUE1#KEY2 = VALUE2#".

        Returns a bool ("accepted" by NVS or not?) and a dict with the
        key-value pairs.
        """
        vals = reply.split(FSEP)
        # we need a header consisting of N#SOS#[AN]CCEPT
        if len(vals) < 3 or vals[0:2] != ['N', 'SOS']:
            raise CommunicationError(self, 'NVS reply did not contain '
                                     'proper header: %r' % reply)
        accepted = vals[2] == 'ACCEPT'  # else 'NCCEPT'
        values = {}
        for keyval in vals[3:]:
            if VSEP in keyval:
                key, val = keyval.split(VSEP, 1)
                values[key.strip()] = val.strip()
        return accepted, values

    def communicate(self, query):
        reply = self._taco_guard(self._dev.communicate, 'N#SOS#' + query)
        return self._parseNVSReply(reply)

    def doRead(self, maxage=0):
        return self.communicate('STATE ')[1]


class SelectorSpeed(HasCommunication, HasLimits, HasPrecision, HasTimeout, Moveable):
    """
    Device object for controlling the speed of an Astrium NVS.

    Uses SelectorState for readout.
    """

    parameters = {
        'blockedspeeds': Param('List of tuples of forbidden speed values',
                               unit='rpm', type=listof(limits)),
    }

    parameter_overrides = {
        'unit':      Override(mandatory=False, default='rpm'),
        'precision': Override(mandatory=False, type=float, default=0),
        'comtries':  Override(default=20),
        'comdelay':  Override(default=5),
    }

    attached_devices = {
        'statedev': (SelectorState, 'The device to get all values from'),
    }

    valuetype = int

    def doInit(self, mode):
        pass

    def doReset(self):
        pass

    def doRead(self, maxage=0):
        st = self._adevs['statedev'].read(10)
        try:
            return int(st['ASPEED'])
        except (KeyError, ValueError):
            raise CommunicationError(self, 'speed not returned by selector or '
                                     'invalid: %r' % st.get('ASPEED'))

    def doStatus(self, maxage=0):
        try:
            st = self._adevs['statedev'].read(10)['STATE']
        except KeyError:
            raise CommunicationError(self, 'state not returned by selector')
        # manual specifies 'IDL', actual reply is 'IDLING'
        if st.startswith('IDL'):
            return status.OK, 'idling'
        elif st.startswith('BRA'):
            return status.ERROR, 'braking'
        elif st.startswith('INA'):
            return status.ERROR, 'inactive'
        elif st.startswith('CONT'):
            return status.OK, 'speed controlled'
        raise CommunicationError(self, 'state returned from selector is '
                                 'unknown: %r' % st)

    def doIsAllowed(self, value):
        for _min, _max in self.blockedspeeds:
            if _min <= value <= _max:
                return False, 'Speed lies in the forbidden range (%d, %d)' \
                               % (_min, _max)
        return True, ''

    def _com_return(self, result, target):
        accepted, state = result
        if accepted:
            rspeed = SelectorSpeed.valuetype(state.get('RSPEED'))
            if abs(rspeed - target) > self.precision:
                # we got a "requested speed" target back and it does not match
                # the one we tried to set
                raise CommunicationError(self, 'selector did not execute '
                                         'speed request')
        return accepted

    def doStart(self, target):
        if abs(self.doRead() - target) <= self.precision:
            return
        # the SPEED command is sometimes not accepted immediately; we try a few
        # times with lots of time in between
        accepted = self._com_retry(target, self._adevs['statedev'].communicate,
                                   'SPEED %05d' % target)
        if not accepted:
            raise InvalidValueError(self, 'speed of %d RPM not accepted'
                                    ' by selector (is it in a forbidden'
                                    ' range?)' % target)

    def doIsCompleted(self):
        # the selector does not return a "busy" state while speeding up/down, so
        # we have to check for the speed reaching the target speed.
        if abs(self.read() - self.target) < self.precision: # XXX: inconsistent with doStatus!
            return True
        if currenttime() < self.started + self.timeout:
            return False
        raise MoveError(self, 'selector did not reach %d rpm in %s seconds' %
                        (self.target, self.timeout))


class SelectorValue(Readable):
    """
    Readout of a single value of the selector state.
    """

    parameters = {
        'valuename': Param('Name of the value to read', mandatory=True, type=str),
    }

    attached_devices = {
        'statedev': (SelectorState, 'The device to get all values from'),
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
    """
    Control selector wavelength directly, converting between speed and
    wavelength.
    """

    parameters = {
        'twistangle': Param('Blade twist angle', mandatory=True, unit='deg'),
        'length':     Param('Selector length', mandatory=True, unit='m'),
        'beamcenter': Param('Beam center position', mandatory=True, unit='m'),
        'maxspeed':   Param('Max selector speed', mandatory=True, unit='rpm'),
    }

    attached_devices = {
        'seldev' : (SelectorSpeed, 'The selector speed device'),
    }

    hardware_access = False

    def _constant(self):
        """With constant tilt angle (not used yet) the relation between speed
        and wavelength is just "speed = C/lambda", this function calculates C.

        Formula adapted from NVS C++ source code.
        """
        ang = 0
        v0 = 3955.98
        lambda0 = self.twistangle * 60 * v0 / (360 * self.length * self.maxspeed)
        A = 2 * self.beamcenter * pi / (60 * v0)
        return (tan(radians(ang)) + (A * self.maxspeed * lambda0)) / \
            (-A**2 * self.maxspeed * lambda0 * tan(radians(ang)) + A)

    def doRead(self, maxage=0):
        spd = self._adevs['seldev'].read(maxage)
        return self._constant() / spd if spd else -1

    def doIsAllowed(self, value):
        if value == 0:
            return False, 'zero wavelength not allowed'
        speed = int(self._constant() / value)
        return self._adevs['seldev'].isAllowed(speed)

    def doStart(self, value):
        speed = int(self._constant() / value)
        self.log.debug('moving selector to %f rpm' % speed)
        self._adevs['seldev'].start(speed)

