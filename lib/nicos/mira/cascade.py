#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""Class for CASCADE detector measurement and readout."""

__version__ = "$Revision$"

from nicos import session, status
from nicos.utils import tupleof, oneof
from nicos.device import Param, Override, Value
from nicos.abstract import ImageStorage, AsyncDetector
from nicos.errors import CommunicationError
from nicos.mira import cascadeclient
from nicos.detector import FRMDetector


class CascadeDetector(AsyncDetector, ImageStorage):

    parameters = {
        'server':   Param('"host:port" of the cascade server to connect to',
                          type=str, mandatory=True, preinit=True),
        'debugmsg': Param('Whether to print debug messages from the client',
                          type=bool, settable=True, default=False),
        'roi':      Param('Region of interest, given as (x1, y1, x2, y2)',
                          type=tupleof(int, int, int, int),
                          default=(-1, -1, -1, -1), settable=True),
        'mode':     Param('Data acquisition mode (tof or image)',
                          type=oneof(str, 'tof', 'image'), settable=True),
        'slave':    Param('Slave mode: start together with master device',
                          type=bool),
        'preselection': Param('Current preselection', unit='s',
                              settable=True, type=float),
        'lastcounts': Param('Counts of the last measurement',
                            type=tupleof(int, int), settable=True),
    }

    attached_devices = {
        'master':   FRMDetector,
    }

    parameter_overrides = {
        'fmtstr':   Override(default='roi %s, total %s, file %s'),
    }

    def doPreinit(self):
        if self._mode != 'simulation':
            self._client = cascadeclient.NicosClient()
            self.doReset()

    def doInit(self):
        self._last_preset = self.preselection
        AsyncDetector.doInit(self)

        # self._tres is set by doUpdateMode
        self._xres, self._yres = (128, 128)

    def doReset(self):
        self._client.disconnect()
        host, port = self.server.split(':')
        port = int(port)
        if not self._client.connecttohost(host, port):
            raise CommunicationError(self, 'could not connect to server')
        if self.slave:
            self._adevs['master'].reset()
        # reset parameters in case the server forgot them
        self.mode = self.mode
        self.preselection = self.preselection

    def valueInfo(self):
        cvals = (Value(self.name + '.roi', unit='cts', type='counter',
                       errors='sqrt', active=self.roi != (-1, -1, -1, -1)),
                 Value(self.name + '.total', unit='cts', type='counter',
                       errors='sqrt'), \
                 Value(self.name + '.file', type='info'))
        if self.slave:
            return self._adevs['master'].valueInfo() + cvals
        return cvals

    def doUpdateDebugmsg(self, value):
        if self._mode != 'simulation':
            cascadeclient.GlobalConfig.SetLogLevel(value and 3 or 0)

    def doShutdown(self):
        self._client.disconnect()

    def doStop(self):
        if self.slave:
            self._adevs['master'].stop()
        else:
            reply = str(self._client.communicate('CMD_stop'))
            if reply != 'OKAY':
                self._raise_reply('could not stop measurement', reply)

    def doRead(self):
        if self.slave:
            return self._adevs['master'].read() + self.lastcounts + \
                (self.lastfilename,)
        return self.lastcounts + (self.lastfilename,)

    def _getconfig(self):
        cfg = self._client.communicate('CMD_getconfig_cdr')
        if cfg[:4] != 'MSG_':
            self._raise_reply('could not get configuration', cfg)
        return dict(v.split('=') for v in str(cfg[4:]).split(' '))

    def doReadMode(self):
        return self._getconfig()['mode']

    def doWriteMode(self, value):
        reply = self._client.communicate('CMD_config_cdr mode=%s' % value)
        if reply != 'OKAY':
            self._raise_reply('could not set mode', reply)

    def doUpdateMode(self, value):
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and (128, 128) or (128, 128, 128)
        self._tres = (value == 'image') and 1 or 128

    def doReadPreselection(self):
        return float(self._getconfig()['time'])

    def doWritePreselection(self, value):
        reply = self._client.communicate('CMD_config_cdr time=%s' % value)
        if reply != 'OKAY':
            self._raise_reply('could not set measurement time', reply)

    def _devStatus(self):
        if not self._client.isconnected():
            return status.ERROR, 'disconnected from server'

    def doSetPreset(self, **preset):
        if preset.get('t'):
            self.preselection = self._last_preset = preset['t']

    def _startAction(self, **preset):
        self._newFile()
        if self.slave:
            self.preselection = 1000000  # master controls preset
        elif preset.get('t'):
            self.preselection = self._last_preset = preset['t']
        config = cascadeclient.GlobalConfig.GetTofConfig()
        config.SetImageWidth(self._xres)
        config.SetImageHeight(self._yres)
        config.SetImageCount(self._tres)
        config.SetPseudoCompression(False)

        reply = str(self._client.communicate('CMD_start'))
        if reply != 'OKAY':
            self._raise_reply('could not start measurement', reply)
        if self.slave:
            self._adevs['master'].start(**preset)

    def _measurementComplete(self):
        status = self._client.communicate('CMD_status_cdr')
        if status == '':
            raise CommunicationError(self, 'no response from server')
        #self.log.debug('got status %r' % status)
        status = dict(v.split('=') for v in str(status[4:]).split(' '))
        return status.get('stop', '0') == '1'

    def _duringMeasureAction(self, elapsedtime):
        self._readLiveData(elapsedtime)

    def _afterMeasureAction(self):
        # get final data including all events from detector
        buf = self._readLiveData(self._last_preset, self.lastfilename)
        # and write into measurement file
        self._writeFile(buf)

    def _measurementFailedAction(self, err):
        self.lastfilename = '<error>'

    def _readLiveData(self, elapsedtime, filename=''):
        # get current data array from detector
        data = self._client.communicate('CMD_readsram')
        if data[:4] != self._dataprefix:
            self._raise_reply('error receiving data from server', data)
        buf = buffer(data, 4)
        # send image to live plots
        session.updateLiveData(
            'cascade', filename, '<I4', self._xres, self._yres,
            self._tres, elapsedtime, buf)
        # determine total and roi counts
        total = self._client.counts(data)
        #ar = np.ndarray(buffer=buf, shape=self._datashape,
        #                order='F', dtype='<I4')
        #total = int(long(ar.sum()))
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            #roi = int(long(ar[x1:x2, y1:y2].sum()))
            roi = self._client.counts(data, x1, x2, y1, y2)
        else:
            roi = total
        self.lastcounts = (roi, total)
        return buf

    def _raise_reply(self, message, reply):
        if not reply:
            raise CommunicationError(self,
                message + ': empty reply (reset device to reconnect)')
        raise CommunicationError(self, message + ': ' + reply[4:])
