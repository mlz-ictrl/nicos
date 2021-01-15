#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Michael Hart <michael.hart@stfc.ac.uk>
#
# *****************************************************************************

from nicos.core import ConfigurationError, Measurable, Param
from nicos.core import oneof, status

try:
    from daqmw.daqmwcom import daqmwcom
except ImportError:
    daqmwcom = None


class uNIDController(Measurable):
    status_map = {
        'idle': (status.OK, 'Service is not running'),
        'running': (status.BUSY, 'Service is running'),
        'paused': (status.BUSY, 'Service is paused'),
        'error': (status.ERROR, 'Error in remote service'),
    }

    parameters = {
        'urlbase': Param('URL where service is running.',
                         type=str, settable=False, mandatory=True),
        '_service_status': Param('Internal service status',
                                 type=oneof(*status_map.keys()),
                                 userparam=False, default='idle')
    }

    _daqmwcom = None
    _preset = {}

    def doInit(self, mode):
        if daqmwcom is None:
            raise ConfigurationError(self, 'daqmw package is missing')

        self._daqmwcom = daqmwcom(self.urlbase)

    def doStatus(self, maxage=0):
        return self.status_map[self._service_status]

    def doRead(self, maxage=0):
        return ''

    def doSetPreset(self, **preset):
        self._preset = preset

    def doStart(self):
        if 'runNo' not in self._preset:
            self.log.error("Must specify 'runNo' preset: unid.start(runNo=...)")
            return

        self.log.info('Starting')
        ret = self._daqmwcom.start(str(self._preset['runNo']))
        self.log.info('uNID Response: ' + str(ret))
        self._setROParam('_service_status', 'running')
        self.poll()

    def doFinish(self):
        self.doStop()

    def doStop(self):
        self.log.info('Stopping')
        ret = self._daqmwcom.stop()
        self.log.info('uNID Response: ' + str(ret))
        self._setROParam('_service_status', 'idle')
        self.poll()

    def doPause(self):
        self.log.info('Pausing')
        ret = self._daqmwcom.pause()
        self.log.info('uNID Response: ' + str(ret))
        self._setROParam('_service_status', 'paused')
        self.poll()

    def doResume(self):
        self.log.info('Resuming')
        ret = self._daqmwcom.resume()
        self.log.info('uNID Response: ' + str(ret))
        self._setROParam('_service_status', 'running')
        self.poll()
