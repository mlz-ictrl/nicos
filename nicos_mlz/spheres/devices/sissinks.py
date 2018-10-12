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
# ****************************************************************************

'''
Sinks which handle the data provided from the SIS detector at SPHERES.
'''

from __future__ import absolute_import, division

from time import localtime, strftime

import numpy
import quickyaml

from nicos import session
from nicos.core.data.dataset import PointDataset, ScanDataset
from nicos.core.params import Param
from nicos.devices.datasinks import special
from nicos.devices.datasinks.image import ImageSink

from nicos_mlz.devices.yamlbase import YAMLBaseFileSinkHandler

timesteptime = 2e-5 #s = 20µs

class SisSinkHandlerBase(object):
    DETAMOUNT = 16

    def splitHisto(self, xvals, data, amount):
        """
        Takes 1 dataarray and redistributes the data into len(xvals) arrays
        [[0..16]*len(xvals)]*amount]*2 (data/timesteps)
        is transformed into
        len(xvals)*[xval, [data0(x)]..[dataN(x)], [timesteps0(x)]..[timestepsN(x)]]
        """

        ret = []

        histolen = len(data) // 2 // amount # = DETAMOUNT*amount*len(xvals)

        offset = len(data) // 2 # timestep offset

        for i in range(len(xvals)):
            # first insert the xvalue
            block = [float(xvals[i])]
            # then add all the data arrays in sets of self.DETAMOUNT
            for h in range(amount):
                block.append(data[h * histolen + i * self.DETAMOUNT:
                h* histolen + (i + 1) * self.DETAMOUNT])
            # then add the corresponding timesteps
            for h in range(amount):
                block.append(data[offset + h * histolen + i * self.DETAMOUNT:
                offset + h * histolen + (i + 1) * self.DETAMOUNT])

            ret.append(block)

        return ret


class SisYamlFileSinkHandlerBase(YAMLBaseFileSinkHandler, SisSinkHandlerBase):
    """
    Base for the Sis File Sinks
    """

    ENERGY = 0
    CHOPPER = 1
    TIME = 2

    # indices of data in the provided images
    TOTAL = 0         # (in)elastic
    PARAMS = 1        # (in)elastic
    TIMETICKS = 2     # elastic
    TIMEDATA = 3      # elastic
    ENERGYTICKS = 2   # inelastic
    ENERGYDATA = 3    # inelastic
    CHOPPERTICKS = 4  # inelastic
    CHOPPERDATA = 5   # inelastic

    def setScanDataSet(self):
        stack = session.data._stack
        if len(stack) >= 2 and isinstance(stack[-2], ScanDataset):
            self.scands = stack[-2]
        else:
            self.scands = None

    def toDict(self, plist):
        return {plist[i]: plist[i + 1] for i in range(0, len(plist), 2)}

    def convertTime(self, time):
        return strftime('%Y-%m-%d %a %H:%M:%S %Z', time)

    def writeData(self, fp, image):
        self.setScanDataSet()
        self.params = self.toDict(image[self.PARAMS])
        self.params['dets4mon'] = tuple(self.params['dets4mon'])

        self.inelasticmode = self.params['type'] == 'inelastic'

        self.buildFileContents(image)

        quickyaml.Dumper(width=self.max_yaml_width, indent=2,
            array_handling=self.yaml_array_handling).dump(self.contents, fp)

    def buildFileContents(self, image):
        self.contents = []

    def getCountDuration(self):
        return self.dataset.values['timer']

    def getDatasetFinish(self):
        return self.dataset.finished if self.dataset.finished \
            else self.dataset.started + self.getCountDuration()

    def extractFromHisto(self, image, histogram):
        if histogram == self.ENERGY and self.inelasticmode:
            xvals = image[self.ENERGYTICKS]
            histo = image[self.ENERGYDATA]
            amount = 4
        elif histogram == self.CHOPPER and self.inelasticmode:
            xvals = image[self.CHOPPERTICKS]
            histo = image[self.CHOPPERDATA]
            amount = 2
        elif histogram == self.TIME and not self.inelasticmode:
            xvals = image[self.TIMETICKS] # [i for i in range(len(image[1]))]
            histo = image[self.TIMEDATA]
            amount = 2
        else:
            return []

        return self.splitHisto(xvals, histo, amount)

    def formatValue(self, value, prec=2):
        if isinstance(value, float):
            return '%%.%df' % prec % value
        elif isinstance(value, int):
            return '%d' %value


class AYamlFileSinkHandler(SisYamlFileSinkHandlerBase):
    '''
    Filesinkhandler which writes the raw SIS data.
    '''

    # export format:
    # elastic:
    #     header:
    #         Meta
    #         History
    #         Shortpar
    #         DetectorSettings
    #     TimeHistograms
    #
    # inelastic(sum):
    #     header:
    #         Meta
    #         History
    #         Shortpar
    #         DetectorSettings
    #     EnergyHistograms
    #     ChopperHistograms
    #
    # inelastic(time):
    #     header:
    #         Meta
    #         History
    #         Shortpar
    #         DetectorSettings
    #     EnergyHistograms
    #     ChopperHistograms

    def buildFileContents(self, image):
        o = self._dict()

        o['Meta'] = self._dict()
        o['Meta']['format'] = 'acq5.2 for yaml1'
        o['Meta']['type'] = 'neutron scattering raw data'
        o['History'] = ['measured on SPHERES']
        o['Shortpar'] = self.getShortPar()
        o['DetectorSettings'] = self.getDetectorSettings()
        if self.inelasticmode:
            o['EnergyHistograms'] = self.extractFromHisto(image, self.ENERGY)
            o['ChopperHistograms'] = self.extractFromHisto(image, self.CHOPPER)
        else:
            o['TimeHistograms'] = self.extractFromHisto(image, self.TIME)

        self.contents = o

    def getScanDuration(self):
        if self.scands:
            duration = 0
            for subset in self.scands.subsets:
                if isinstance(subset, PointDataset):
                    duration += subset.detvaluelist[0]

            return duration

        return self.getCountDuration()

    def getShortPar(self):
        o = self._dict()

        o['spectrometer'] = 'SPHERES'
        o['expdir'] = session.experiment.proposal
        o['subscan'] = self.getSubScanNumber()
        if self.scands:
            o['scan_since'] = self.convertTime(localtime(self.scands.started))
        else:
            o['scan_since'] = self.convertTime(localtime(self.dataset.started))
        o['subs_since'] = self.convertTime(localtime(self.dataset.started))
        o['subs_until'] = self.convertTime(localtime(self.getDatasetFinish()))
        o['subs_duration'] = '%.6f' % self.getCountDuration()
        o['scan_duration'] = '%.6f' % self.getScanDuration()
        o['saved_because'] = self.params['reason']
        o['energy_resolved'] = self.inelasticmode
        o['daq_time_step'] = '%.6f s' % float(self.params['daq_time_step'])
        o['ndet'] = len(eval(self.params['distances']))
        o['analyzers'] = self.params['analyzers']
        o['monochromator'] = self.params['monochromator']
        o['chop_refl_from'] = '%.6f deg' % float(self.params['chopper_refl_from'])
        o['chop_refl_to'] = '%.6f deg' % float(self.params['chopper_refl_to'])
        o['chop_open_from'] = '%.6f deg' % float(self.params['chopper_open_from'])
        o['chop_open_to'] = '%.6f deg' % float(self.params['chopper_open_to'])


        if self.inelasticmode:
            o['incremental'] = bool(int(self.params['incremental']))
            o['elast_max'] = '%.6f ueV' % float(self.params['elast_max'])
            o['inelast_min'] = '%.6f ueV' % float(self.params['inelast_min'])
            o['path_dop_sam'] = '%.6f m' % float(self.params['path_dop_sam'])
            o['path_sam_ana'] = '%.6f m' % float(self.params['path_sam_ana'])
            o['path_sam_det'] = '%.6f m' % float(self.params['path_sam_det'])
        else:
            o['scan_time_step'] = self.params['scan_time_step'] + ' s'

        return o

    def getDetectorSettings(self):
        settings = []

        distances = eval(self.params['distances'])


        for i, entry in enumerate(distances):
            o = self._dict()
            o['det'] = i
            o['pathdiff'] = '%.5f' % entry

            settings.append(o)

        return settings

    def getSubScanNumber(self):
        if not self.scands:
            return 'live'
        return '%da%d' % (self.scands.counter, self.dataset.number)


class UYamlFileSinkHandler(SisYamlFileSinkHandlerBase):
    '''
    Filesinkhandler that writes processed SIS data.
    '''

    def __init__(self, sink, dataset, detector):
        SisYamlFileSinkHandlerBase.__init__(self, sink, dataset, detector)

        self._cache = session.cache

    def _createFile(self):
        SisYamlFileSinkHandlerBase._createFile(self)

    def buildFileContents(self, image):
        o = self._dict()
        o['Meta'] = self._dict()
        o['Meta']['format'] = 'usr5.6 for yaml1'
        o['Meta']['type'] = 'compact subscan data'
        # o['Warnings'] = []
        o['Shortpar'] = self.getShortpar()
        o['Longpar'] = self.getLongpar(self.dataset.started,
                                       self.getDatasetFinish())
        o['DetectorAngles'] = self._flowlist(eval(self.params['angles']))
        o['HistogramExplain'] = self.getHistoExplain()
        o['Histogram'] = self.getHistogram(image)

        self.contents = o

    def getAngles(self):
        o = self._dict()
        o['DetectorAngles'] = self._flowlist(eval(self.params['angles']))

        return o

    def getShortpar(self):
        # test without commented out lines, if frida does not complain remove
        o = self._dict()
        o['spectrometer'] = 'SPHERES'
        o['expdir'] = session.experiment.proposal
        o['scan'] = self.dataset.counter
        o['subscan'] = self.dataset.number
        #o['docfile_version'] = 0 # legacy
        o['team'] = session.experiment.users
        o['localcontact'] = session.experiment.localcontact
        o['title'] = session.experiment.title
        o['sample'] = session.experiment.sample.name
        # o['sample_geom'] = session.experiment.sample.description
        o['energy_resolved'] = self.inelasticmode
        if self.scands:
            o['scan_since'] = self.convertTime(localtime(self.scands.started))
        else:
            o['scan_since'] = self.convertTime(localtime(self.dataset.started))
        o['subs_since'] = self.convertTime(localtime(self.dataset.started))
        o['subs_until'] = self.convertTime(localtime(self.getDatasetFinish()))
        o['saved_because'] = self.params['reason']
        o['ndet'] = len(eval(self.params['distances']))
        o['daq_time_step'] = '%.6f s' % float(self.params['daq_time_step'])
        o['analyzers'] = self.params['analyzers']
        o['monochromator'] = self.params['monochromator']
        o['lambda_i'] = self.getWavelength(self.params['analyzers'])
        o['lambda_f'] = self.getWavelength(self.params['monochromator'])
        o['dets4mon'] = '%d..%d' % self.params['dets4mon']

        return o

    def getWavelength(self, crystal):
        if crystal == 'Si111':
            return '6.27095 Angstroem'
        elif crystal == 'Si311':
            return '3.27490 Angstroem'
        else:
            return ''

    def getLongpar(self, start, end):
        o = self._dict()

        o['env.sam.tmp'] = self.getDevicePars(start, end,
                                              self.sink.envcontroller)
        o['env.setp'] = self.getDevicePars(start, end,
                                           self.sink.setpointdev)

        return o

    def getDevicePars(self, start, end, dev):
        o = self._dict()
        values = self.dataset.valuestats[dev]

        o['units'] = self._cache.get(dev, 'unit')
        o['nobs'] = max(len(self._cache.history(dev, 'value', start, end)) - 1,
                        1)
        o['avge'] = values[0]
        o['stdv'] = values[1] if values[1] != float('inf') else 0
        o['min'] = values[2]
        o['max'] = values[3]

        return o

    def getHistoExplain(self):
        if self.inelasticmode:
            return ['energy (ueV)',
                    'pseudomonitor time steps',
                    'pseudomonitor counts',
                    'time steps',
                    'counts']
        else:
            return ['lineno',
                    'env.sam.tmp',
                    'env.setp',
                    'direct time steps',
                    'direct counts',
                    'elastic time steps',
                    'elastic counts']

    def getHistogram(self, image):
        histogram = []

        if self.inelasticmode:
            dets = list(self.params['dets4mon'])
            dets[1] = dets[1] + 1

            rawHistos = self.extractFromHisto(image, self.ENERGY)

            for i, entry in enumerate(rawHistos):
                # energy (1)
                row = list([entry[0]])
                # pseudomonitor timesteps (1)
                row.append(int(sum(entry[5] + entry[6]) /
                               (len(entry[5]) + len(entry[6])) / 2))
                # pseudomonitor counts (1)
                row.append(int(sum(entry[3][dets[0]:dets[1]] +
                                   entry[4][dets[0]:dets[1]])))
                #time steps (1)
                row.append(int(sum(entry[7] + entry[8]) /
                               (len(entry[7]) + len(entry[8])) / 2))
                # counts (16)
                row += [int(entry[1][x] + entry[2][x])
                        for x in range(self.DETAMOUNT)]

                histogram.append(self._flowlist(row))
        else:
            rawHistos = self.extractFromHisto(image, self.TIME)
            for i, entry in enumerate(rawHistos):
                # lineno (1)
                row = [float(i)]
                # env.sam.temp (1)
                row.append(self._cache.get(self.sink.envcontroller, 'value',
                                           mintime=entry[0]))
                # env.setp (1)
                row.append(self._cache.get(self.sink.setpointdev, 'value',
                                           mintime=entry[0]))
                # direct timesteps (1)
                row.append(float(sum(entry[3]) / len(entry[3])))
                # direct counts (1)
                row.append(int(sum(entry[2])))
                # elastic timesteps (1)
                row.append(float(sum(entry[4]) / len(entry[4])))
                # elastic counts (19)
                counts = [int(value) for value in entry[1]]
                row += counts

                histogram.append(self._flowlist(row))

        return histogram


class PreviewSinkHandler(special.LiveViewSinkHandler, SisSinkHandlerBase):
    def processArrays(self, result):
        previewdata = result[1][0][0]

        mergerows = 7

        if not previewdata:
            preview = numpy.zeros(1, dtype=numpy.uint32)
            self.abscissa = numpy.zeros(1, dtype=numpy.float32)
        else:
            p = self.splitHisto(previewdata[0], previewdata[1], 4)

            entryamount = len(p) // mergerows

            preview = numpy.zeros(entryamount, dtype=numpy.uint32)
            self.abscissa = numpy.zeros(entryamount, dtype=numpy.float32)

            for i in range(entryamount):
                energy = 0
                counts = 0
                tsteps = 0

                for j in range(mergerows):
                    index = i*mergerows+j
                    energy += p[index][0]
                    counts += sum(p[index][1]) + sum(p[index][2])
                    tsteps += sum(p[index][5]) + sum(p[index][6])

                self.abscissa[i] = energy/mergerows
                if tsteps == 0:
                    preview[i] = 0
                else:
                    preview[i] = counts / (tsteps * timesteptime) # = counts/s

        return [preview]

    def getAbscissa(self, result):
        return ['<f4']

    def getAbscissaArrays(self, result):
        return [self.abscissa]


class AFileSink(ImageSink):
    handlerclass = AYamlFileSinkHandler


class UFileSink(ImageSink):
    handlerclass = UYamlFileSinkHandler

    parameters = {
        'envcontroller':    Param('Environment temperature controller',
                                  type = str),
        'setpointdev':      Param('Device for the setpoint',
                                  type = str),
    }


class PreviewSink(special.LiveViewSink):
    handlerclass = PreviewSinkHandler
