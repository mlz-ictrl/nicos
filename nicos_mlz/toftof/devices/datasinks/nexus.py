#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Nexus data sink classes for TOFTOF."""

from __future__ import absolute_import, division, print_function

import os
from time import localtime, strftime, time as currenttime

from nicos import session
from nicos.core.constants import LIVE
from nicos.pycompat import from_maybe_utf8

from nicos_mlz.toftof.devices import calculations as calc
from nicos_mlz.toftof.devices.datasinks.base import TofSink, TofSinkHandler
from nicos_mlz.toftof.devices.datasinks.nxtoftof import NXtofsingle, string_


class TofNeXuSHandler(TofSinkHandler):

    def __init__(self, sink, dataset, detector):
        TofSinkHandler.__init__(self, sink, dataset, detector)

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        _, filenames = self.manager.getFilenames(self.dataset, self._template,
                                                 self._subdir)
        self._filename = filenames[0]
        self._tof = NXtofsingle('detector', name=string_('Scan'))
        #                        dinfo=self.sink._detinfo_parsed[1:])
        self._tof.write_entry_identifier('%d' % self.dataset.counter)

    def begin(self):
        self._starttime = currenttime()
        self._local_starttime = localtime(self._starttime)

    def putResults(self, quality, results):
        if quality == LIVE:
            return
        elif self.detector.name in results:
            preset = float(self.dataset.metainfo['det', 'preset'][1])
            info = results[self.detector.name][0]
            if self.dataset.metainfo['det', 'mode'][1] != 'time':
                self._tof.write_times(
                    strftime('%d.%m.%YT%H:%M:%S', self._local_starttime),
                    strftime('%d.%m.%YT%H:%M:%S', localtime(currenttime())))
                val = int(info[1])
                if val < preset:
                    self._tof.write_togo('%d counts' %
                                         (int(preset) - val))
                else:
                    self._tof.write_togo('0 counts')
                self._tof.write_status('%5.1f %% completed' %
                                       (100. * val / preset))
            else:
                # This code looks a little bit strange, but this is due to the
                # problem of the buggy TACO timer device which sets the time to
                # the preset during a stop. This will also be done if the timer
                # is not finished yet. If the time between start time and
                # current time is less then the preset the counting is running
                # or stopped
                tim = min(currenttime() - self.dataset.started, float(info[0]))
                if tim > preset:
                    tim = preset
                self._tof.write_times(
                    strftime('%d.%m.%YT%H:%M:%S', self._local_starttime),
                    strftime('%d.%m.%YT%H:%M:%S', localtime(currenttime())),
                    tim)
                if tim < preset:
                    self._tof.write_togo('%.0f s' % (preset - tim))
                else:
                    self._tof.write_togo('0 s')
                self._tof.write_status('%5.1f %% completed' %
                                       (100. * tim / preset
                                        if preset else 100.))
            data = results[self.detector.name][1][0]
            if data is not None:
                self._tof.write_data(
                    data, self.dataset.metainfo['det', 'timechannels'][0])
                self._tof.write_monitor_data(
                    data[self.dataset.metainfo['det', 'monitorchannel'][0]])
                self._tof.write_sample_counts(int(info[2]),
                                              '%.3f' % (info[2] / info[0]
                                                        if info[0] else 0.))
                self._tof.write_monitor_integral(int(info[1]))
                self._tof.write_monitor_rate('%.3f' % (info[1] / info[0]
                                                       if info[0] else 0.))
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
                    self.log.info('Sample: current: %.4f K, average: %.4f K, '
                                  'stddev: %.4f K, min: %.4f K, max: %.4f K',
                                  _ct, _mean, _std, _min, _max)
                    self._tof.write_sample_temperature('%.4f K' % _mean,
                                                       '%.4f K' % _std,
                                                       '%.4f K' % _min,
                                                       '%.4f K' % _max)
                elif dev.name == 'B':
                    _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                    unit = dev.unit
                    self.log.info('Sample: current: %.4f %s, average: %.4f %s',
                                  (_mean, unit, _std, unit))
                    self._tof.write_sample_magfield('%.4f %s' % (_mean, unit),
                                                    '%.4f %s' % (_std, unit))
                elif dev.name == 'P':
                    self.log.info('Sample: current: %.4f %s, average: %.4f %s',
                                  (_mean, unit, _std, unit))
                    _mean, _std, _min, _max = self.dataset.valuestats[dev.name]
                    self._tof.write_sample_pressure('%.4f %s' % (_mean, unit),
                                                    '%.4f %s' % (_std, unit))
            self._save()

    def _save(self):
        tmpfilename = self._filename + '.new'
        self.log.debug('Create tmp NXS file: %s', tmpfilename)
        try:
            self._tof.save(tmpfilename, 'w5')
            self.log.debug('Rename from %s to %s', tmpfilename, self._filename)
            os.rename(tmpfilename, self._filename)
        except Exception as e:
            self.log.warning('Error occured during NeXuS writing: %s', e)
            try:
                os.remove(tmpfilename)
            except IOError:
                pass

    def putMetainfo(self, metainfo):
        if ('det', 'usercomment') in metainfo:
            usercomment = metainfo['det', 'usercomment'][1]
        elif ('det', 'info') in metainfo:
            usercomment = metainfo['det', 'info'][1]
        else:
            usercomment = ''
        self._tof.write_title(from_maybe_utf8(usercomment))
        self._tof.write_experiment_title(
            from_maybe_utf8(metainfo['Sample', 'samplename'][1]))
        self._tof.write_proposal_title(
            from_maybe_utf8(metainfo['Exp', 'title'][1]))
        self._tof.write_proposal_number(
            from_maybe_utf8(metainfo['Exp', 'proposal'][1]))

        self._tof.write_mode('Total_Time'
                             if metainfo['det', 'mode'][1] == 'time'
                             else 'MonitorCounts')

        slit_pos = metainfo['slit', 'value'][0]
        self._tof.write_slit_ho(slit_pos[0])
        self._tof.write_slit_hg(slit_pos[1])
        self._tof.write_slit_vo(slit_pos[2])
        self._tof.write_slit_vg(slit_pos[3])

        self._tof.write_hv_power_supplies('hv0-2: %s V, %s V, %s V' % tuple(
            [metainfo.get(('hv%d' % i, 'value'), (0, 'unknown'))[1]
             for i in range(3)]))
        self._tof.write_lv_power_supplies('lv0-7: %s' % ', '.join(
            [metainfo.get(('lv%d' % i, 'value'), (0, 'unknown'))[1]
             for i in range(8)]))
        self._tof.write_goniometer_xyz('%s %s %s %s %s %s' % (
            metainfo['gx', 'value'][1:3] + metainfo['gy', 'value'][1:3] +
            metainfo['gz', 'value'][1:3]))
        self._tof.write_goniometer_phicxcy('%s %s %s %s %s %s' % (
            metainfo['gphi', 'value'][1:3] + metainfo['gcx', 'value'][1:3] +
            metainfo['gcy', 'value'][1:3]))

        self._tof.write_local_contact(
            from_maybe_utf8(metainfo['Exp', 'localcontact'][1]))
        self._tof.write_user(from_maybe_utf8(metainfo['Exp', 'users'][1]))

        self._tof.write_chopper_vacuum(metainfo['vac0', 'value'][1],
                                       metainfo['vac1', 'value'][1],
                                       metainfo['vac2', 'value'][1],
                                       metainfo['vac3', 'value'][1])
        self._tof.write_chopper_speed(' '.join(metainfo['ch', 'value'][1:3]))
        self._tof.write_chopper_ratio(metainfo['chRatio', 'value'][1])
        self._tof.write_chopper_crc(metainfo['chCRC', 'value'][1])
        self._tof.write_chopper_slittype(metainfo['chST', 'value'][1])
        self._tof.write_chopper_delay(metainfo['chdelay', 'value'][1])
        self._tof.write_chopper_tof_time_preselection(
            metainfo['det', 'preset'][0])
        self._tof.write_chopper_tof_num_inputs(metainfo['det', 'numinputs'][1])
        self._tof.write_chopper_ch5_90deg_offset(
            metainfo['ch', 'ch5_90deg_offset'][1])
        self._tof.write_chopper_num_of_channels(
            metainfo['det', 'timechannels'][1])
        self._tof.write_chopper_num_of_detectors(
            metainfo['det', 'numinputs'][1])

        self._tof.write_wavelength(' '.join(metainfo['chWL', 'value'][1:3]))
        chwl = metainfo['chWL', 'value'][0]
        guess = round(4.e-6 * chwl * calc.alpha /
                      (calc.ttr * metainfo['det', 'channelwidth'][0]))
        self._tof.write_monitor_elastic_peak('%d' % guess)
        self._tof.write_monitor_tof(metainfo['det', 'channelwidth'][1],
                                    metainfo['det', 'timechannels'][1],
                                    metainfo['det', 'delay'][1])
        self._tof.write_monitor_tof_time_interval(
            metainfo['det', 'timeinterval'][1])
        self._tof.write_monitor_input(metainfo['det', 'monitorchannel'][1])
        self._tof.write_detinfo(self.detector._detinfo[2:])
        self._tof.write_sample_description(
            from_maybe_utf8(metainfo['Sample', 'samplename'][1]))

    def end(self):
        # self.log.info('%s' % self._tof._entry.nxroot.tree)
        if self._filename:
            self._save()
        self._tof = None


class TofNeXuS(TofSink):

    handlerclass = TofNeXuSHandler
