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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Matthias Pomm <matthias.pomm@hzg.de>
#
# *****************************************************************************
"""REFSANS SDS (safe detector system) devices."""

import requests

from nicos.core import Override, Param, Readable, oneof, status
from nicos.core.errors import CommunicationError, ConfigurationError, \
    NicosError


class SdsBase(Readable):
    """Base class to read information from the SDS.

    The SDS is an intelligent detector safety system, which protects the
    detector against to high data rates in the area as well as for local
    spots.
    """

    parameters = {
        'url': Param('URL reading the values',
                     type=str,
                     default='http://savedetector.refsans.frm2/json?1'),
        'timeout': Param('timeout to get an answers from URL',
                         default=0.1),
    }

    def _read_controller(self, key):
        try:
            data = requests.get(self.url, self.timeout).json()
        except requests.Timeout as e:
            raise CommunicationError(self, 'HTTP request failed: %s' % e)
        except Exception as e:
            raise ConfigurationError(self, 'HTTP request failed: %s' % e)
        return data[key]

    def doStatus(self, maxage=0):
        # TODO select the right entry to find out the state of the SDS
        try:
            self._read_controller('time')
            return status.OK, ''
        except NicosError:
            return status.ERROR, 'Could not talk to hardware.'


class SdsRatemeter(SdsBase):
    """Read the count rates for the different input channels of the SDS."""

    parameters = {
        'channel': Param('Channel to be rated',
                         type=oneof('a', 'x', 'y'), default='a',
                         settable=False)
    }

    parameter_overrides = {
        'fmtstr': Override(default='%d'),
        'unit': Override(default='cps'),
    }

    def doRead(self, maxage=0):
        res = self._read_controller('mon_counts_cps_%s' % self.channel)
        return int(res)
