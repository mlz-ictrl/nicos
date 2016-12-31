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
#   Andreas Wilhelm <andreas.wilhelm@frm2.tum.de>
#
# *****************************************************************************

"""Show values read out from a Memograph web UI.

Memographs are the logging system for 'cooling water' related data in the
neutron guide hall of the FRM II.
"""

from nicos.core import Param, Readable, Override, CommunicationError, \
    ConfigurationError, NicosError, status

try:
    from lxml.html import parse
except ImportError:
    parse = None


class MemographValue(Readable):

    parameters = {
        'hostname':  Param('Host name of the memograph webserver',
                           type=str, mandatory=True),
        'group':     Param('Group in the memograph web UI',
                           type=int, mandatory=True),
        'valuename': Param('Name of the value to read (as displayed in first'
                           ' column of web UI)', type=str, mandatory=True),
    }

    parameter_overrides = {
        'unit':         Override(mandatory=False),
        'pollinterval': Override(default=60),
        'maxage':       Override(default=125),
    }

    def _getRaw(self):
        if parse is None:
            raise NicosError(self, 'cannot parse web page, lxml is not '
                             'installed on this system')
        url = 'http://%s/web?group=%d' % (self.hostname, self.group)
        try:
            tree = parse(url)
            names = [name.text.strip()
                     for name in tree.findall('//font[@class="tagname"]')]
            values = [value.text.strip()
                      for value in tree.findall('//font[@class="pv"]')]
            info = dict(zip(names, values))
            if self.valuename not in info:
                raise ConfigurationError(self, 'value %r not found on '
                                         'Memograph page (valid values are %s)'
                                         % (self.valuename,
                                            ', '.join(map(repr, names))))
            return info[self.valuename]
        except ConfigurationError:  # pass through error raised above
            raise
        except Exception as err:
            raise CommunicationError(self, 'Memograph not responding or '
                                     'changed format: %s' % err)

    def doReadUnit(self):
        return self._getRaw().split()[1].encode('utf-8').decode('utf-8').\
            replace(u'°', 'deg')

    def doRead(self, maxage=0):
        return float(self._getRaw().split()[0].replace(',', '.'))

    def doStatus(self, maxage=0):
        return status.OK, ''
