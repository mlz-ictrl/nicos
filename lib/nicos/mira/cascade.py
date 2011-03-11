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

from nicos import session
from nicos.utils import existingdir
from nicos.device import Measurable, Param


class CascadeDetector(Measurable):

    parameters = {
        'server': Param('"host:port" of the cascade server to connect to',
                        type=str, mandatory=True),
        'serverdebug': Param('', type=bool, settable=True, default=False),
    }

    def doInit(self):
        host, port = self.server.split(':')
        port = int(port)
        self._client = cascadenicosobj.NicosClient()
        self._client.connecttohost(host, port)
        self._filenumber = 0  # XXX
        self._lastfilename = ''
        self._last_preset = 0  # XXX read from server
        self._measure = threading.Event()
        self._processed = threading.Event()
        self._processed.set()

        self._thread = threading.Thread(target=self._thread_entry)
        self._thread.setDaemon(True)
        self._thread.start()

    def valueInfo(self):
        return ['time', 'filename'], ['s', '']

    def doWriteServerdebug(self, value):
        self._client.SetDebugLog(value)

    def doShutdown(self):
        self._client.disconnect()

    def doStart(self, **preset):
        self._lastfilename = path.join(session.system.datapath, 'cascade',
                                       'cascade_%s' % self._filenumber)
        self._filenumber += 1
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
                    sleep(0.05)
                    status = str(self._client.communicate('CMD_status'))
                    status = dict(v.split('=') for v in status[4:].split(' '))
                    #self.printdebug('got status %s' % status)
                    if status.get('stop', '0') == '1':
                        break
                    data = self._client.communicate('CMD_readsram')
                    #self.printdebug('got live data len=%d' % len(data))
                    # XXX send live data somewhere
            except:
                self._measure.clear()
                self._processed.set()
                self.printexception('measuring failed')
                continue
            self._measure.clear()
            try:
                with open(self._lastfilename, 'w') as fp:
                    fp.write(self._client.communicate('CMD_readsram')[4:])
            except:
                self.printexception('saving measurement failed')
            finally:
                self._processed.set()
