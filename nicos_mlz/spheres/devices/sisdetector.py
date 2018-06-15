#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Stefan Rainow <s.rainow@fz-juelich.de>
#
# *****************************************************************************

"""
Devices for the SIS-detector at SPHERES
"""

from math import ceil
from numpy.core.numeric import array_equal

from nicos import session
from nicos.core import Param, LIVE, INTERMEDIATE, FINAL, INTERRUPTED, oneof, \
    status
from nicos.core.constants import SIMULATION
from nicos.core.params import Attach, Value, listof
from nicos.devices.generic.detector import Detector
from nicos.devices.tango import ImageChannel, NamedDigitalOutput
from nicos_mlz.spheres.devices.doppler import ELASTIC, INELASTIC

CHOPPER =  'chopper'
DOPPLER =  'doppler'
ENERGY =   'energy'
TIME =     'time'
SUMS1 =    'sums1'
SUMS2 =    'sums2'
TOTAL =    'total'
INACTIVE = 'inactive'
ACTIVE =   'active'

CHOPPERSIZE = 2
DOPPLERSIZE = 2
ENERGYSIZE =  4
TIMESIZE =    2
SUMSIZE =     2
TOTALSIZE =   1


class SISChannel(ImageChannel):
    """
    Spheres SIS ImageChannel
    """

    parameters = {
        'analyzers':         Param('Analyzer Crystal',
                                   type=oneof('Si111', 'Si311'),
                                   default='Si111'),
        'monochromator':     Param('Monochromator Crystal',
                                   type=oneof('Si111', 'Si311'),
                                   default='Si111'),
        'incremental':       Param('Incremental Mode',
                                   type=bool,
                                   settable=True),
        'inelasticinterval': Param('Interval for the inelastic scan',
                                   type=int,
                                   settable=True, default=1200),
        'regulardets':       Param('relevant detectors for the monitor',
                                   type=listof(int),
                                   volatile=True),
        'elasticparams':     Param('Interval and amount for one elastic scan '
                                   'datafile',
                                   type=listof(int),
                                   settable=True, volatile=True),
    }

    def __init__(self, name, **config):
        ImageChannel.__init__(self, name, **config)

        self._block = []
        self._reason = ''

        self._accumulated = []

    def clearAccumulated(self):
        self._accumulated = []

    def getMode(self):
        return self._dev.GetMeasureMode()

    def doReadElasticparams(self):
        return [self._dev.tscan_interval,
                self._dev.tscan_amount]

    def doWriteElasticparams(self, val):
        self._dev.tscan_interval = val[0]
        self._dev.tscan_amount = val[1]

    def setTscanAmount(self, amount):
        if session.sessiontype == SIMULATION:
            return
        if self.status()[0] == status.OK:
            self._dev.setProperties(['tscan_amount', str(amount)])

    def doPrepare(self):
        self._checkShutter()
        self._dev.Prepare()
        self._hw_wait()

    def doReadArray(self, quality):
        self.readresult = [sum(self._dev.value)]
        mode = self.getMode()

        if quality == LIVE:
            return [self._readLiveData()]
        elif quality == INTERMEDIATE:
            self._reason = 'intermediate'
        elif quality == FINAL:
            self._reason = 'final'
        elif quality == INTERRUPTED:
            self._reason = 'interrupted'

        if mode == ELASTIC:
            return self._readElastic()
        elif mode == INELASTIC:
            return self._readInelastic()

    def doReadRegulardets(self):
        return list(self._dev.GetRegularDetectors())

    def valueInfo(self):
        return (Value(name=TOTAL, type="counter", fmtstr="%d", unit="cts"),)

    def _readLiveData(self):
        # strip the timesteps from the provided dataset
        # return [self._dev.GetData(INACTIVE)[:48]]

        flux = self._dev.GetFlux()
        if self.getMode() == INELASTIC:
            live = self._readLiveInelastic()
        else:
            live = []

        return [flux, live]

    def _readLiveInelastic(self):
        r = [self._dev.GetTickData(ENERGY), self._dev.GetData(ENERGY)]

        return r

    def _readElastic(self):
        live = self._readLiveData()
        params = self._dev.GetParams() + \
            ['type', 'elastic'] + \
            self.getAdditionalParams()
        ticks = self._dev.GetTickData(TIME)
        counts = self._dev.GetData(TIME)

        data = [
            live,
            params,
            ticks,
            counts
        ]

        if self.incremental:
            self._incrementCounts(data)
            return self._accumulated

        return data

    def _readInelastic(self):
        live = self._readLiveData()
        params = self._dev.GetParams() + \
            ['type', 'inelastic'] + \
            self.getAdditionalParams()
        eticks = self._dev.GetTickData(ENERGY)
        edata = self._dev.GetData(ENERGY)
        cticks = self._dev.GetTickData(CHOPPER)
        cdata = self._dev.GetData(CHOPPER)

        data = [
            live,
            params,
            eticks,
            edata,
            cticks,
            cdata
        ]

        if self.incremental:
            self._incrementCounts(data)
            return self._accumulated

        return data

    def getAdditionalParams(self):
        return ['monochromator', self.monochromator,
                'analyzers', self.analyzers,
                'reason', self._reason,
                'incremental', self.incremental,
                'dets4mon', [self.regulardets[0], self.regulardets[-1]]]

    def _mergeCounts(self, total, increment):
        """
        Increments the first array, entry by entry with the corresponding
        entries from the second array.

        :param total: Array containing the summed up counts.
        :param increment: Array containing incremental counts.
        :return: incremented array
        """

        for i in range(len(total)):
            total[i] += increment[i]

        return total

    def _incrementCounts(self, data):
        """
        Increment accumulated data by the given data
        """

        if not self._accumulated:
            self._accumulated = data
            return

        mode = self.getMode()

        if mode == INELASTIC:
            if not array_equal(data[2], self._accumulated[2]):
                self.resetIncremental('Energy tick data does not match '
                                      'previous dataset.', data)
            if not array_equal(data[4], self._accumulated[4]):
                self.resetIncremental('Chopper tick data does not match '
                                      'previous dataset.', data)
            try:
                self._accumulated[3] = self._mergeCounts(self._accumulated[3],
                                                         data[3])

                self._accumulated[5] = self._mergeCounts(self._accumulated[5],
                                                         data[5])
            except IndexError:
                self.resetIncremental('Error while merging arrays. '
                                      'Lenght of accumulated(%d, %d) differs '
                                      'from provided(%d, %d) array. '
                                      'Switching to non incremental mode.'
                                      % (len(self._accumulated[3]),
                                         len(self._accumulated[5]),
                                         len(data[3]),
                                         len(data[5])), data)
                return

        # TODO: incremental for elastic? (readElastic)
        if mode == ELASTIC:
            if array_equal(data[2], self._accumulated[2]):
                self.log.warning('Time tick data does not match previous '
                                 'dataset. Switching to non incremental mode.')
                self.incremental = False
                self._accumulated = data
            try:
                self._accumulated[3] = self._mergeCounts(self._accumulated[3],
                                                         data[3])
            except IndexError:
                self.resetIncremental('Error while merging arrays. '
                                      'Lenght of accumulated(%d) differs '
                                      'from provided(%d) array. '
                                      'Switching to non incremental mode.'
                                      % (len(self._accumulated[3]),
                                         len(data[3])), data)

    def resetIncremental(self, message, data):
        self.log.warning(message + ' Switching to non incremental mode.')
        self.incremental = False
        self._accumulated = data


class SISDetector(Detector):
    """
    Detector device for the SIS detector at SPHERES.
    """

    parameters = {
        'autoshutter': Param(
            'Automatically open and close shutter as needed',
            type=bool,
            settable=True)
    }

    attached_devices = {
        'shutter': Attach('Shutter', NamedDigitalOutput)
    }

    def doSetPreset(self, **preset):
        Detector.doSetPreset(self, **preset)
        if 't' in preset and self._adevs['images'][0]._mode == 'elastic':
            duration = preset['t']
            interv = self._adevs['images'][0].tscaninterval

            self._adevs['images'][0].preselection = int(ceil(duration/interv))

    def doPrepare(self):
        self._checkShutter()

    def doFinish(self):
        Detector.doFinish(self)
        if self.autoshutter:
            self._attached_shutter.maw('close')

    def _checkShutter(self):
        if self._attached_shutter.read() in self._attached_shutter.CLOSEDSTATES:
            if self.autoshutter:
                self._attached_shutter.maw('open')
            else:
                self.log.warning('Shutter closed while counting: %s'
                                 % self._attached_shutter.status()[1])
