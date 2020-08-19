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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""REFSANS SDS (safe detector system) devices."""

import requests

from nicos.core import Override, Param, Readable, intrange, oneof, status, \
    usermethod
from nicos.core.errors import CommunicationError, ConfigurationError, \
    NicosError
from nicos.core.mixins import HasOffset


class JsonBase(Readable):
    """Base class for webinterface

    """

    parameters = {
        'url': Param('URL reading the values',
                     type=str),
        'timeout': Param('timeout to get an answers from URL',
                         default=0.1),
        'valuekey': Param('Key inside the json dict, only to proof comm',
                          type=str,),
    }

    def _read_controller(self, keys):
        line = '_read_controller %s' % keys
        self.log.debug(line)
        try:
            data = requests.get(self.url, timeout=self.timeout).json()
            self.log.debug(data)
        except requests.Timeout as e:
            self.log.info(line)
            self.log.info('url %s' % self.url)
            self.log.info('err %s' % e)
            raise CommunicationError(self, 'HTTP Timeout failed')
        except Exception as e:
            self.log.info(line)
            self.log.info('url %s' % self.url)
            self.log.info('err %s' % e)
            raise ConfigurationError(self, 'HTTP request failed')
        res = {}
        for key in keys:
            res[key] = data[key]
        return res

    def doStatus(self, maxage=0):
        try:
            self._read_controller([self.valuekey])
            return status.OK, ''
        except CommunicationError:
            return status.WARN, 'Timeout during talk to hardware.'
        except NicosError:
            return status.ERROR, 'Could not talk to hardware.'


class CPTReadout(HasOffset, JsonBase):

    parameters = {
        'phasesign': Param('Phase sign',
                           type=oneof('unsigned', 'signed'),
                           settable=False,
                           default='unsigned'),
        'channel': Param('Index of value',
                         type=intrange(-1, 99),),
    }

    def _read_ctrl(self, channel):
        data = self._read_controller([self.valuekey, 'start_act'])
        self.log.debug('res: %r', data)
        self.log.debug('channel %d', channel)
        if channel == -1:
            self.log.debug('calc speed')
            res = 3e9 / data['start_act']  # speed
            res -= self.offset  # should be Zero
        elif channel == 90:
            self.log.debug('calc phase in respect to Disk 1 of Disc 1')
            self.log.debug('offset %.2f', self.offset)
            res = -360.0 * data[self.valuekey][6] / data['start_act']
            res = self._kreis(res)
        else:
            self.log.debug('calc phase in respect to Disk 1')
            self.log.debug('offset %.2f', self.offset)
            res = -360.0 * data[self.valuekey][channel] / data['start_act']
            res -= self.offset
            res = self._kreis(res)
        return res

    def _kreis(self, phase, kreis=360.0):
        line = 'kreis phase %.2f' % phase
        if self.phasesign == 'signed':
            while phase > kreis / 2:
                phase -= kreis
            while phase < -kreis / 2:
                phase += kreis
        else:
            phase = -phase
            while phase > kreis:
                phase -= kreis
            while phase < 0:
                phase += kreis
        self.log.debug('%s %.2f', line, phase)
        return phase

    def doRead(self, maxage=0):
        return self._read_ctrl(self.channel)


class SdsRatemeter(JsonBase):
    """Read count rates for the different input channels of the SDS."""

    parameters = {
        'channel': Param('Channel to be rated',
                         type=oneof('a', 'x', 'y'), default='a',
                         settable=False),
        'mode': Param('mode of the beam',
                      type=oneof('reflectivity', 'gisans'),
                      settable=True, userparam=True, default='gisans'),
        'masks': Param('Maps mask to attached devices positions',
                       type=dict, mandatory=True),
        'controlurl': Param('URL to the control side',
                            type=str, userparam=False),
    }

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
        'unit': Override(default='cps'),
    }

    def doWriteMode(self, target):
        self.log.debug('WriteMode to: %s', target)
        val = int(self.masks[target])
        try:
            res = requests.post(self.controlurl, timeout=self.timeout,
                                data={'mon_limit_start': '%d' % val})
            if res.status_code != 200:
                self.log.error('write mode: res %d %s', res.status_code,
                               res.reason)
            res.close()
        except ConnectionError as e:
            self.log.error('write mode: %s', e)

    @usermethod
    def clear(self):
        try:
            res = requests.post(self.controlurl, timeout=self.timeout,
                                data={'mon_button': '1'})
            if res.status_code != 200:
                self.log.error('clear res: %d %s', res.status_code, res.reason)
            res.close()
        except ConnectionError as e:
            self.log.error('clear: %s', e)

    def doStatus(self, maxage=0):
        try:
            res = self._read_controller([self.valuekey])
            if int(res[self.valuekey]) == 0:
                return status.OK, ''
            return status.ERROR, 'System tripped! Please, clear.'
        except CommunicationError:
            return status.WARN, 'Timeout during talk to the hardware.'
        except NicosError:
            return status.ERROR, 'Could not talk to hardware.'

    def doRead(self, maxage=0):
        res = self._read_controller(['mon_counts_cps_%s' % self.channel])
        res = int(list(res.values())[0])  # Pyth3 res.popitem()[1]
        ret = int(res / 2.46)
        self.log.info('system %dfoo countrate %dcps', res, ret)
        return ret
