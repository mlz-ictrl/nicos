#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from collections import namedtuple

from nicos import session
from nicos.core import FINAL, INTERMEDIATE, LIVE, NicosError, Param, \
    UsageError, oneof, status
from nicos.core.constants import SIMULATION
from nicos.core.params import Attach, Value, listof
from nicos.devices.generic.detector import Detector
from nicos.devices.tango import BaseImageChannel, NamedDigitalOutput

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

EnergyHisto = namedtuple('EnergyHisto', 'energy '
                                        'c_refl_l c_refl_r '
                                        'c_open_l c_open_r '
                                        't_refl_l t_refl_r '
                                        't_open_l t_open_r')
TimeHisto = namedtuple('TimeHisto', 'tval '
                                    'c_refl c_open '
                                    't_refl t_open')
ChopperHisto = namedtuple('ChopperHisto', 'angle '
                                          'c_refl c_open '
                                          't_refl t_open')


class SISChannel(BaseImageChannel):
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
        'detamount':         Param('Amount of detectors for the reshaping '
                                   'of the read data.',
                                   type=int,
                                   default=16),
        'backgroundmode':    Param('Mode of the background chopper',
                                   type=float,
                                   volatile=True),
        'backgroundoffset':  Param('Count offset in relation to the first PST '
                                   'zero after each background zero.',
                                   type=float,
                                   settable=True,
                                   volatile=True),
        'chopperopen':       Param('Chopper is open in this range. If the '
                                   'first value is bigger then the second the '
                                   'area is wrapped around 360 deg',
                                   type=listof(float),
                                   settable=True,
                                   volatile=True),
        'chopperreflecting': Param('Chopper is reflecting in this range. If '
                                   'the first value is bigger then the second '
                                   'the area is wrapped around 360 deg',
                                   type=listof(float),
                                   settable=True,
                                   volatile=True),
        'chopstatisticlen':  Param('Revolutions for Background chopper '
                                   'statistics',
                                   type=int,
                                   settable=True,
                                   volatile=True),
        'backzerorange':     Param('Range of the pst zero passes for the last'
                                   'chopstatisticlen pst revolutions',
                                   type=listof(float),
                                   volatile=True),
        'measuremode':       Param('Mode in which the detector is measuring',
                                   type=oneof(ELASTIC, INELASTIC, SIMULATION),
                                   volatile=True),
    }

    def __init__(self, name, **config):
        BaseImageChannel.__init__(self, name, **config)

        self._block = []
        self._reason = ''

        self.clearAccumulated()

    def clearAccumulated(self):
        self._last_edata = None
        self._last_cdata = None

    def doReadElasticparams(self):
        return [self._dev.tscan_interval,
                self._dev.tscan_amount]

    def doWriteElasticparams(self, val):
        self._dev.tscan_interval = val[0]
        self._dev.tscan_amount = val[1]

    def doReadBackgroundmode(self):
        return self._dev.backgr_mode

    def doReadBackgroundoffset(self):
        return self._dev.backgr_offset

    def doWriteBackgroundoffset(self, value):
        self._dev.backgr_offset = value

    def doReadChopperopen(self):
        return [self._dev.chop_open_f,
                self._dev.chop_open_t]

    def doWriteChopperopen(self, value):
        if len(value) != 2:
            raise UsageError('Chopperopen needs exactly 2 values: '
                             '"from" and "to"')

        self._dev.chop_open_f = value[0]
        self._dev.chop_open_t = value[1]

    def doReadChopperreflecting(self):
        return [self._dev.chop_refl_f,
                self._dev.chop_refl_t]

    def doWriteChopperreflecting(self, value):
        if len(value) != 2:
            raise UsageError('Chopperreflecting needs exactly 2 values: '
                             '"from" and "to"')

        self._dev.chop_refl_f = value[0]
        self._dev.chop_refl_t = value[1]

    def doReadChopstatisticlen(self):
        return self._dev.chop_statisticlen

    def doWriteChopstatisticlen(self, value):
        self._dev.chop_statisticlen = value

    def doReadBackzerorange(self):
        return [self._dev.backgr_zero_min, self._dev.backgr_zero_max]

    def doReadMeasuremode(self):
        if session.sessiontype == SIMULATION:
            return SIMULATION
        return self._dev.GetMeasureMode()

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
        mode = self.measuremode

        if mode == SIMULATION:
            return []

        if quality == LIVE:
            return [self._readLiveData()]
        else:
            self._reason = quality

        if mode == ELASTIC:
            return self._readElastic()
        elif mode == INELASTIC:
            return self._readInelastic()

    def doReadRegulardets(self):
        if session.sessiontype == SIMULATION:
            return []
        return list(self._dev.GetRegularDetectors())

    def valueInfo(self):
        return Value(name=TOTAL, type="counter", fmtstr="%d", unit="cts"),

    def _readLiveData(self):
        if self.measuremode == INELASTIC:
            if self._last_edata is not None:
                if self.incremental:
                    live = self._readData(ENERGY)
                    self._mergeCounts(live, self._last_edata)
                else:
                    live = self._last_edata
            else:
                live = self._readData(ENERGY)
        else:
            live = []

        return live

    def _readElastic(self):
        live = self._readLiveData()
        params = self._dev.GetParams() + \
            ['type', 'elastic'] + \
            self.getAdditionalParams()
        data = self._readData(TIME)

        return live, params, data

    def _readInelastic(self):
        live = self._readLiveData()
        params = self._dev.GetParams() + \
            ['type', 'inelastic'] + \
            self.getAdditionalParams()
        edata = self._readData(ENERGY)
        cdata = self._readData(CHOPPER)

        if self.incremental:
            if self._reason == FINAL:
                self._processCounts(edata, cdata)
                edata = self._last_edata
                cdata = self._last_cdata
            else:
                self._mergeCounts(edata, self._last_edata)
                self._mergeCounts(cdata, self._last_cdata)

        return live, params, edata, cdata

    def _readData(self, target):
        '''Read the requested data from the hardware and generate the according
        histogram tuples to make further processing easier.
        '''

        if target == ENERGY:
            targettuple = EnergyHisto
        elif target == TIME:
            targettuple = TimeHisto
        elif target == CHOPPER:
            targettuple = ChopperHisto
        else:
            raise NicosError('Can not read "%s"-data. Target not supported' %
                             target)

        xvals = self._dev.GetTickData(target)
        xvalsize = len(xvals)
        rawdata = self._dev.GetData(target)
        rawdatasize = len(rawdata)

        data = []
        amount = rawdatasize // (xvalsize * self.detamount * 2)
        if target in [ENERGY, TIME]:
            self.readresult = [sum(rawdata[:rawdatasize // 2])]
        counts = rawdata[:rawdatasize // 2].reshape(amount, xvalsize,
                                                    self.detamount)
        times = rawdata[rawdatasize // 2:].reshape(amount, xvalsize,
                                                   self.detamount)

        # to filter out the superfluous zero arrays in the elastic scan
        # we only iterate over the amount of unique xvals. The arrays not yet
        # 'triggered' all have the corresponding xval of 0, same as the first
        # array. Thus every array corresponding to the 2nd+ 0 xval will not be
        # added.
        for i in range(len(set(xvals))):
            # first insert the xvalue
            block = [float(xvals[i])]
            # then add the i-th count array from each of the count blocks
            for h in range(amount):
                block.append(counts[h, i, :])
            # then add the corresponding timesteps the same way
            for h in range(amount):
                block.append(times[h, i, :])
            data.append(targettuple._make(block))

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
        """
        if not increment:
            return

        for i, entry in enumerate(total):
            for j, arr in enumerate(entry):
                if j == 0:
                    continue
                arr.__iadd__(increment[i][j])

    def _processCounts(self, edata, cdata):
        """
        Set data arrays to the right values for further processing.
        """

        if self._last_edata is None:
            self._last_edata = edata
            self._last_cdata = cdata
            return

        try:
            self._mergeCounts(self._last_edata, edata)
            self._mergeCounts(self._last_cdata, cdata)
        except IndexError:
            self.resetIncremental('Error while merging arrays. '
                                  'Lenght of accumulated(%d, %d) differs '
                                  'from provided(%d, %d) array. '
                                  'Switching to non incremental mode.'
                                  % (len(self._last_edata),
                                     len(self._last_cdata),
                                     len(edata),
                                     len(cdata)))
            return

    def resetIncremental(self, message):
        self.log.warning(message + ' Switching to non incremental mode.')
        self.incremental = False
        self._last_edata = None
        self._last_cdata = None

    def setDummyDoppler(self, speed):
        self._dev.dummy_doppvel = speed


class SISDetector(Detector):
    """
    Detector device for the SIS detector at SPHERES.
    """

    parameters = {
        'autoshutter': Param(
            'Automatically open and close shutter as needed',
            type=bool,
            settable=True),
    }

    attached_devices = {
        'shutter': Attach('Shutter', NamedDigitalOutput)
    }

    def doInit(self, mode):
        Detector.doInit(self, mode)

        self._continueCounting = False
        self._saveIntermediateFlag = False

    def doPause(self):
        Detector.doPause(self)
        self._saveIntermediate()

    def saveIntermediate(self):
        self._saveIntermediateFlag = True

    def _saveIntermediate(self):
        session.experiment.data.putResults(
            INTERMEDIATE, {self.name: self.readResults(INTERMEDIATE)})

    def duringMeasureHook(self, elapsed):
        if self._saveIntermediateFlag:
            self._saveIntermediate()
            self._saveIntermediateFlag = False
        return Detector.duringMeasureHook(self, elapsed)

    def getSisImageDevice(self):
        return self._adevs['images'][0]

    def doPrepare(self):
        self._checkShutter()

    def clearAccumulated(self):
        if self._continueCounting:
            return

        for image in self._attached_images:
            if isinstance(image, SISChannel):
                image.clearAccumulated()

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
