#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

"""Sets values with a w&t web UI.

w&t box creates trigger signal for tisane fg1 burst mode.
"""

from nicos.core import Param, Moveable, Override, CommunicationError, \
     ConfigurationError, NicosError, status

try:
    from urllib2 import urlopen
except ImportError:
    urlopen = None


class WutValue(Moveable):

    parameters = {
        'hostname':     Param('Host name of the wut site',
                              type=str, mandatory=True),
        'port':         Param('Port of the sensor',
                              type=str, mandatory=True),
    }

    parameter_overrides = {
        'unit':         Override(mandatory=False),
        'pollinterval': Override(default=5),
        'maxage':       Override(default=17),
    }

    def _getRaw(self):
        if urlopen is None:
            raise NicosError(self, 'cannot parse web page, urllib2 is not '
                             'installed on this system')
        url = 'http://%s/Single%s' % (self.hostname, self.port)
        try:
            response = urlopen(url)
            html = response.read()
            return html
        except ConfigurationError:  # pass through error raised above
            raise
        except Exception as err:
            raise CommunicationError(self, 'wut-box not responding or '
                                     'changed format: %s' % err)

    def doReadUnit(self):
        return self._getRaw().split(';')[-1].split(' ')[-1]

    def doRead(self, maxage=0):
        return float(self._getRaw().split(';')[-1].split(' ')[0].replace(',', '.'))

    def doStatus(self, maxage=0):
        return status.OK, ''

    def doStart(self, value):
        if urlopen is None:
            raise NicosError(self, 'cannot parse web page, urllib2 is not '
                             'installed on this system')
        url = 'http://%s/outputaccess%s?PW=sans1&State=%s&' % (self.hostname, self.port, value)
        try:
            response = urlopen(url, timeout=1)
            html = response.read()
            self.log.debug(html)

        except ConfigurationError:  # pass through error raised above
            raise
        except Exception as err:
            raise CommunicationError(self, 'wut-box not responding or '
                                     'changed format: %s' % err)
