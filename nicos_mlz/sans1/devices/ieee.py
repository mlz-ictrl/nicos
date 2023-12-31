# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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

from nicos import session
from nicos.core import Override, Param, Readable, status
from nicos.core.errors import ConfigurationError


class IEEEDevice(Readable):
    """Special device to put arbitrary device values/parameters into the
    BerSANS "IEEE" header fields (to be able to use them during analysis).
    """

    parameters = {
        'valuename': Param('Device ("dev") or parameter ("dev.param") '
                           'to return on read', type=str, settable=True,
                           unit='', category='general'),
    }
    parameter_overrides = {
        'unit': Override(mandatory=False, default='', settable=False,
                         category='general'),
    }

    hardware_access = False

    def doWriteValuename(self, valuename):
        if valuename and '.' not in valuename:
            if self._cache:
                unit = self._cache.get(valuename, 'unit', '')
            else:
                unit = getattr(session.getDevice(valuename), 'unit', '')
        else:
            try:
                devname, parname = valuename.rsplit('.', 1)
                dev = session.getDevice(devname)
                devunit = getattr(dev, 'unit', '')
                unit = dev._getParamConfig(parname).unit or ''
                if devunit:
                    unit = unit.replace('main', devunit)
            except ConfigurationError:
                unit = ''
        self._setROParam('unit', unit)

    def doStatus(self, maxage=0):
        if not self.valuename:
            return status.OK, ''

        devname = self.valuename.rsplit('.', 1)[0]
        if self._cache:
            return self._cache.get(devname, 'status')
        return session.getDevice(devname).status(maxage)

    def doRead(self, maxage=0):
        if not self.valuename:
            return ''

        if '.' in self.valuename:
            devname, parname = self.valuename.rsplit('.', 1)
            if self._cache:
                return self._cache.get(devname, parname)
            return getattr(session.getDevice(devname), parname)
        if self._cache:
            return self._cache.get(self.valuename, 'value')
        return session.getDevice(self.valuename).read(maxage)
