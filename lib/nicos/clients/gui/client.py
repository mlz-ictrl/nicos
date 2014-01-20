#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""NICOS daemon client object for the GUI."""

from PyQt4.QtCore import QObject, SIGNAL

from nicos.clients.base import NicosClient
from nicos.protocols.daemon import DAEMON_EVENTS


class NicosGuiClient(NicosClient, QObject):
    siglist = ['connected', 'disconnected', 'broken', 'failed', 'error'] + \
              DAEMON_EVENTS.keys()

    def __init__(self, parent):
        QObject.__init__(self, parent)
        NicosClient.__init__(self)

    def signal(self, name, *args):
        self.emit(SIGNAL(name), *args)

    # high-level functionality

    def getDeviceList(self, needs_class='nicos.core.device.Device',
                      only_explicit=True):
        """Return list of devices."""
        query = 'list(dn for (dn, d) in session.devices.iteritems() ' \
                'if %r in d.classes' % needs_class
        if only_explicit:
            query += ' and dn in session.explicit_devices'
        query += ')'
        return sorted(self.eval(query, []))

    def getDeviceParamInfo(self, devname):
        """Return info about all parameters of the device."""
        query = 'dict((pn, pi.serialize()) for (pn, pi) in ' \
                'session.getDevice(%r).parameters.iteritems())' % devname
        return self.eval(query, {})

    def getDeviceParams(self, devname):
        """Return values of all device parameters from cache."""
        params = {}
        devkeys = self.ask('getcachekeys', devname.lower() + '/') or []
        for key, value in devkeys:
            param = key.split('/')[1]
            params[param] = value
        return params

    def getDeviceParam(self, devname, param):
        """Return value of a specific device parameter from cache."""
        key = self.ask('getcachekeys', devname.lower() + '/' + param)
        if key:
            return key[0][1]
        return None
