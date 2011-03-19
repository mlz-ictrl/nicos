#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

from __future__ import with_statement

"""Class for CASCADE detector measurement and readout."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import threading
from os import path
from time import sleep

import cascadenicosobj

from nicos import session, status
from nicos.data import NeedsDatapath
from nicos.utils import existingdir, readFileCounter, updateFileCounter
from nicos.device import Measurable, Param
from nicos.errors import CommunicationError


class CascadeDetector(Measurable, NeedsDatapath):

    parameters = {
        'server':   Param('"host:port" of the cascade server to connect to',
                          type=str, mandatory=True),
        'debugmsg': Param('Whether to print debug messages from the client',
                          type=bool, settable=True, default=False),
        'nametemplate': Param('Template for the data file names',
                              type=str, default='cascade_%05d'),
        # XXX add ROI, MIEZE ROI, etc.
    }

    def doInit(self):
        self._client = cascadenicosobj.NicosClient()
        self.doReset()

        self._setDatapath(session.system.experiment.datapath)
        self._last_preset = 0  # XXX read from server
        self._measure = threading.Event()
        self._processed = threading.Event()
        self._processed.set()

        self._thread = threading.Thread(target=self._thread_entry)
        self._thread.setDaemon(True)
        self._thread.start()

    def _setDatapath(self, value):
        self._datapath = path.join(value, 'cascade')
        self._filenumber = readFileCounter(path.join(self._datapath, 'counter'))
        self._lastfilename = path.join(self._datapath,
                                       self.nametemplate % self._filenumber)

    def valueInfo(self):
        return ['time', 'cascade.filename'], ['s', '']

    def doWriteServerdebug(self, value):
        self._client.SetDebugLog(value)

    def doShutdown(self):
        self._client.disconnect()

    def doReset(self):
        self._client.disconnect()
        host, port = self.server.split(':')
        port = int(port)
        if not self._client.connecttohost(host, port):
            raise CommunicationError('could not connect to server')

    def doStatus(self):
        if not self._client.isconnected():
            return status.ERROR, 'disconnected from server'
        elif self._measure.isSet():
            return status.BUSY, 'measuring'
        elif not self._processed.isSet():
            return status.BUSY, 'processing',
        return status.OK, 'idle'

    def doStart(self, **preset):
        self._lastfilename = path.join(self._datapath,
                                       self.nametemplate % self._filenumber)
        self._filenumber += 1
        updateFileCounter(path.join(self._datapath, 'counter'), self._filenumber)
        self._processed.wait()
        self._processed.clear()
        if preset.get('t'):
            self._client.communicate('CMD_config time=%s' % preset['t'])
            self._last_preset = preset['t']
        self._measure.set()

    def doIsCompleted(self):
        return (self._processed.isSet()) and (not self._measure.isSet())

    def doStop(self):
        self._client.communicate('CMD_stop')

    def doRead(self):
        return [self._last_preset, self._lastfilename]

    def _thread_entry(self):
        while True:
            try:
                # wait for start signal
                self._measure.wait()
                # start measurement
                self._client.communicate('CMD_start')
                # wait for completion of measurement
                while True:
                    sleep(0.2)
                    status = self._client.communicate('CMD_status')
                    if status == '':
                        raise CommunicationError('no response from server')
                    #self.printdebug('got status %r' % status)
                    status = dict(v.split('=')
                                  for v in str(status[4:]).split(' '))
                    if status.get('stop', '0') == '1':
                        break
                    data = self._client.communicate('CMD_readsram')
                    # XXX send live data somewhere
                    session.emitfunc('new_livedata', data[4:])
            except:
                self._lastfilename = '<error>'
                self.printexception('measuring failed')
                self._measure.clear()
                self._processed.set()
                continue
            self._measure.clear()
            try:
                with open(self._lastfilename, 'w') as fp:
                    fp.write(self._client.communicate('CMD_readsram')[4:])
            except:
                self._lastfilename = '<error>'
                self.printexception('saving measurement failed')
            finally:
                self._processed.set()
