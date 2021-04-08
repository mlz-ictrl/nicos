#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Nexus data template for TOFTOF."""

import re
import time

import numpy as np

from nicos import session
from nicos.nexus.elements import ImageDataset, NexusElementBase, NXTime

from nicos_mlz.toftof.devices import calculations as calc


class ExperimentTitle(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        usercomment = metainfo.get(('det', 'usercomment'),
                                   metainfo.get(('det', 'info'),
                                                ('', '', '', '')))[0]
        dtype = 'S%d' % (len(usercomment) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(usercomment)


class EntryIdentifier(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        counter = '%d' % sinkhandler.dataset.counter
        dtype = 'S%d' % (len(counter) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(counter)


class Status(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        dtype = 'S%d' % (20 + 1)
        dset = h5parent.create_dataset(name, (1,), dtype=dtype)
        dset[0] = np.string_('0.0 %% completed')

    def results(self, name, h5parent, sinkhandler, results):
        if sinkhandler.detector is None:
            try:
                info = next(iter(results.values()))[0]
            except StopIteration:
                return
        else:
            info = results[sinkhandler.detector.name][0]

        metainfo = sinkhandler.dataset.metainfo
        preset = metainfo['det', 'preset'][0]
        if metainfo.get(('det', 'mode'),
                        ('time', 'time', '', ''))[1] != 'time':
            val = int(info[1])
        else:
            val = min(time.time() - sinkhandler.dataset.started,
                      float(info[0]))
        status = 100. * val / preset if val < preset else 100
        h5parent[name][0] = np.string_('%.1f %% completed' % status)


class ToGo(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        preset = metainfo['det', 'preset'][0]
        if metainfo.get(('det', 'mode'),
                        ('time', 'time', '', ''))[1] != 'time':
            dset = h5parent.create_dataset(name, (1,), dtype='int32')
            dset.attrs['units'] = np.string_('counts')
        else:
            dset = h5parent.create_dataset(name, (1,), dtype='float32',)
            dset.attrs['units'] = np.string_('s')
        dset[0] = preset

    def results(self, name, h5parent, sinkhandler, results):
        if sinkhandler.detector is None:
            try:
                info = next(iter(results.values()))[0]
            except StopIteration:
                return
        else:
            info = results[sinkhandler.detector.name][0]
        metainfo = sinkhandler.dataset.metainfo
        preset = metainfo['det', 'preset'][0]
        if metainfo.get(('det', 'mode'),
                        ('time', 'time', '', ''))[1] != 'time':
            val = int(info[1])
            togo = int(preset) - val if val < preset else 0
        else:
            tim = min(time.time() - sinkhandler.dataset.started,
                      float(info[0]))
            togo = preset - tim if tim < preset else 0
        h5parent[name][0] = togo


class Mode(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        if metainfo.get(('det', 'mode'),
                        ('time', 'time', '', ''))[1] == 'time':
            mode = 'Total_Time'
        else:
            mode = 'Monitor_Counts'
        dtype = 'S%d' % (len(mode) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(mode)


class StartTime(NXTime):

    def __init__(self):
        NXTime.__init__(self)
        self.time = 0

    def formatTime(self):
        return time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(self.time))

    def create(self, name, h5parent, sinkhandler):
        self.time = sinkhandler.dataset.started
        NXTime.create(self, name, h5parent, sinkhandler)


class EndTime(StartTime):

    def create(self, name, h5parent, sinkhandler):
        if sinkhandler.dataset.finished:
            self.time = sinkhandler.dataset.finished
        else:
            self.time = time.time()
        NXTime.create(self, name, h5parent, sinkhandler)

    def update(self, name, h5parent, sinkhandler, values):
        if sinkhandler.dataset.finished:
            self.time = sinkhandler.dataset.finished
        else:
            self.time = time.time()
        dset = h5parent[name]
        dset[0] = np.string_(self.formatTime())


class Duration(NexusElementBase):

    def _calc(self, dataset):
        duration = 0
        if dataset.started:
            duration = dataset.started
            if not dataset.finished:
                duration = time.time() - duration
            else:
                duration = dataset.finished - duration
        return int(round(duration))

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (1,), dtype='int32')
        dset.attrs['units'] = np.string_('s')
        dset[0] = self._calc(sinkhandler.dataset)

    def update(self, name, h5parent, sinkhandler, values):
        dset = h5parent[name]
        dset[0] = self._calc(sinkhandler.dataset)


class GonioDataset(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        phicxcy = '%s %s %s %s %s %s' % (
            metainfo['gphi', 'value'][1:3] + metainfo['gcx', 'value'][1:3] +
            metainfo['gcy', 'value'][1:3])
        dtype = 'S%d' % (len(phicxcy) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(phicxcy)


class TableDataset(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        xyz = '%s %s %s %s %s %s' % (
            metainfo['gx', 'value'][1:3] + metainfo['gy', 'value'][1:3] +
            metainfo['gz', 'value'][1:3])
        dtype = 'S%d' % (len(xyz) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(xyz)


class HVDataset(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        hv = 'hv0-2: %s V, %s V, %s V' % tuple(
            metainfo.get(('hv%d' % i, 'value'), (0, 'unknown'))[1]
            for i in range(3))
        dtype = 'S%d' % (len(hv) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(hv)


class LVDataset(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        lv = 'lv0-7: %s' % ', '.join(
            [metainfo.get(('lv%d' % i, 'value'), (0, 'unknown'))[1]
             for i in range(8)])
        dtype = 'S%d' % (len(lv) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(lv)


class FileName(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        filename = sinkhandler._filename
        dtype = 'S%d' % (len(filename) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.string_(filename)


class ElasticPeakGuess(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        chwl = metainfo['chWL', 'value'][0]
        guess = round(4.e-6 * chwl * calc.alpha /
                      (calc.ttr * metainfo['det', 'channelwidth'][0]))
        dset = h5parent.create_dataset(name, (1,), dtype='int32')
        dset[0] = int(guess)


class MonitorTof(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        dset = h5parent.create_dataset(name, (3,), dtype='float32')
        dset[0] = metainfo['det', 'channelwidth'][0]
        dset[1] = metainfo['det', 'timechannels'][0]
        dset[2] = metainfo['det', 'delay'][0]


class MonitorValue(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (1,), dtype='int32')
        dset.attrs['units'] = np.string_('counts')
        dset[0] = 0

    def results(self, name, h5parent, sinkhandler, results):
        if sinkhandler.detector is None:
            try:
                info = next(iter(results.values()))[0]
            except StopIteration:
                info = [0] * 3
        else:
            info = results[sinkhandler.detector.name][0]
        h5parent[name][0] = int(info[1])


class MonitorRate(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (1,), dtype='float32')
        dset.attrs['units'] = np.string_('1/s')
        dset[0] = 0

    def results(self, name, h5parent, sinkhandler, results):
        if sinkhandler.detector is None:
            try:
                info = next(iter(results.values()))[0]
            except StopIteration:
                info = [0] * 3
        else:
            info = results[sinkhandler.detector.name][0]
        h5parent[name][0] = info[1] / info[0] if info[0] else 0.


class SampleCounts(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (1,), dtype='int32')
        dset.attrs['units'] = np.string_('counts')
        dset[0] = 0

    def results(self, name, h5parent, sinkhandler, results):
        if sinkhandler.detector is None:
            try:
                info = next(iter(results.values()))[0]
            except StopIteration:
                info = [0] * 3
        else:
            info = results[sinkhandler.detector.name][0]
        h5parent[name][0] = int(info[2])


class SampleCountRate(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (1,), dtype='float32')
        dset.attrs['units'] = np.string_('1/s')
        dset[0] = 0

    def results(self, name, h5parent, sinkhandler, results):
        if sinkhandler.detector is None:
            try:
                info = next(iter(results.values()))[0]
            except StopIteration:
                info = [0] * 3
        else:
            info = results[sinkhandler.detector.name][0]
        h5parent[name][0] = info[2] / info[0] if info[0] else 0.


class MonitorData(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        det = sinkhandler.dataset.detectors[0]
        dset = h5parent.create_dataset(name, (det.timechannels,),
                                       dtype='int64')
        dset.attrs['units'] = np.string_('counts')
        dset.attrs['signal'] = 1

    def results(self, name, h5parent, sinkhandler, results):
        if sinkhandler.detector is None:
            try:
                data = next(iter(results.values()))[1][0]
            except StopIteration:
                return
        else:
            data = results[sinkhandler.detector.name][1][0]

        if data is not None:
            dset = h5parent[name]
            for i, v in enumerate(
                data[:, sinkhandler.dataset.metainfo['det',
                                                     'monitorchannel'][0]]):
                dset[i] = v


class DetInfo(NexusElementBase):

    def __init__(self, column):
        NexusElementBase.__init__(self)
        self.column = column

    def create(self, name, h5parent, sinkhandler):
        if sinkhandler.detector is None:
            return
        pattern = re.compile(r"((?:[^'\s+]|'[^']*')+)")
        block = sinkhandler.detector._detinfo[2:]
        nDet = len(block)
        detNr = np.zeros(nDet, dtype='int32')
        theta = np.zeros(nDet, dtype='float32')
        values = np.zeros(nDet, dtype='int32')
        haveBoxInfo = True
        list_of_none_detectors = []
        for i in range(nDet):
            line = block[i]
            entry = pattern.split(line)[1::2]
            _detNr = int(entry[0])
            if not _detNr == i + 1:
                raise Exception('Unexpected detector number')
            detNr[i] = _detNr
            theta[i] = float(entry[5])
            if self.column == 5:
                continue
            elif self.column == 13:
                if entry[self.column] == "'None'":
                    list_of_none_detectors.append(_detNr)
            elif haveBoxInfo and len(entry) == 16:
                values[i] = int(entry[self.column])
            elif len(entry) == 14:
                values[i] = int(entry[self.column])
                haveBoxInfo = False
            else:
                raise Exception('Unexpected number of entries in detector info'
                                ' line')
        inds = theta.argsort()
        theta = theta[inds]
        values = values[inds]
        if self.column == 13:
            list_of_none_detectors_angles = []
            for none_det in list_of_none_detectors:
                list_of_none_detectors_angles.append(
                    int(np.where(detNr == none_det)[0]))
            list_of_none_detectors_angles.sort()

            masked_detectors = np.zeros(len(list_of_none_detectors),
                                        dtype='int32')
            for i in range(len(list_of_none_detectors)):
                masked_detectors[i] = list_of_none_detectors_angles[i]

        if self.column == 5:  # theta
            dset = h5parent.create_dataset(name, (nDet,), dtype='float32')
        elif self.column == 13:
            dset = h5parent.create_dataset(name, (len(masked_detectors),),
                                           dtype='int32')
        else:
            dset = h5parent.create_dataset(name, (nDet,), dtype='int32')

        if self.column == 13:
            for i, v in enumerate(masked_detectors):
                dset[i] = v
            return
        if self.column == 5:
            for i, v in enumerate(theta):
                dset[i] = v
            return

        for i, v in enumerate(values):
            dset[i] = v


class TOFTOFImageDataset(ImageDataset):

    def create(self, name, h5parent, sinkhandler):
        self.testAppend(sinkhandler)
        if len(sinkhandler.dataset.detectors) <= self.detectorIDX:
            session.log.warning('Cannot find detector with ID %d',
                                self.detectorIDX)
            self.valid = False
            return
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        arrinfo = det.arrayInfo()
        myDesc = arrinfo[self.imageIDX]
        rawshape = det.numinputs, 1, det.timechannels
        dset = h5parent.create_dataset(name, rawshape,
                                       chunks=tuple(rawshape),
                                       dtype=myDesc.dtype,
                                       compression='gzip')
        self.createAttributes(dset, sinkhandler)

    def update(self, name, h5parent, sinkhandler, values):
        if not self.valid:
            return
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        if det.name not in values:
            return

    def results(self, name, h5parent, sinkhandler, results):
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        data = results.get(det.name)
        if data is not None:
            array = data[1][0]
            dset = h5parent[name]
            if self.doAppend:
                if len(dset) < self.np + 1:
                    self.resize_dataset(dset, sinkhandler)
                dset[self.np] = array
            else:
                ninputs = det.numinputs
                tchannels = det.timechannels
                reddata = array[0:tchannels, 0:ninputs]
                h5parent[name][...] = reddata.reshape(ninputs, 1, tchannels)

    def resize_dataset(self, dset, sinkhandler):
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        arrinfo = det.arrayInfo()
        myDesc = arrinfo[self.imageIDX]
        rawshape = myDesc.shape
        idx = self.np + 1
        shape = list(rawshape)
        shape.insert(0, idx)
        session.log.info('New shape: %r', shape)
        dset.resize(shape)


class ChannelList(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        det = sinkhandler.dataset.detectors[0]
        dset = h5parent.create_dataset(name, (det.timechannels,),
                                       dtype='float32')
        for i in range(det.timechannels):
            dset[i] = float(i + 1)
