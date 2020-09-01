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

from __future__ import absolute_import, division, print_function

import re
from datetime import datetime

import numpy as np
import pytz
# pylint: disable=no-name-in-module
from nexusformat.nexus import NeXusError, NXattr, NXdata, NXdetector, \
    NXdisk_chopper, NXentry, NXfield, NXinstrument, NXmonitor, NXroot, \
    NXsample, NXuser

from nicos_mlz.toftof.devices.datasinks.nxfile import NexusFile

# NXbeam, NXbeam_stop, NXcollimator, NXFile, NXgeometry, NXgroup, NXlink,
# NXlog, NXnote, NXpositioner, NXsource,


def string_(value):
    if not value:
        value = ' '
    f = NXfield(value, dtype='|S%d' % (len(value) + 1))
    return f


def string_attr(value):
    if not value:
        value = ' '
    a = NXattr(value, dtype='|S%d' % (len(value) + 1))
    return a


class NXtofsingle:

    def __init__(self, exptitle, *items, **opts):
        self._entry = NXentry(*items, **opts)
        self._entry.FileName = string_('')
        self._entry.data = NXdata()
        self._entry.user1 = NXuser(role=string_('local_contact'))
        self._entry.user2 = NXuser(role=string_('experiment_team'))
        # TODO data will not written correctly !!!
        # look into NexusFile class, where the list of axes has to be written
        self._entry.monitor = NXmonitor()  # axes='channel_number')
        self._entry.instrument = NXinstrument(platform=string_('Linux'))
        self._entry.instrument.name = string_('TOFTOF')
        self._entry.instrument.chopper = NXdisk_chopper()
        self._entry.instrument.detector = NXdetector()
        self._entry.sample = NXsample()
        self.root = NXroot(self._entry)

    def save(self, filename=None, mode='w5'):
        if filename:
            self._entry.FileName = string_(filename)
            # self.write_entry_identifier(string_(filename.replace(
            #     '.nxs', '')))
        self.nxpath = '/'
        # f = NXFile(filename, mode)
        f = NexusFile(filename, mode)
        f.writefile(self.root)

    def write_wavelength(self, value):
        val, unit = value.split()
        self._entry.wavelength = NXfield(float(val), dtype='float32',
                                         units=string_attr(unit))

    def write_title(self, value):
        self._entry.title = string_(value)

    def write_experiment_title(self, value):
        self._entry.experiment_identifier = string_(value)

    def write_entry_identifier(self, value):
        self._entry.entry_identifier = string_(value)

    def write_proposal_title(self, value):
        self._entry.proposal = string_(value)

    def write_proposal_number(self, value):
        if isinstance(value, str):
            self._entry.proposal_number = string_(value)
        else:
            self._entry.proposal_number = NXfield(int(value), dtype='int32')

    def write_mode(self, value):
        self._entry.mode = string_(value)

    def write_times(self, stime, etime, duration=None):
        fmtin = '%d.%m.%YT%H:%M:%S'
        fmtout = '%Y-%m-%dT%H:%M:%S%z'
        tzinfo = pytz.timezone('Europe/Berlin')
        t0 = datetime.strptime(stime, fmtin).replace(tzinfo=tzinfo)
        t1 = datetime.strptime(etime, fmtin).replace(tzinfo=tzinfo)
        if duration is None:
            duration = (t1 - t0).total_seconds()
        assert(duration >= 0)
        self._entry.start_time = string_(t0.strftime(fmtout))
        self._entry.end_time = string_(t1.strftime(fmtout))
        self._entry.duration = NXfield(int(duration), dtype='int32',
                                       units=string_attr('s'))

    def write_status(self, value):
        self._entry.status = string_(value)

    def write_togo(self, value):
        val, unit = value.split()
        self._entry.to_go = NXfield(float(val), dtype='float32',
                                    units=string_attr(unit))

    def write_slit_ho(self, value):
        # val, unit = value.split()
        self._entry.slit_ho = NXfield(float(value), dtype='float32',
                                      units=string_attr('mm'))

    def write_slit_hg(self, value):
        # val, unit = value.split()
        self._entry.slit_hg = NXfield(float(value), dtype='float32',
                                      units=string_attr('mm'))

    def write_slit_vo(self, value):
        # val, unit = value.split()
        self._entry.slit_vo = NXfield(float(value), dtype='float32',
                                      units=string_attr('mm'))

    def write_slit_vg(self, value):
        # val, unit = value.split()
        self._entry.slit_vg = NXfield(float(value), dtype='float32',
                                      units=string_attr('mm'))

    def write_hv_power_supplies(self, value):
        self._entry.instrument.hv_power_supplies = string_(value)

    def write_lv_power_supplies(self, value):
        self._entry.instrument.lv_power_supplies = string_(value)

    def write_goniometer_xyz(self, value):
        self._entry.instrument.goniometer_xyz = string_(value)

    def write_goniometer_phicxcy(self, value):
        self._entry.instrument.goniometer_phicxcy = string_(value)

    def write_local_contact(self, value):
        self._entry.user1.name = string_(value)

    def write_user(self, value):
        self._entry.user2.name = string_(value)

    def write_chopper_vacuum(self, vac0, vac1, vac2, vac3):
        if vac0 is not None:
            self._entry.instrument.chopper_vac0 = NXfield(
                float(vac0), dtype='float32', units=string_attr('mbar'))
        if vac1 is not None:
            self._entry.instrument.chopper_vac1 = NXfield(
                float(vac1), dtype='float32', units=string_attr('mbar'))
        if vac2 is not None:
            self._entry.instrument.chopper_vac2 = NXfield(
                float(vac2), dtype='float32', units=string_attr('mbar'))
        if vac3 is not None:
            self._entry.instrument.chopper_vac3 = NXfield(
                float(vac3), dtype='float32', units=string_attr('mbar'))

    def write_chopper_speed(self, value):
        val, unit = value.split()
        self._entry.instrument.chopper.rotation_speed = NXfield(
            float(val), dtype='float32', units=string_attr(unit))

    def write_chopper_ratio(self, value):
        self._entry.instrument.chopper.ratio = NXfield(int(value),
                                                       dtype='int32')

    def write_chopper_crc(self, value):
        self._entry.instrument.chopper.crc = NXfield(int(value),
                                                     dtype='int32')

    def write_chopper_slittype(self, value):
        self._entry.instrument.chopper.slit_type = NXfield(int(value),
                                                           dtype='int32')

    def write_chopper_delay(self, value):
        self._entry.instrument.chopper.delay = NXfield(int(value),
                                                       dtype='int32')

    def write_chopper_tof_time_preselection(self, value):
        self._entry.instrument.chopper.tof_time_preselection = NXfield(
            int(value), dtype='int32', units=string_attr('s'))

    def write_chopper_tof_num_inputs(self, value):
        self._entry.instrument.chopper.tof_num_inputs = NXfield(int(value),
                                                                dtype='int32')

    def write_chopper_ch5_90deg_offset(self, value):
        self._entry.instrument.chopper.tof_ch5_90deg_offset = NXfield(
            int(value), dtype='int32')

    def write_chopper_num_of_channels(self, value):
        self._entry.instrument.chopper.num_of_channels = NXfield(int(value),
                                                                 dtype='int32')

    def write_chopper_num_of_detectors(self, value):
        self._entry.instrument.chopper.num_of_detectors = NXfield(
            int(value), dtype='int32')

    def write_monitor_elastic_peak(self, value):
        self._entry.monitor.elastic_peak = NXfield(int(value), dtype='int32')

    def write_monitor_tof(self, width, timechannels, delay):
        tof = np.zeros(3, dtype='float32')
        tof[0] = width
        tof[1] = timechannels
        tof[2] = delay
        self._entry.monitor.time_of_flight = NXfield(tof)

    def write_monitor_tof_time_interval(self, value):
        self._entry.monitor.tof_time_interval = NXfield(
            float(value), dtype='float32', units=string_attr('s'))

    def write_monitor_integral(self, value):
        self._entry.monitor.integral = NXfield(int(value), dtype='int32')

    def write_monitor_rate(self, value):
        self._entry.monitor.monitor_count_rate = NXfield(
            float(value), dtype='float32', units=string_attr('1/s'))

    def write_monitor_input(self, value):
        self._entry.monitor.tof_monitor_input = NXfield(int(value),
                                                        dtype='int32')

    def write_monitor_data(self, value):
        self._entry.monitor.data = NXfield(value, signal=1, dtype='int64',
                                           # axis=string_attr('channel_number'),
                                           units=string_attr('counts'))

    def write_sample_description(self, value):
        self._entry.sample.description = string_(value)

    def write_sample_temperature(self, average, std, minimum, maximum):
        val, unit = average.split()
        self._entry.sample.temperature = NXfield(float(val), dtype='float32',
                                                 units=string_attr(unit))
        val, unit = std.split()
        self._entry.sample.standard_deviation_of_temperature = NXfield(
            float(val), dtype='float32', units=string_attr(unit))
        val, unit = minimum.split()
        self._entry.sample.minimum_temperature = NXfield(
            float(val), dtype='float32', units=string_attr(unit))
        val, unit = maximum.split()
        self._entry.sample.maximum_temperature = NXfield(
            float(val), dtype='float32', units=string_attr(unit))

    def write_sample_magfield(self, average, std, minimum=None, maximum=None):
        val, unit = average.split()
        self._entry.sample.magnetic_field = NXfield(
            float(val), dtype='float32', units=string_attr(unit))
        val, unit = std.split()
        self._entry.sample.standard_deviation_of_magnetic_field = NXfield(
            float(val), dtype='float32', units=string_attr(unit))
        if minimum:
            val, unit = minimum.split()
            self._entry.sample.minimum_magnetic_field = NXfield(
                float(val), dtype='float32', units=string_attr(unit))
        if maximum:
            val, unit = maximum.split()
            self._entry.sample.maximum_magnetic_field = NXfield(
                float(val), dtype='float32', units=string_attr(unit))

    def write_sample_pressure(self, average, std, minimum=None, maximum=None):
        val, unit = average.split()
        self._entry.sample.pressure = NXfield(float(val), dtype='float32',
                                              units=string_attr(unit))
        val, unit = std.split()
        self._entry.sample.standard_deviation_of_pressure = NXfield(
            float(val), dtype='float32', units=string_attr(unit))
        if minimum:
            val, unit = minimum.split()
            self._entry.sample.minimum_pressure = NXfield(
                float(val), dtype='float32', units=string_attr(unit))
        if maximum:
            val, unit = maximum.split()
            self._entry.sample.maximum_pressure = NXfield(
                float(val), dtype='float32', units=string_attr(unit))

    def write_sample_counts(self, total, rate):
        self._entry.sample.total_counts = NXfield(int(total), dtype='int32',
                                                  units=string_attr('counts'))
        self._entry.sample.total_count_rate = NXfield(
            float(rate), dtype='float32', units=string_attr('1/s'))

    def write_detinfo(self, block):
        nDet = len(block)
        detNr = np.zeros(nDet, dtype='int32')
        detRack = np.zeros(nDet, dtype='int32')
        detPlate = np.zeros(nDet, dtype='int32')
        detPos = np.zeros(nDet, dtype='int32')
        detRPos = np.zeros(nDet, dtype='int32')
        theta = np.zeros(nDet, dtype='float32')
        eleCard = np.zeros(nDet, dtype='int32')
        eleChan = np.zeros(nDet, dtype='int32')
        self.eleTotal = np.zeros(nDet, dtype='int32')
        BoxNr = np.zeros(nDet, dtype='int32')
        BoxChan = np.zeros(nDet, dtype='int32')

        list_of_none_detectors = []
        haveBoxInfo = True
        pattern = re.compile(r"((?:[^'\s+]|'[^']*')+)")
        for i in range(nDet):
            line = block[i]
            entry = pattern.split(line)[1::2]
            _detNr = int(entry[0])
            if not _detNr == i + 1:
                raise Exception('Unexpected detector number')
            detNr[i] = _detNr
            detRack[i] = int(entry[1])
            detPlate[i] = int(entry[2])
            detPos[i] = int(entry[3])
            detRPos[i] = int(entry[4])
            theta[i] = float(entry[5])
            eleCard[i] = int(entry[10])
            eleChan[i] = int(entry[11])
            self.eleTotal[i] = int(entry[12])
            if haveBoxInfo and len(entry) == 16:
                BoxNr[i] = int(entry[14])
                BoxChan[i] = int(entry[15])
            elif len(entry) == 14:
                haveBoxInfo = False
            else:
                raise Exception('Unexpected number of entries in detector info'
                                ' line')
            if entry[13] == "'None'":
                list_of_none_detectors.append(_detNr)

        inds = theta.argsort()
        theta = theta[inds]
        detNr = detNr[inds]
        detRack = detRack[inds]
        detPlate = detPlate[inds]
        detPos = detPos[inds]
        detRPos = detRPos[inds]
        eleCard = eleCard[inds]
        eleChan = eleChan[inds]
        self.eleTotal = self.eleTotal[inds]
        if haveBoxInfo:
            BoxNr = BoxNr[inds]
            BoxChan = BoxChan[inds]

        list_of_none_detectors_angles = []
        for i in range(len(list_of_none_detectors)):
            list_of_none_detectors_angles.append(
                int(np.where(detNr == list_of_none_detectors[i])[0]))
        list_of_none_detectors_angles.sort()

        self._entry.instrument.detector.detector_number = NXfield(detNr)
        self._entry.instrument.detector.det_rack = NXfield(detRack)
        self._entry.instrument.detector.det_plate = NXfield(detPlate)
        self._entry.instrument.detector.det_pos = NXfield(detPos)
        self._entry.instrument.detector.det_rpos = NXfield(detRPos)

        self._entry.instrument.detector.polar_angle = NXfield(theta)

        self._entry.instrument.detector.ele_card = NXfield(eleCard)
        self._entry.instrument.detector.ele_chan = NXfield(eleChan)
        self._entry.instrument.detector.ele_total = NXfield(self.eleTotal)

        if haveBoxInfo:
            self._entry.instrument.detector.box_nr = NXfield(BoxNr)
            self._entry.instrument.detector.box_chan = NXfield(BoxChan)

        masked_detectors = np.zeros(len(list_of_none_detectors), dtype='int32')
        for i in range(len(list_of_none_detectors)):
            masked_detectors[i] = list_of_none_detectors_angles[i]
        self._entry.instrument.detector.pixel_mask = NXfield(masked_detectors)

    def write_data(self, block, channels):
        try:
            self._entry.data.makelink(
                self._entry.instrument.detector.polar_angle)
        except NeXusError:
            pass
        nDet = len(self.eleTotal)
        data = []
        for i in range(nDet):
            data += block[self.eleTotal[i] - 1].tolist()

        data = np.array(data, dtype='int32').reshape((nDet, 1, int(channels)))
        self._entry.data.data = NXfield(data, signal=1, dtype='int32',
                                        # compression='lzf',
                                        axes=string_attr('2theta:channel_number'),
                                        units=string_attr('counts'))

        channel_number = np.arange(int(channels), dtype='float32')
        self._entry.data.channel_number = NXfield(channel_number)

    # def create_nexus(self, data, filename='mynexus.nxs'):
    #     self.write_wavelength(data['Chopper_Wavelength'])
    #     self.write_title(data['Title'] if 'Title' in data else '')
    #     self.write_experiment_title(data['ExperimentTitle']
    #                                 if 'ExperimentTitle' in data else '')
    #     self.write_entry_identifier(filename.split('_')[0])
    #     if 'ProposalTitle' in data:
    #         self.write_proposal_title(data['ProposalTitle'])
    #     self.write_proposal_number(data['ProposalNr'])
    #     self.write_mode(data['TOF_MMode'])
    #     self.write_status(data['Status'])
    #     self.write_times('%sT%s' % (data['StartDate'], data['StartTime']),
    #                      '%sT%s' % (data['SavingDate'], data['SavingTime']))
    #     if 'ToGo' in data:
    #         self.write_togo(data['ToGo'])
    #     self.write_slit_ho(data['SampleSlit_ho'])
    #     self.write_slit_hg(data['SampleSlit_hg'])
    #     self.write_slit_vo(data['SampleSlit_vo'])
    #     self.write_slit_vg(data['SampleSlit_vg'])
    #     self.write_hv_power_supplies(data['HV_PowerSupplies'])
    #     self.write_lv_power_supplies(data['LV_PowerSupplies'])
    #     self.write_goniometer_xyz(data['Goniometer_XYZ'])
    #     self.write_goniometer_phicxcy(data['Goniometer_PhiCxCy'])
    #     self.write_local_contact(data['LocalContact'])
    #     self.write_user(data['ExperimentTeam']
    #                     if 'ExperimentTeam' in data else '')

    #     vac0 = data['Chopper_Vac0'] if 'Chopper_Vac0' in data else None
    #     vac1 = data['Chopper_Vac1'] if 'Chopper_Vac1' in data else None
    #     vac2 = data['Chopper_Vac2'] if 'Chopper_Vac2' in data else None
    #     vac3 = data['Chopper_Vac3'] if 'Chopper_Vac3' in data else None
    #     self.write_chopper_vacuum(vac0, vac1, vac2, vac3)
    #     self.write_chopper_speed(data['Chopper_Speed'])
    #     self.write_chopper_ratio(data['Chopper_Ratio'])
    #     self.write_chopper_crc(data['Chopper_CRC'])
    #     self.write_chopper_slittype(data['Chopper_SlitType'])
    #     self.write_chopper_delay(data['Chopper_Delay'])
    #     self.write_chopper_tof_time_preselection(data['TOF_TimePreselection'])
    #     self.write_chopper_tof_num_inputs(data['TOF_NumInputs'])
    #     if 'TOF_Ch5_90deg_Offset' in data:
    #         self.write_chopper_ch5_90deg_offset(data['TOF_Ch5_90deg_Offset'])
    #     self.write_chopper_num_of_channels(data['NumOfChannels'])
    #     self.write_chopper_num_of_detectors(data['NumOfDetectors'])

    #     self.write_monitor_elastic_peak(data['TOF_ChannelOfElasticLine_Guess'])
    #     self.write_monitor_tof(data['TOF_ChannelWidth'],
    #                            data['TOF_TimeChannels'], data['TOF_Delay'])
    #     self.write_monitor_tof_time_interval(data['TOF_TimeInterval'])
    #     self.write_monitor_integral(data['MonitorCounts'])
    #     if 'MonitorCountRate' in data:
    #         self.write_monitor_rate(data['MonitorCountRate'])
    #     self.write_monitor_input(data['TOF_MonitorInput'])
    #     self.write_monitor_data(data['aData'][int(data['TOF_MonitorInput'])])

    #     self.write_sample_description('sample_description')
    #     if 'AverageSampleTemperature' in data:
    #         self.write_sample_temperature(data['AverageSampleTemperature'],
    #                                       data['StandardDeviationOfSampleTemperature'],
    #                                       data['MinimumSampleTemperature'],
    #                                       data['MaximumSampleTemperature'])
    #     self.write_sample_counts(data['TotalCounts'], data['TotalCountRate'])
    #     self.write_detinfo(data['aDetInfo'])
    #     self.write_data(data['aData'], data['NumOfChannels'])

    #     self.save(filename)
