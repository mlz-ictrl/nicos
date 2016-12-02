#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Data sink classes (new API) for NICOS."""

import os

from time import asctime, localtime, strftime, time as currenttime

from nicos import session
from nicos.core.constants import LIVE
from nicos.pycompat import from_maybe_utf8

from nicos.toftof import calculations as calc
from nicos.toftof.datasinks.base import TofSink, TofSinkHandler
from nicos.utils import syncFile

import numpy as np


class TofImageSinkHandler(TofSinkHandler):

    def __init__(self, sink, dataset, detector):
        TofSinkHandler.__init__(self, sink, dataset, detector)
        self._logtemplate = self._template[0].replace('.raw', '.log')

    def prepare(self):
        session.data.assignCounter(self.dataset)
        self._datafile = session.data.createDataFile(
            self.dataset, self._template, self._subdir)
        self._logfile = session.data.createDataFile(
            self.dataset, self._logtemplate, self._subdir, nomeasdata=True)

    def begin(self):
        self._starttime = currenttime()
        self._local_starttime = localtime(self._starttime)

    def _writeHeader(self, fp, header):
        fp.seek(0)
        fp.write('File_Creation_Time: %s\n' % asctime())
        fp.write('Title: %s\n' %
                 from_maybe_utf8(header['det', 'usercomment'][1]))
        fp.write('ExperimentTitle: %s\n' %
                 from_maybe_utf8(header['Sample', 'samplename'][1]))
        fp.write('ProposalTitle: %s\n' %
                 from_maybe_utf8(header['Exp', 'title'][1]))
        fp.write('ProposalNr: %s\n' % header['Exp', 'proposal'][1])

        fp.write('ExperimentTeam: %s\n' %
                 from_maybe_utf8(header['Exp', 'users'][1]))
        fp.write('LocalContact: %s\n' %
                 from_maybe_utf8(header['Exp', 'localcontact'][1]))
        fp.write('StartDate: %s\n' % strftime('%d.%m.%Y',
                                              self._local_starttime))
        fp.write('StartTime: %s\n' % strftime('%H:%M:%S',
                                              self._local_starttime))
        if header['det', 'mode'][1] == 'time':
            fp.write('TOF_MMode: Total_Time\n')
            fp.write('TOF_TimePreselection: %d\n' %
                     header['det', 'preset'][0])
        else:
            fp.write('TOF_MMode: Monitor_Counts\n')
            fp.write('TOF_CountPreselection: %d\n' %
                     header['det', 'preset'][0])

        fp.write('TOF_TimeInterval: %f\n' %
                 header['det', 'timeinterval'][0])
        fp.write('TOF_ChannelWidth: %s\n' % header['det', 'channelwidth'][1])
        fp.write('TOF_TimeChannels: %s\n' % header['det', 'timechannels'][1])
        fp.write('TOF_NumInputs: %s\n' % header['det', 'numinputs'][1])
        fp.write('TOF_Delay: %s\n' % header['det', 'delay'][1])
        fp.write('TOF_MonitorInput: %s\n' %
                 header['det', 'monitorchannel'][1])

        fp.write('TOF_Ch5_90deg_Offset: %s\n' %
                 header['ch', 'ch5_90deg_offset'][1])
        chwl = header['chWL', 'value'][0]
        guess = round(4.0 * chwl * 1e-6 * calc.alpha /
                      (calc.ttr * header['det', 'channelwidth'][0]))
        fp.write('TOF_ChannelOfElasticLine_Guess: %d\n' % guess)

        fp.write('HV_PowerSupplies: hv0-2: %s V, %s V, %s V\n' %
                 tuple([header.get(('hv%d' % i, 'value'), (0, 'unknown'))[1]
                        for i in range(3)]))
        fp.write('LV_PowerSupplies: lv0-7: %s\n' %
                 ', '.join(
                     [header.get(('lv%d' % i, 'value'), (0, 'unknown'))[1]
                      for i in range(8)]))

        slit_pos = header['slit', 'value'][1].split()
        fp.write('SampleSlit_ho: %s\n' % slit_pos[0])
        fp.write('SampleSlit_hg: %s\n' % slit_pos[2])
        fp.write('SampleSlit_vo: %s\n' % slit_pos[1])
        fp.write('SampleSlit_vg: %s\n' % slit_pos[3])

        fp.write('Guide_config: %s\n' % header['ngc', 'value'][1])
        if header['ngc', 'value'][1] == 'focus':
            fp.write('ng_focus: %d %d %d %d\n' %
                     tuple(header.get(('ng_focus', 'value'),
                                      ([0, 0, 0, 0], '0 0 0 0'))[0]))
        fp.write('Chopper_Speed: %s %s\n' % header['ch', 'value'][1:3])
        fp.write('Chopper_Wavelength: %s %s\n' %
                 header['chWL', 'value'][1:3])
        fp.write('Chopper_Ratio: %s\n' % header['chRatio', 'value'][1])
        fp.write('Chopper_CRC: %s\n' % header['chCRC', 'value'][1])
        fp.write('Chopper_SlitType: %s\n' % header['chST', 'value'][1])
        fp.write('Chopper_Delay: %s\n' % header['chdelay', 'value'][1])

        for i in range(4):
            fp.write('Chopper_Vac%d: %s\n' %
                     (i, header['vac%d' % i, 'value'][1]))

        fp.write('Goniometer_XYZ: %s %s %s %s %s %s\n' % (
            header['gx', 'value'][1:3] + header['gy', 'value'][1:3] +
            header['gz', 'value'][1:3]))
        fp.write('Goniometer_PhiCxCy: %s %s %s %s %s %s\n' % (
            header['gphi', 'value'][1:3] + header['gcx', 'value'][1:3] +
            header['gcy', 'value'][1:3]))
        fp.write('FileName: %s\n' % self._datafile.filepath)
        fp.write('SavingDate: %s\n' % strftime('%d.%m.%Y'))
        fp.write('SavingTime: %s\n' % strftime('%H:%M:%S'))

        fp.flush()

    def _writeLogs(self, fp, stats):
        fp.seek(0)
        fp.write('%-15s\tmean\tstdev\tmin\tmax\n' % '# dev')
        for dev in self.dataset.valuestats:
            fp.write('%-15s\t%.3f\t%.3f\t%.3f\t%.3f\n' %
                     ((dev,) + self.dataset.valuestats[dev]))
        fp.flush()

    def writeData(self, fp, info, data):
        f = session.data.createDataFile(self.dataset,
                                        [self._template[0] + '.new', ],
                                        self._subdir, nomeasdata=True)
        self._writeHeader(f, self.dataset.metainfo)
        preset = float(self.dataset.metainfo['det', 'preset'][1])
        if self.dataset.metainfo['det', 'mode'][1] != 'time':
            if int(info[1]) < preset:
                f.write('ToGo: %d counts\n' % (int(preset) - int(info[1])))
            f.write('Status: %5.1f %% completed\n' %
                    (100. * int(info[1]) / preset))
        else:
            # This code looks a little bit strange, but this is due to the
            # problem of the buggy TACO timer device which sets the time to
            # the preset during a stop. This will also be done if the timer
            # is not finished yet. If the time between start time and current
            # time is less then the preset the counting is running or stopped
            time = min(currenttime() - self.dataset.started, float(info[0]))
            if time > preset:
                time = preset
            if time < preset:
                f.write('ToGo: %.0f s\n' % (preset - time))
            f.write('Status: %5.1f %% completed\n' % (100. * time / preset))

        tempfound = False
        for dev in session.experiment.sampleenv:
            if dev.name.startswith('T') or dev.name == 'bio':
                if tempfound:
                    continue
                tempfound = True
                _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                _ct = dev.read()
                if dev.unit == 'degC':
                    _ct += 273.15
                    _mean += 273.15
                    _min += 273.15
                    _max += 273.15
                f.write('AverageSampleTemperature: %10.4f K\n' % _mean)
                f.write('StandardDeviationOfSampleTemperature: %10.4f K\n' %
                        _std)
                f.write('MinimumSampleTemperature: %10.4f K\n' % _min)
                f.write('MaximumSampleTemperature: %10.4f K\n' % _max)
                self.log.info('Sample: current: %.4f K, average: %.4f K, '
                              'stddev: %.4f K, min: %.4f K, max: %.4f K',
                              _ct, _mean, _std, _min, _max)
            elif dev.name == 'B':
                _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                f.write('AverageMagneticfield: %.4f %s\n' % (_mean, dev.unit))
                f.write('StandardDeviationOfMagneticfield: %.4f %s\n' %
                        (_std, dev.unit))
            elif dev.name == 'P':
                _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                f.write('AveragePressure: %.4f %s\n' % (_mean, dev.unit))
                f.write('StandardDeviationOfPressure: %.4f %s\n' %
                        (_std, dev.unit))

        f.write('MonitorCounts: %d\n' % int(info[1]))
        f.write('TotalCounts: %d\n' % int(info[2]))
        f.write('MonitorCountRate: %.3f\n' % (info[1] / info[0]))
        f.write('TotalCountRate: %.3f\n' % (info[2] / info[0]))
        f.write('NumOfChannels: %s\n' %
                self.dataset.metainfo['det', 'timechannels'][1])
        f.write('NumOfDetectors: %s\n' %
                self.dataset.metainfo['det', 'numinputs'][1])
        # to ease interpreting the data...
        f.write('Plattform: %s\n' % os.uname()[0])
        # The detector information length is not correct it has 1 line more
        # than the number of the detectors
        f.write('aDetInfo(%u,%u): \n' % (14, self.detector._detinfolength - 1))
        f.write('%s' % ''.join(self.detector._detinfo))
        f.write('aData(%u,%u): \n' % (data.shape[0], data.shape[1]))
        np.savetxt(f, data, '%d')
        syncFile(f)
        self.log.debug('Rename from %s to %s', f.filepath, fp.filepath)
        os.rename(f.filepath, fp.filepath)

    def putResults(self, quality, results):
        if quality == LIVE:
            return
        if self.detector.name in results:
            result = results[self.detector.name]
            if result is None:
                return
            info = result[0]
            data = result[1][0]
            if data is not None:
                self.writeData(self._datafile, info, data)

    def end(self):
        self._writeLogs(self._logfile, self.dataset.valuestats)
        if self._datafile:
            self._datafile.close()


class TofImageSink(TofSink):

    handlerclass = TofImageSinkHandler
