#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

import numpy as np

from nicos import session
from nicos.core.constants import LIVE
from nicos.pycompat import from_maybe_utf8, to_utf8
from nicos_mlz.toftof.devices import calculations as calc
from nicos_mlz.toftof.devices.datasinks.base import TofSink, TofSinkHandler


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
        headlines = []
        headlines.append('File_Creation_Time: %s' % asctime())
        headlines.append('Title: %s' %
                         from_maybe_utf8(header['det', 'usercomment'][1]))
        headlines.append('ExperimentTitle: %s' %
                         from_maybe_utf8(header['Sample', 'samplename'][1]))
        headlines.append('ProposalTitle: %s' %
                         from_maybe_utf8(header['Exp', 'title'][1]))
        headlines.append('ProposalNr: %s' % header['Exp', 'proposal'][1])

        headlines.append('ExperimentTeam: %s' %
                         from_maybe_utf8(header['Exp', 'users'][1]))
        headlines.append('LocalContact: %s' %
                         from_maybe_utf8(header['Exp', 'localcontact'][1]))
        headlines.append('StartDate: %s' % strftime('%d.%m.%Y',
                                                    self._local_starttime))
        headlines.append('StartTime: %s' % strftime('%H:%M:%S',
                                                    self._local_starttime))
        if header['det', 'mode'][1] == 'time':
            headlines.append('TOF_MMode: Total_Time')
            headlines.append('TOF_TimePreselection: %d' %
                             header['det', 'preset'][0])
        else:
            headlines.append('TOF_MMode: Monitor_Counts')
            headlines.append('TOF_CountPreselection: %d' %
                             header['det', 'preset'][0])

        headlines.append('TOF_TimeInterval: %f' %
                         header['det', 'timeinterval'][0])
        headlines.append('TOF_ChannelWidth: %s' %
                         header['det', 'channelwidth'][1])
        headlines.append('TOF_TimeChannels: %s' %
                         header['det', 'timechannels'][1])
        headlines.append('TOF_NumInputs: %s' % header['det', 'numinputs'][1])
        headlines.append('TOF_Delay: %s' % header['det', 'delay'][1])
        headlines.append('TOF_MonitorInput: %s' %
                         header['det', 'monitorchannel'][1])

        headlines.append('TOF_Ch5_90deg_Offset: %s' %
                         header['ch', 'ch5_90deg_offset'][1])
        chwl = header['chWL', 'value'][0]
        guess = round(4.0 * chwl * 1e-6 * calc.alpha /
                      (calc.ttr * header['det', 'channelwidth'][0]))
        headlines.append('TOF_ChannelOfElasticLine_Guess: %d' % guess)

        headlines.append('HV_PowerSupplies: hv0-2: %s V, %s V, %s V' % tuple(
            [header.get(('hv%d' % i, 'value'), (0, 'unknown'))[1]
             for i in range(3)]))
        headlines.append('LV_PowerSupplies: lv0-7: %s' % ', '.join(
            [header.get(('lv%d' % i, 'value'), (0, 'unknown'))[1]
             for i in range(8)]))

        slit_pos = header['slit', 'value'][1].split()
        headlines.append('SampleSlit_ho: %s' % slit_pos[0])
        headlines.append('SampleSlit_hg: %s' % slit_pos[2])
        headlines.append('SampleSlit_vo: %s' % slit_pos[1])
        headlines.append('SampleSlit_vg: %s' % slit_pos[3])

        headlines.append('Guide_config: %s' % header['ngc', 'value'][1])
        if header['ngc', 'value'][1] == 'focus':
            headlines.append('ng_focus: %d %d %d %d' % tuple(
                header.get(('ng_focus', 'value'),
                           ([0, 0, 0, 0], '0 0 0 0'))[0]))
        headlines.append('Chopper_Speed: %s %s' % header['ch', 'value'][1:3])
        headlines.append('Chopper_Wavelength: %s %s' %
                         header['chWL', 'value'][1:3])
        headlines.append('Chopper_Ratio: %s' % header['chRatio', 'value'][1])
        headlines.append('Chopper_CRC: %s' % header['chCRC', 'value'][1])
        headlines.append('Chopper_SlitType: %s' % header['chST', 'value'][1])
        headlines.append('Chopper_Delay: %s' % header['chdelay', 'value'][1])

        for i in range(4):
            headlines.append('Chopper_Vac%d: %s' %
                             (i, header['vac%d' % i, 'value'][1]))

        headlines.append('Goniometer_XYZ: %s %s %s %s %s %s' % (
            header['gx', 'value'][1:3] + header['gy', 'value'][1:3] +
            header['gz', 'value'][1:3]))
        headlines.append('Goniometer_PhiCxCy: %s %s %s %s %s %s' % (
            header['gphi', 'value'][1:3] + header['gcx', 'value'][1:3] +
            header['gcy', 'value'][1:3]))
        headlines.append('FileName: %s' % self._datafile.filepath)
        headlines.append('SavingDate: %s' % strftime('%d.%m.%Y'))
        headlines.append('SavingTime: %s' % strftime('%H:%M:%S'))

        fp.seek(0)
        for line in headlines:
            fp.write(to_utf8('%s\n' % line))
        fp.flush()

    def _writeLogs(self, fp, stats):
        loglines = []
        loglines.append('%-15s\tmean\tstdev\tmin\tmax' % '# dev')
        for dev in self.dataset.valuestats:
            loglines.append('%-15s\t%.3f\t%.3f\t%.3f\t%.3f' %
                            ((dev,) + self.dataset.valuestats[dev]))
        fp.seek(0)
        for line in loglines:
            fp.write(to_utf8('%s\n' % line))
        fp.flush()

    def writeData(self, fp, info, data):
        lines = []
        f = session.data.createDataFile(self.dataset,
                                        [self._template[0] + '.new'],
                                        self._subdir, nomeasdata=True)
        self._writeHeader(f, self.dataset.metainfo)
        preset = float(self.dataset.metainfo['det', 'preset'][1])
        if self.dataset.metainfo['det', 'mode'][1] != 'time':
            if int(info[1]) < preset:
                lines.append('ToGo: %d counts' %
                             (int(preset) - int(info[1])))
            lines.append('Status: %5.1f %% completed' %
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
                lines.append('ToGo: %.0f s' % (preset - time))
            lines.append('Status: %5.1f %% completed' %
                         (100. * time / preset))

        tempfound = False
        for dev in session.experiment.sampleenv:
            if dev.name.startswith('T'):
                if not tempfound:
                    tempfound = True
                    _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                    _ct = dev.read()
                    if dev.unit == 'degC':
                        _ct += 273.15
                        _mean += 273.15
                        _min += 273.15
                        _max += 273.15
                    lines.append('AverageSampleTemperature: %10.4f K' % _mean)
                    lines.append('StandardDeviationOfSampleTemperature: %10.4f'
                                 'K' % _std)
                    lines.append('MinimumSampleTemperature: %10.4f K' % _min)
                    lines.append('MaximumSampleTemperature: %10.4f K' % _max)
                    self.log.info('Sample: current: %.4f K, average: %.4f K, '
                                  'stddev: %.4f K, min: %.4f K, max: %.4f K',
                                  _ct, _mean, _std, _min, _max)
            elif dev.name == 'B':
                _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                lines.append('AverageMagneticfield: %.4f %s' %
                             (_mean, dev.unit))
                lines.append('StandardDeviationOfMagneticfield: %.4f %s' %
                             (_std, dev.unit))
            elif dev.name == 'P':
                _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                lines.append('AveragePressure: %.4f %s' % (_mean, dev.unit))
                lines.append('StandardDeviationOfPressure: %.4f %s' %
                             (_std, dev.unit))

        lines.append('MonitorCounts: %d' % int(info[1]))
        lines.append('TotalCounts: %d' % int(info[2]))
        lines.append('MonitorCountRate: %.3f' % (info[1] / info[0]))
        lines.append('TotalCountRate: %.3f' % (info[2] / info[0]))
        lines.append('NumOfChannels: %s' %
                     self.dataset.metainfo['det', 'timechannels'][1])
        lines.append('NumOfDetectors: %s' %
                     self.dataset.metainfo['det', 'numinputs'][1])
        # to ease interpreting the data...
        lines.append('Plattform: %s' % os.uname()[0])
        # The detector information length is not correct it has 1 line more
        # than the number of the detectors
        lines.append('aDetInfo(%u,%u): ' %
                     (14, self.detector._detinfolength))
        # Remove the last '\n' which will be added again by writing header to
        # the file
        lines.append('%s' % ''.join(self.detector._detinfo).strip())
        lines.append('aData(%u,%u): ' % (data.shape[0], data.shape[1]))
        for line in lines:
            f.write(to_utf8('%s\n' % line))
        np.savetxt(f, data, '%d')
        f.close()
        self.log.debug('Rename from %s to %s', f.filepath, fp.filepath)
        os.rename(f.filepath, fp.filepath)

    def putResults(self, quality, results):
        if quality != LIVE and self.detector.name in results:
            result = results[self.detector.name]
            if result:
                info = result[0]
                data = result[1][0]
                if data is not None:
                    self.writeData(self._datafile, info, data)

    def end(self):
        self._writeLogs(self._logfile, self.dataset.valuestats)
        if self._datafile:
            self._datafile.close()
        if self._logfile:
            self._logfile.close()


class TofImageSink(TofSink):

    handlerclass = TofImageSinkHandler
