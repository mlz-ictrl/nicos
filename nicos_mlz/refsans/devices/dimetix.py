#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""Device for the Dimetix distance laser sensor."""

from __future__ import absolute_import, division, print_function

from nicos.core import Param, Readable, status
from nicos.core.errors import CommunicationError, HardwareError
from nicos.core.mixins import CanDisable, HasOffset
from nicos.core.params import string
from nicos.devices.tango import StringIO

errors = {
    203: 'Wrong syntax in command, prohibited parameter in command entry or '
         'non-valid result',
    210: 'Not in tracking mode, start tracking mode first',
    211: 'Sampling too fast, set the sampling time to a larger value',
    212: 'Command cannot be executed, because tracking mode is active, first '
         'use the "sNc" command to stop tracking mode',
    220: 'Communication error',
    230: 'Distance value overflow caused by wrong user configuration. Change '
         'user offset (and/or user gain)',
    231: 'Wrong mode for digital input status read',
    232: 'Digital output 1 cannot be set if configured as digital input',
    233: 'Number cannot be displayed (Check output format)',
    234: 'Distance out of range',
    236: 'Digital output manual mode (DOM) cannot be activated when configured'
         ' as digital input',
    252: 'Temperature too high (contact Dimetix if error occurs at room '
         'temperature)',
    253: 'Temperature too low (contact Dimetix if error occurs at room '
         'temperature)',
    254: 'Bad signal from target. It takes too long to measure according '
         'distance',
    255: 'Received signal too weak (Use different target and distances, if '
         'problem persists, please contact Dimetix)',
    256: 'Received signal too strong (Use different target and distances, if '
         'problem persists, please contact Dimetix)',
    257: 'Too much background light (Use different target and distances, if '
         'problem persists, please contact Dimetix)',
    258: 'Power supply voltage is too high',
    260: 'Distance cannot be calculated because of ambiguous targets. Use '
         'clear defined targets to measure the distance',
    360: 'Measuring time is too short',
    361: 'Measuring time is too long',
}


class DimetixLaser(CanDisable, HasOffset, Readable, StringIO):

    parameters = {
        'signalstrength': Param('signal strength',
                                type=int, settable=False, volatile=True,
                                userparam=True, fmtstr='%.0f', unit=''),
        'temperature': Param('Device temperature',
                             type=float, settable=False, volatile=True,
                             userparam=True, fmtstr='%.2f', unit='C'),
        'id': Param('Device ID',
                    type=int, settable=False, userparam=False, default=0),
        'serialnumber': Param('Hardware serial number',
                              type=int, settable=False, volatile=True),
        'version': Param('Software version',
                         type=string, settable=False, volatile=True),
    }

    def _floatN1(self, val):
        return float(val) / 10.

    def _integer(self, val):
        return int(val)

    def _communicate(self, cmd):
        mnem = '%d%s' % (self.id, cmd)
        ret = self.communicate('s%s' % mnem)
        if ret and ret.startswith == ('g%s' % mnem):
            return ret[len(mnem):]
        if ret[2:4] == '@E':
            err = self._integer(ret[4:])
            if err in errors:
                raise HardwareError(errors[err])
            raise HardwareError('Hardware failure (Contact Dimetix)')
        raise CommunicationError("Did not get a valid answer from hardware "
                                 "for command '%s': '%s'" % (cmd, ret))

    def doReadSerialnumber(self):
        return self._integer(self._communicate('sn'))

    def doReadVersion(self):
        ret = self._communicate('sv')
        return '%d-%d' % (self._integer(ret[4:9]), self._integer(ret[9:]))

    def doReadSignalstrength(self):
        return self._integer(self._communicate('m+0'))

    def doReadTemperature(self):
        return self._floatN1(self._communicate('t'))

    def _get_value(self):
        # read Value
        return self._floatN1(self._communicate('g'))

    def doEnable(self, onoff):
        self._communicate('o' if onoff else 'p')

    def doRead(self, maxage=0):
        return self._get_value() - self.offset

    def doStatus(self, maxage=0):
        try:
            self._get_value()
            return status.OK, ''
        except (CommunicationError, HardwareError):
            return status.ERROR, 'timeout'

    def doPoll(self, n, maxage):
        self._pollParam('signalstrength')
