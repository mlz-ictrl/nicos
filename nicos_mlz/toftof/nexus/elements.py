# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
from nicos.nexus.elements import ImageDataset, NexusElementBase, NXAttribute

from nicos_mlz.nexus import axis1
from nicos_mlz.toftof.lib import calculations as calc


class ExperimentTitle(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        usercomment = metainfo.get(('det', 'usercomment'),
                                   metainfo.get(('det', 'info'),
                                                ('', '', '', '')))[0]
        dtype = 'S%d' % (len(usercomment.encode('utf-8')) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.array(usercomment.encode('utf-8'), dtype=dtype)


class EntryIdentifier(NexusElementBase):

    def __init__(self, dtype='string'):
        NexusElementBase.__init__(self)
        self.dtype = dtype

    def create(self, name, h5parent, sinkhandler):
        counter = '%d' % sinkhandler.dataset.counter
        if self.dtype == 'string':
            dtype = 'S%d' % (len(counter) + 1)
            dset = h5parent.create_dataset(name, (1,), dtype)
            dset[0] = np.bytes_(counter)
        else:
            dset = h5parent.create_dataset(name, (1,), self.dtype)
            dset[0] = sinkhandler.dataset.counter


class Status(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        dtype = 'S%d' % (20 + 1)
        dset = h5parent.create_dataset(name, (1,), dtype=dtype)
        dset[0] = np.bytes_('0.0 %% completed')

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
        h5parent[name][0] = np.bytes_('%.1f %% completed' % status)


class ToGo(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        preset = metainfo.get(('det', 'preset'), (0, ))[0]
        if metainfo.get(('det', 'mode'),
                        ('time', 'time', '', ''))[1] != 'time':
            dset = h5parent.create_dataset(name, (1,), dtype='int32')
            dset.attrs['units'] = np.bytes_('counts')
        else:
            dset = h5parent.create_dataset(name, (1,), dtype='float32',)
            dset.attrs['units'] = np.bytes_('s')
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
        preset = metainfo.get(('det', 'preset'), (0, ))[0]
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
        dset[0] = np.bytes_(mode)


class MonitorMode(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        mode = 'monitor'
        if metainfo.get(('det', 'mode'),
                        ('time', 'time', '', ''))[1] == 'time':
            mode = 'timer'
        dtype = 'S%d' % (len(mode) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.bytes_(mode)


class Duration(NexusElementBase):

    def __init__(self, dtype='int32'):
        NexusElementBase.__init__(self)
        self.dtype = dtype

    def _calc(self, dataset):
        duration = 0
        if dataset.started:
            duration = dataset.started
            if not dataset.finished:
                duration = time.time() - duration
            else:
                duration = dataset.finished - duration
        if self.dtype in {'int', 'int32', 'int64'}:
            return int(round(duration))
        return duration

    def create(self, name, h5parent, sinkhandler):
        dset = h5parent.create_dataset(name, (1,), dtype=self.dtype)
        dset.attrs['units'] = np.bytes_('s')
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
        dset[0] = np.bytes_(phicxcy)


class TableDataset(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        xyz = '%s %s %s %s %s %s' % (
            metainfo['gx', 'value'][1:3] + metainfo['gy', 'value'][1:3] +
            metainfo['gz', 'value'][1:3])
        dtype = 'S%d' % (len(xyz) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.bytes_(xyz)


class HVDataset(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        hv = 'hv0-2: %s V, %s V, %s V' % tuple(
            metainfo.get(('hv%d' % i, 'value'), (0, 'unknown'))[1]
            for i in range(3))
        dtype = 'S%d' % (len(hv) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.bytes_(hv)


class LVDataset(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        lv = 'lv0-7: %s' % ', '.join(
            [metainfo.get(('lv%d' % i, 'value'), (0, 'unknown'))[1]
             for i in range(8)])
        dtype = 'S%d' % (len(lv) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.bytes_(lv)


class FileName(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        filename = sinkhandler._filename
        dtype = 'S%d' % (len(filename.encode('utf-8')) + 1)
        dset = h5parent.create_dataset(name, (1,), dtype)
        dset[0] = np.array(filename.encode('utf-8'), dtype=dtype)


class NeutronEnergy(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        metainfo = sinkhandler.dataset.metainfo
        energy = calc.Energy(metainfo['chWL', 'value'][0])
        dset = h5parent.create_dataset(name, (1,), dtype='float32')
        dset[0] = energy
        dset.attrs['units'] = np.bytes_('meV')


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
        dset.attrs['units'] = np.bytes_('counts')
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
        dset.attrs['units'] = np.bytes_('1/s')
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
        dset.attrs['units'] = np.bytes_('counts')
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
        dset.attrs['units'] = np.bytes_('1/s')
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


class SampleEnvironment(NexusElementBase):

    def __init__(self, device, unit):
        NexusElementBase.__init__(self)
        self.device = device
        self.unit = unit
        self._names = ['', 'standard_deviation_of_', 'minimum_', 'maximum_']

    def create(self, name, h5parent, sinkhandler):
        for s in self._names:
            dset = h5parent.create_dataset('%s%s' % (s, name), (1,),
                                           dtype='float32')
            dset.attrs['units'] = np.bytes_(self.unit)
            dset[0] = 0

    def results(self, name, h5parent, sinkhandler, results):
        for s, v in zip(self._names,
                        sinkhandler.dataset.valuestats[self.device]):
            h5parent['%s%s' % (s, name)][0] = v


class MonitorData(NexusElementBase):

    def create(self, name, h5parent, sinkhandler):
        det = sinkhandler.dataset.detectors[0]
        dset = h5parent.create_dataset(name, (det.timechannels,),
                                       dtype='int64')
        dset.attrs['units'] = np.bytes_('counts')
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

    def __init__(self, column, **attrs):
        NexusElementBase.__init__(self)
        self.column = column
        self.attrs = {}
        for key, val in attrs.items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    def create(self, name, h5parent, sinkhandler):
        pattern = re.compile(r"((?:[^'\s+]|'[^']*')+)")
        if sinkhandler.detector is None:
            block = sinkhandler.dataset.detectors[0]._detinfo[2:]
        else:
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
            if self.column == 13:
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
        detNr = detNr[inds]
        if self.column == 13:
            list_of_none_detectors_angles = []
            for none_det in list_of_none_detectors:
                list_of_none_detectors_angles.append(
                    int(np.where(detNr == none_det)[0][0]))
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
        elif self.column == 5:
            for i, v in enumerate(theta):
                dset[i] = v
        else:
            for i, v in enumerate(values):
                dset[i] = v
        self.createAttributes(dset, sinkhandler)


class DetectorDistances(DetInfo):

    def __init__(self, **attrs):
        DetInfo.__init__(self, 5, units='m', **attrs)

    def create(self, name, h5parent, sinkhandler):
        DetInfo.create(self, name, h5parent, sinkhandler)
        dset = h5parent[name]
        for i, _ in enumerate(dset):
            dset[i] = calc.Lsd


class TimeOfFlight(NexusElementBase):

    def __init__(self, **attrs):
        NexusElementBase.__init__(self, **attrs)
        self.attrs = {}
        for key, val in (attrs | {'axis': axis1, 'units': 's'}).items():
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val, 'string')
            self.attrs[key] = val

    def create(self, name, h5parent, sinkhandler):
        if sinkhandler.detector is None:
            det = sinkhandler.dataset.detectors[0].name
        else:
            det = sinkhandler.detector.name

        metainfo = sinkhandler.dataset.metainfo
        wl = metainfo['chWL', 'value'][0]
        # ch_width = metainfo[det, 'channelwidth'][0]
        timeinterval = metainfo[det, 'timeinterval'][0]
        nChannels = metainfo[det, 'timechannels'][0]
        dset = h5parent.create_dataset(name, (nChannels,), dtype='float32')
        tof = calc.t2(0, wl, calc.Lsd)
        for i in range(nChannels):
            dset[i] = i * timeinterval + tof
        self.createAttributes(dset, sinkhandler)


class AzimuthalAngles(DetInfo):

    azimuth = {
        1: -64.45,
        2: -46.347,
        3: -41.008,
        4: -37.831,
        5: -34.738,
        6: -0.0,
        7: -0.0,
        8: -0.0,
        9: -0.0,
        10: -0.0,
        11: -0.0,
        12: -0.0,
        13: -0.0,
        14: -0.0,
        15: -0.0,
        16: -0.0,
        17: -0.0,
        18: -0.0,
        19: -0.0,
        20: -0.0,
        21: 64.45,
        22: 46.347,
        23: 40.585,
        24: 37.831,
        25: 34.632,
        26: 76.801,
        27: 64.917,
        28: 56.679,
        29: 51.923,
        30: 49.171,
        31: 46.31,
        32: 43.942,
        33: 41.777,
        34: 39.922,
        35: 38.155,
        36: 36.639,
        37: 64.45,
        38: 46.347,
        39: 41.008,
        40: 37.831,
        41: 34.738,
        42: 32.164,
        43: 30.002,
        44: 28.171,
        45: 26.479,
        46: 25.032,
        47: 23.732,
        48: 22.562,
        49: 21.545,
        50: 21.093,
        51: 20.622,
        52: 20.172,
        53: 19.741,
        54: 19.33,
        55: 0.0,
        56: 0.0,
        57: 0.0,
        58: 0.0,
        59: 0.0,
        60: 0.0,
        61: 0.0,
        62: 0.0,
        63: 0.0,
        64: 0.0,
        65: 0.0,
        66: 0.0,
        67: 0.0,
        68: 0.0,
        69: 0.0,
        70: 0.0,
        71: 0.0,
        72: 0.0,
        73: 0.0,
        74: 0.0,
        75: 0.0,
        76: 0.0,
        77: 0.0,
        78: 0.0,
        79: 0.0,
        80: 0.0,
        81: 0.0,
        82: 0.0,
        83: 0.0,
        84: 0.0,
        85: 0.0,
        86: 0.0,
        87: 0.0,
        88: -64.45,
        89: -46.347,
        90: -40.585,
        91: -37.831,
        92: -34.632,
        93: -32.164,
        94: -30.002,
        95: -28.099,
        96: -26.479,
        97: -25.032,
        98: -23.732,
        99: -22.562,
        100: -21.503,
        101: -20.58,
        102: -20.168,
        103: -19.738,
        104: 35.235,
        105: 33.98,
        106: 33.388,
        107: 32.817,
        108: 32.265,
        109: 31.733,
        110: 31.218,
        111: 30.721,
        112: 30.241,
        113: 29.812,
        114: 29.362,
        115: 28.927,
        116: 28.538,
        117: 28.129,
        118: 27.764,
        119: 27.38,
        120: 27.037,
        121: 26.676,
        122: 26.353,
        123: 26.039,
        124: 25.709,
        125: 25.413,
        126: 25.126,
        127: 24.846,
        128: 24.552,
        129: 24.289,
        130: 24.032,
        131: 23.783,
        132: 23.54,
        133: 23.303,
        134: 23.074,
        135: 22.85,
        136: 22.632,
        137: 18.969,
        138: 18.591,
        139: 18.229,
        140: 17.91,
        141: 17.575,
        142: 17.28,
        143: 16.971,
        144: 16.673,
        145: 16.41,
        146: 16.134,
        147: 15.89,
        148: 15.633,
        149: 15.405,
        150: 15.165,
        151: 14.953,
        152: 14.729,
        153: 14.531,
        154: 14.339,
        155: 14.136,
        156: 13.956,
        157: 13.766,
        158: 13.597,
        159: 13.433,
        160: 13.259,
        161: 13.105,
        162: 12.942,
        163: 12.797,
        164: 12.656,
        165: 12.507,
        166: 12.374,
        167: 12.245,
        168: 12.108,
        169: 11.986,
        170: 11.867,
        171: 11.741,
        172: 11.629,
        173: 11.52,
        174: 11.403,
        175: 0.0,
        176: 0.0,
        177: 0.0,
        178: 0.0,
        179: 0.0,
        180: 0.0,
        181: 0.0,
        182: 0.0,
        183: 0.0,
        184: 0.0,
        185: 0.0,
        186: 0.0,
        187: 0.0,
        188: 0.0,
        189: 0.0,
        190: 0.0,
        191: 0.0,
        192: 0.0,
        193: 0.0,
        194: 0.0,
        195: 0.0,
        196: 0.0,
        197: 0.0,
        198: 0.0,
        199: 0.0,
        200: 0.0,
        201: 0.0,
        202: 0.0,
        203: 0.0,
        204: 0.0,
        205: 0.0,
        206: 0.0,
        207: 0.0,
        208: 0.0,
        209: 0.0,
        210: 0.0,
        211: 0.0,
        212: 0.0,
        213: 0.0,
        214: -19.327,
        215: -18.966,
        216: -18.588,
        217: -18.226,
        218: -17.907,
        219: -17.573,
        220: -17.278,
        221: -16.969,
        222: -16.671,
        223: -16.408,
        224: -16.132,
        225: -15.888,
        226: -15.631,
        227: -15.403,
        228: -15.164,
        229: -14.952,
        230: -14.728,
        231: -14.53,
        232: -14.337,
        233: -14.135,
        234: -13.955,
        235: -13.764,
        236: -13.595,
        237: -13.432,
        238: -13.258,
        239: -13.104,
        240: -12.941,
        241: -12.796,
        242: -12.655,
        243: -12.506,
        244: -12.373,
        245: -12.244,
        246: -12.107,
        247: -11.985,
        248: -11.866,
        249: -11.74,
        250: -11.628,
        251: -11.519,
        252: -11.403,
        253: 22.419,
        254: 22.213,
        255: 22.011,
        256: 21.815,
        257: 21.624,
        258: 21.438,
        259: 21.257,
        260: 21.08,
        261: 20.922,
        262: 20.754,
        263: 20.59,
        264: 20.43,
        265: 20.274,
        266: 20.122,
        267: 19.987,
        268: 19.841,
        269: 19.699,
        270: 19.572,
        271: 19.437,
        272: 19.305,
        273: 19.188,
        274: 19.062,
        275: 18.94,
        276: 18.831,
        277: 18.714,
        278: 18.61,
        279: 18.5,
        280: 18.392,
        281: 18.295,
        282: 18.193,
        283: 18.101,
        284: 18.003,
        285: 17.908,
        286: 17.823,
        287: 17.733,
        288: 17.652,
        289: 17.567,
        290: 11.3,
        291: 11.199,
        292: 11.101,
        293: 10.996,
        294: 10.902,
        295: 10.811,
        296: 10.722,
        297: 10.635,
        298: 10.543,
        299: 10.46,
        300: 10.38,
        301: 10.302,
        302: 10.225,
        303: 10.144,
        304: 10.072,
        305: 10.001,
        306: 9.932,
        307: 9.864,
        308: 9.799,
        309: 9.729,
        310: 9.666,
        311: 9.605,
        312: 9.546,
        313: 9.488,
        314: 9.431,
        315: 9.376,
        316: 9.317,
        317: 9.265,
        318: 9.214,
        319: 9.164,
        320: 9.115,
        321: 9.068,
        322: 9.021,
        323: 8.972,
        324: 8.928,
        325: 8.885,
        326: 8.843,
        327: 8.803,
        328: 0.0,
        329: 0.0,
        330: 0.0,
        331: 0.0,
        332: 0.0,
        333: 0.0,
        334: 0.0,
        335: 0.0,
        336: 0.0,
        337: 0.0,
        338: 0.0,
        339: 0.0,
        340: 0.0,
        341: 0.0,
        342: 0.0,
        343: 0.0,
        344: 0.0,
        345: 0.0,
        346: 0.0,
        347: 0.0,
        348: 0.0,
        349: 0.0,
        350: 0.0,
        351: 0.0,
        352: 0.0,
        353: 0.0,
        354: 0.0,
        355: 0.0,
        356: 0.0,
        357: 0.0,
        358: 0.0,
        359: 0.0,
        360: 0.0,
        361: 0.0,
        362: 0.0,
        363: 0.0,
        364: 0.0,
        365: 0.0,
        366: -11.299,
        367: -11.198,
        368: -11.1,
        369: -10.996,
        370: -10.902,
        371: -10.811,
        372: -10.722,
        373: -10.635,
        374: -10.543,
        375: -10.46,
        376: -10.38,
        377: -10.302,
        378: -10.225,
        379: -10.144,
        380: -10.072,
        381: -10.001,
        382: -9.932,
        383: -9.864,
        384: -9.799,
        385: -9.729,
        386: -9.666,
        387: -9.605,
        388: -9.546,
        389: -9.488,
        390: -9.431,
        391: -9.376,
        392: -9.317,
        393: -9.265,
        394: -9.214,
        395: -9.164,
        396: -9.115,
        397: -9.068,
        398: -9.021,
        399: -8.972,
        400: -8.928,
        401: -8.885,
        402: -8.844,
        403: -8.803,
        404: 17.49,
        405: 17.409,
        406: 17.336,
        407: 17.259,
        408: 17.19,
        409: 17.117,
        410: 17.052,
        411: 16.983,
        412: 16.921,
        413: 16.856,
        414: 16.798,
        415: 16.736,
        416: 16.681,
        417: 16.623,
        418: 16.572,
        419: 16.517,
        420: 16.469,
        421: 16.418,
        422: 16.372,
        423: 16.324,
        424: 16.282,
        425: 16.237,
        426: 16.198,
        427: 16.16,
        428: 16.12,
        429: 16.085,
        430: 16.048,
        431: 16.015,
        432: 15.981,
        433: 15.951,
        434: 15.92,
        435: 15.893,
        436: 15.867,
        437: 15.84,
        438: 15.817,
        439: 15.793,
        440: 15.772,
        441: 15.751,
        442: 8.763,
        443: 8.724,
        444: 8.687,
        445: 8.647,
        446: 8.611,
        447: 8.576,
        448: 8.543,
        449: 8.51,
        450: 8.478,
        451: 8.447,
        452: 8.416,
        453: 8.384,
        454: 8.356,
        455: 8.328,
        456: 8.301,
        457: 8.275,
        458: 8.25,
        459: 8.226,
        460: 8.202,
        461: 8.177,
        462: 8.155,
        463: 8.134,
        464: 8.113,
        465: 8.093,
        466: 8.074,
        467: 8.055,
        468: 8.037,
        469: 8.02,
        470: 8.004,
        471: 7.987,
        472: 7.972,
        473: 7.957,
        474: 7.944,
        475: 7.931,
        476: 7.918,
        477: 7.906,
        478: 7.895,
        479: 7.885,
        480: 7.874,
        481: 0.0,
        482: 0.0,
        483: 0.0,
        484: 0.0,
        485: 0.0,
        486: 0.0,
        487: 0.0,
        488: 0.0,
        489: 0.0,
        490: 0.0,
        491: 0.0,
        492: 0.0,
        493: 0.0,
        494: 0.0,
        495: 0.0,
        496: 0.0,
        497: 0.0,
        498: 0.0,
        499: 0.0,
        500: 0.0,
        501: 0.0,
        502: 0.0,
        503: 0.0,
        504: 0.0,
        505: 0.0,
        506: 0.0,
        507: 0.0,
        508: 0.0,
        509: 0.0,
        510: 0.0,
        511: 0.0,
        512: 0.0,
        513: 0.0,
        514: 0.0,
        515: 0.0,
        516: 0.0,
        517: 0.0,
        518: 0.0,
        519: 0.0,
        520: -8.763,
        521: -8.724,
        522: -8.687,
        523: -8.647,
        524: -8.611,
        525: -8.576,
        526: -8.543,
        527: -8.51,
        528: -8.478,
        529: -8.447,
        530: -8.416,
        531: -8.384,
        532: -8.356,
        533: -8.328,
        534: -8.301,
        535: -8.275,
        536: -8.25,
        537: -8.226,
        538: -8.202,
        539: -8.177,
        540: -8.155,
        541: -8.134,
        542: -8.113,
        543: -8.093,
        544: -8.074,
        545: -8.055,
        546: -8.037,
        547: -8.02,
        548: -8.004,
        549: -7.987,
        550: -7.972,
        551: -7.957,
        552: -7.944,
        553: -7.931,
        554: -7.918,
        555: -7.906,
        556: -7.895,
        557: -7.885,
        558: -7.874,
        559: 15.733,
        560: 15.716,
        561: 15.698,
        562: 15.684,
        563: 15.669,
        564: 15.657,
        565: 15.645,
        566: 15.636,
        567: 15.627,
        568: 15.619,
        569: 15.613,
        570: 15.608,
        571: 15.604,
        572: 15.601,
        573: 15.6,
        574: 15.6,
        575: 15.601,
        576: 15.604,
        577: 15.607,
        578: 15.612,
        579: 15.618,
        580: 15.626,
        581: 15.634,
        582: 15.644,
        583: 15.655,
        584: 15.668,
        585: 15.681,
        586: 15.695,
        587: 15.712,
        588: 15.729,
        589: 15.749,
        590: 15.768,
        591: 15.791,
        592: 15.813,
        593: 15.836,
        594: 15.862,
        595: 15.888,
        596: 7.865,
        597: 7.856,
        598: 7.848,
        599: 7.841,
        600: 7.834,
        601: 7.828,
        602: 7.823,
        603: 7.818,
        604: 7.813,
        605: 7.809,
        606: 7.806,
        607: 7.804,
        608: 7.802,
        609: 7.801,
        610: 7.8,
        611: 7.8,
        612: 7.801,
        613: 7.802,
        614: 7.804,
        615: 7.806,
        616: 7.809,
        617: 7.813,
        618: 7.817,
        619: 7.822,
        620: 7.827,
        621: 7.833,
        622: 7.84,
        623: 7.847,
        624: 7.855,
        625: 7.864,
        626: 7.873,
        627: 7.883,
        628: 7.893,
        629: 7.904,
        630: 7.916,
        631: 7.928,
        632: 7.941,
        633: 7.955,
        634: 0.0,
        635: 0.0,
        636: 0.0,
        637: 0.0,
        638: 0.0,
        639: 0.0,
        640: 0.0,
        641: 0.0,
        642: 0.0,
        643: 0.0,
        644: 0.0,
        645: 0.0,
        646: 0.0,
        647: 0.0,
        648: 0.0,
        649: 0.0,
        650: 0.0,
        651: 0.0,
        652: 0.0,
        653: 0.0,
        654: 0.0,
        655: 0.0,
        656: 0.0,
        657: 0.0,
        658: 0.0,
        659: 0.0,
        660: 0.0,
        661: 0.0,
        662: 0.0,
        663: 0.0,
        664: 0.0,
        665: 0.0,
        666: 0.0,
        667: 0.0,
        668: 0.0,
        669: 0.0,
        670: 0.0,
        671: 0.0,
        672: -7.865,
        673: -7.856,
        674: -7.848,
        675: -7.841,
        676: -7.834,
        677: -7.828,
        678: -7.823,
        679: -7.818,
        680: -7.813,
        681: -7.809,
        682: -7.806,
        683: -7.804,
        684: -7.802,
        685: -7.801,
        686: -7.8,
        687: -7.8,
        688: -7.801,
        689: -7.802,
        690: -7.804,
        691: -7.806,
        692: -7.809,
        693: -7.813,
        694: -7.817,
        695: -7.822,
        696: -7.827,
        697: -7.833,
        698: -7.84,
        699: -7.847,
        700: -7.855,
        701: -7.864,
        702: -7.873,
        703: -7.883,
        704: -7.893,
        705: -7.904,
        706: -7.916,
        707: -7.928,
        708: -7.941,
        709: -7.956,
        710: 15.917,
        711: 15.946,
        712: 15.978,
        713: 16.009,
        714: 16.044,
        715: 16.078,
        716: 16.113,
        717: 16.153,
        718: 16.191,
        719: 16.233,
        720: 16.274,
        721: 16.32,
        722: 16.364,
        723: 16.413,
        724: 16.46,
        725: 16.512,
        726: 16.562,
        727: 16.618,
        728: 16.671,
        729: 16.731,
        730: 16.787,
        731: 16.845,
        732: 16.91,
        733: 16.971,
        734: 17.04,
        735: 17.105,
        736: 17.177,
        737: 17.252,
        738: 17.323,
        739: 17.402,
        740: 17.476,
        741: 17.559,
        742: 17.637,
        743: 17.725,
        744: 17.808,
        745: 17.9,
        746: 7.97,
        747: 7.985,
        748: 8.001,
        749: 8.017,
        750: 8.034,
        751: 8.052,
        752: 8.07,
        753: 8.089,
        754: 8.109,
        755: 8.132,
        756: 8.153,
        757: 8.175,
        758: 8.198,
        759: 8.221,
        760: 8.246,
        761: 8.271,
        762: 8.296,
        763: 8.326,
        764: 8.353,
        765: 8.382,
        766: 8.411,
        767: 8.441,
        768: 8.472,
        769: 8.504,
        770: 8.536,
        771: 8.57,
        772: 8.608,
        773: 8.643,
        774: 8.68,
        775: 8.717,
        776: 8.756,
        777: 8.795,
        778: 8.836,
        779: 8.881,
        780: 8.924,
        781: 8.968,
        782: 9.013,
        783: 0.0,
        784: 0.0,
        785: 0.0,
        786: 0.0,
        787: 0.0,
        788: 0.0,
        789: 0.0,
        790: 0.0,
        791: 0.0,
        792: 0.0,
        793: 0.0,
        794: 0.0,
        795: 0.0,
        796: 0.0,
        797: 0.0,
        798: 0.0,
        799: 0.0,
        800: 0.0,
        801: 0.0,
        802: 0.0,
        803: 0.0,
        804: 0.0,
        805: 0.0,
        806: 0.0,
        807: 0.0,
        808: 0.0,
        809: 0.0,
        810: 0.0,
        811: 0.0,
        812: 0.0,
        813: 0.0,
        814: 0.0,
        815: 0.0,
        816: 0.0,
        817: 0.0,
        818: 0.0,
        819: 0.0,
        820: 0.0,
        821: 0.0,
        822: -7.97,
        823: -7.985,
        824: -8.001,
        825: -8.017,
        826: -8.034,
        827: -8.052,
        828: -8.07,
        829: -8.089,
        830: -8.109,
        831: -8.132,
        832: -8.153,
        833: -8.175,
        834: -8.198,
        835: -8.221,
        836: -8.246,
        837: -8.271,
        838: -8.296,
        839: -8.326,
        840: -8.353,
        841: -8.382,
        842: -8.411,
        843: -8.441,
        844: -8.472,
        845: -8.504,
        846: -8.536,
        847: -8.57,
        848: -8.608,
        849: -8.643,
        850: -8.68,
        851: -8.717,
        852: -8.756,
        853: -8.795,
        854: -8.836,
        855: -8.881,
        856: -8.924,
        857: -8.968,
        858: -9.013,
        859: 17.987,
        860: 18.084,
        861: 18.184,
        862: 18.277,
        863: 18.382,
        864: 18.481,
        865: 18.591,
        866: 18.704,
        867: 18.81,
        868: 18.929,
        869: 19.041,
        870: 19.166,
        871: 19.294,
        872: 19.414,
        873: 19.549,
        874: 19.687,
        875: 19.816,
        876: 19.961,
        877: 20.11,
        878: 20.263,
        879: 20.406,
        880: 20.566,
        881: 20.731,
        882: 20.9,
        883: 21.058,
        884: 21.236,
        885: 21.418,
        886: 21.605,
        887: 21.797,
        888: 21.994,
        889: 22.179,
        890: 22.386,
        891: 22.599,
        892: 22.818,
        893: 23.043,
        894: 9.059,
        895: 9.106,
        896: 9.155,
        897: 9.209,
        898: 9.26,
        899: 9.312,
        900: 9.366,
        901: 9.421,
        902: 9.477,
        903: 9.535,
        904: 9.599,
        905: 9.66,
        906: 9.723,
        907: 9.786,
        908: 9.852,
        909: 9.919,
        910: 9.994,
        911: 10.065,
        912: 10.137,
        913: 10.211,
        914: 10.287,
        915: 10.365,
        916: 10.452,
        917: 10.535,
        918: 10.619,
        919: 10.705,
        920: 10.794,
        921: 10.893,
        922: 10.987,
        923: 11.083,
        924: 11.181,
        925: 11.282,
        926: 11.396,
        927: 11.503,
        928: 11.612,
        929: 11.725,
        930: 11.851,
        931: 0.0,
        932: 0.0,
        933: 0.0,
        934: 0.0,
        935: 0.0,
        936: 0.0,
        937: 0.0,
        938: 0.0,
        939: 0.0,
        940: 0.0,
        941: 0.0,
        942: 0.0,
        943: 0.0,
        944: 0.0,
        945: 0.0,
        946: 0.0,
        947: 0.0,
        948: 0.0,
        949: 0.0,
        950: 0.0,
        951: 0.0,
        952: 0.0,
        953: 0.0,
        954: 0.0,
        955: 0.0,
        956: 0.0,
        957: 0.0,
        958: 0.0,
        959: 0.0,
        960: 0.0,
        961: 0.0,
        962: 0.0,
        963: 0.0,
        964: 0.0,
        965: 0.0,
        966: 0.0,
        967: 0.0,
        968: 0.0,
        969: -9.059,
        970: -9.106,
        971: -9.155,
        972: -9.209,
        973: -9.26,
        974: -9.312,
        975: -9.366,
        976: -9.421,
        977: -9.477,
        978: -9.535,
        979: -9.599,
        980: -9.66,
        981: -9.723,
        982: -9.786,
        983: -9.852,
        984: -9.919,
        985: -9.994,
        986: -10.065,
        987: -10.137,
        988: -10.211,
        989: -10.287,
        990: -10.365,
        991: -10.452,
        992: -10.535,
        993: -10.619,
        994: -10.705,
        995: -10.794,
        996: -10.893,
        997: -10.987,
        998: -11.083,
        999: -11.181,
        1000: -11.282,
        1001: -11.396,
        1002: -11.503,
        1003: -11.612,
        1004: -11.725,
        1005: -11.851,
        1006: -11.971
    }

    def __init__(self, **attrs):
        DetInfo.__init__(self, 5, units='deg', **attrs)

    def create(self, name, h5parent, sinkhandler):
        DetInfo.create(self, name, h5parent, sinkhandler)
        dset = h5parent[name]
        for i, _ in enumerate(dset):
            dset[i] = self.azimuth[i + 1]
        self.createAttributes(dset, sinkhandler)


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
                tchannels = det.timechannels
                reddata = np.transpose(array[0:tchannels, det._detectormap])
                h5parent[name][...] = reddata.reshape(det.numinputs, 1,
                                                      tchannels)

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

    def __init__(self, axis=None):
        NexusElementBase.__init__(self)
        self.attrs = {}
        if axis is not None:
            if not isinstance(axis, NXAttribute):
                axis = NXAttribute(axis, 'string')
            self.attrs['axis'] = axis

    def create(self, name, h5parent, sinkhandler):
        det = sinkhandler.dataset.detectors[0]
        dset = h5parent.create_dataset(name, (det.timechannels,),
                                       dtype='float32')
        for i in range(det.timechannels):
            dset[i] = float(i + 1)
        self.createAttributes(dset, sinkhandler)
