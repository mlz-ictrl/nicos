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

"""Very simple class for CCD camera measurement and readout."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import threading
from os import path
from time import sleep

import TacoDevice

from nicos import session, status
from nicos.data import NeedsDatapath
from nicos.utils import readFileCounter, updateFileCounter
from nicos.device import Measurable, Param, Override, Value


# XXX this is not yet a TacoDevice since the server doesn't support the
# standard FRM methods

class CascadeDetector(Measurable, NeedsDatapath):

    parameters = {
        'tacodevice': Param('taco device name', type=str, mandatory=True,
                            preinit=True),
        'preselection': Param('Current preselection', unit='s',
                              settable=True, type=float),
        'lastfilename': Param('File name of the last measurement',
                              type=str, settable=True),
        'lastfilenumber': Param('File number of the last measurement',
                                type=int, settable=True),
    }

    parameter_overrides = {
        'pollinterval': Override(default=0)
    }

    def doPreinit(self):
        if self._mode != 'simulation':
            self._dev = TacoDevice.TacoDevice(self.tacodevice)
            self._dev.timeout(60)

    def doInit(self):
        self._dev.DevCCDInitialize()
        self._last_preset = self.preselection
        self._measure = threading.Event()
        self._processed = threading.Event()
        self._processed.set()

        if self._mode != 'simulation':
            self._thread = threading.Thread(target=self._thread_entry)
            self._thread.setDaemon(True)
            self._thread.start()

    def doReset(self):
        self._dev.DevCCDShutdown()
        self._dev.DevCCDInitialize()

    def doReadDatapath(self):
        return session.experiment.datapath

    def doUpdateDatapath(self, value):
        # always use only first data path
        self._datapath = path.join(value[0], 'ccd')
        self._counter = readFileCounter(path.join(self._datapath, 'counter'))
        self._setROParam('lastfilenumber', self._counter)
        self._setROParam('listfilename', 'ccd_%05d.fits' % self._counter)

    def valueInfo(self):
        return Value(self.name + '.file', type='info'),

    def doShutdown(self):
        self._dev.DevCCDShutdown()

    def doStatus(self):
        st = self._dev.DevCCDAcqStatus()
        if st == 0:
            return status.OK, 'idle'
        elif st == 1:
            return status.BUSY, 'recording'
        elif st == 2:
            return status.ERROR, 'temperature not stable'
        else:
            return status.ERROR, 'failure (code %d)' % st

    def doStart(self, **preset):
        if self._datapath is None:
            self.datapath = session.experiment.datapath
        self.lastfilename = path.join(
            self._datapath, self.nametemplate[self.mode] % self._counter)
        self.lastfilenumber = self._counter
        self._counter += 1
        updateFileCounter(path.join(self._datapath, 'counter'), self._counter)
        self._processed.wait()
        self._processed.clear()
        try:
            if preset.get('t'):
                self.preselection = self._last_preset = preset['t']
        except:
            self._processed.set()
            raise
        self._measure.set()

    def doIsCompleted(self):
        return not self._measure.isSet() and self._processed.isSet()

    def doStop(self):
        pass # not available?

    def doRead(self):
        return (self.lastfilename,)

    def doReadPreselection(self):
        return 20 # XXX cannot read this out yet

    def doWritePreselection(self, value):
        self._dev.DevCCDSetTimes(value * 1000)

    def _thread_entry(self):
        while True:
            try:
                # wait for start signal
                self._measure.wait()
                # start measurement
                self._dev.DevCCDAcqStart()
                # wait for completion of measurement
                st = self.doStatus()[0]
                while st == status.BUSY:
                    sleep(0.2)
                if st == status.ERROR:
                    raise Exception('failed')
            except:
                self.lastfilename = '<error>'
                self.log.exception('measuring failed')
                self._measure.clear()
                self._processed.set()
                continue
            self._measure.clear()
            try:
                data = self._dev.DevCCDReadImageBin()
                session.updateLiveData(
                    'ccd', '<I4', 2048, 2048, 1, self._last_preset, data)
                self._dev.DevCCDReadImageTif(self.lastfilename)
            except:
                self.lastfilename = '<error>'
                self.log.exception('saving measurement failed')
            finally:
                self._processed.set()
