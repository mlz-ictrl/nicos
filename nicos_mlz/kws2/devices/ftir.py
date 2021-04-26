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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Support for measuring in-situ with the FTIR spectrometer."""

from time import time as currenttime

from nicos import session
from nicos.core import Attach, Moveable, Measurable, Param, \
    Readable, status, NicosTimeoutError, Value, listof

BUSY = 1
READY = 2


class FTIRSpectro(Measurable):
    """Trigger FTIR measurements from NICOS."""

    hardware_access = True

    attached_devices = {
        'trigger_out': Attach('Output to start the FTIR', Moveable),
        'status_in':   Attach('Input to signal status', Readable),
        'fileno_in':   Attach('Input of file number', Readable),
        'polarizer':   Attach('Polarizer', Moveable),
    }

    parameters = {
        'polvalues': Param('Polarizer states to measure (if empty, do not '
                           'touch polarizer)', unit='deg',
                           type=listof(float), settable=True),
    }

    def doInit(self, mode):
        self._measuring = False
        self._presettime = 0
        self._nfinished = 0
        self._polindex = 0
        self._started = None
        self._duration = 0

    def doSetPreset(self, **preset):
        if 't' in preset:
            self._presettime = preset['t']

    def presetInfo(self):
        return ('t',)

    def doStart(self):
        self._measuring = True
        self._polindex = 0
        self._pol_move = False
        self._nfinished = -1
        self._started = currenttime()
        self._duration = 0
        self._firstfile = self._attached_fileno_in.read(0) + 1

    def doFinish(self):
        self.doStop()

    def doStop(self):
        self._measuring = False

    def doReset(self):
        self._measuring = False

    def doStatus(self, maxage=0):
        return status.BUSY if self._measuring else status.OK, \
            '%d done' % self._nfinished

    def doRead(self, maxage=0):
        if self._nfinished > 0:
            return [self._firstfile, self._firstfile + self._nfinished - 1]
        else:
            return [0, 0]

    def valueInfo(self):
        return Value('FTIR.first', 'other', fmtstr='%d'), \
            Value('FTIR.last', 'other', fmtstr='%d')

    def _wait_for(self, sig, name):
        i = 0
        while self._attached_status_in.read(0) != sig:
            session.delay(0.1)
            i += 1
            if i == 100:
                raise NicosTimeoutError(self, 'timeout waiting for %s '
                                        'signal from spectrometer' % name)

    def _start_measurement(self):
        self.log.debug('starting new FTIR measurement')
        # wait for READY signal - otherwise no measurement is planned
        self._wait_for(READY, 'READY')
        # a \_/ flank is needed to trigger start
        self._attached_trigger_out.start(0)
        session.delay(0.05)
        self._attached_trigger_out.start(1)
        self._wait_for(BUSY, 'BUSY')

    def duringMeasureHook(self, elapsed):
        if self._pol_move:
            if self._attached_polarizer.status(0)[0] != status.BUSY:
                self._pol_move = False
                self._start_measurement()
            return

        # start new measurement when needed
        spstatus = self._attached_status_in.read(0)
        if spstatus == BUSY:
            return
        self._nfinished += 1

        # after 1 measurement we know approximately how long it takes
        if self._nfinished == 1:
            self._duration = currenttime() - self._started
        # if we have less than an approximate duration to go, stop
        if currenttime() > self._started + self._presettime - self._duration:
            self.log.info('made %d FTIR measurement(s)', self._nfinished)
            self._measuring = False
            return
        # move to next polarizer position if wanted, else start measuring
        if self.polvalues:
            polvalue = self.polvalues[self._polindex % len(self.polvalues)]
            self._polindex += 1
            self.log.debug('moving polarizer to %s', polvalue)
            self._pol_move = True
            self._attached_polarizer.start(polvalue)
        else:
            self._start_measurement()

    def doIsCompleted(self):
        return self.status(0)[0] != status.BUSY
