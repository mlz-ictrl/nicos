#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
"""The STRESSI specific CARESS data writing module."""

from __future__ import print_function

import struct
import time

from collections import OrderedDict, namedtuple

from nicos import custom_version, nicos_version, session
from nicos.core import Override
from nicos.core.constants import FINAL, POINT, SCAN, SUBSCAN
from nicos.core.data import DataSinkHandler
from nicos.core.errors import ConfigurationError
from nicos.devices.datasinks import FileSink
from nicos.pycompat import iteritems, string_types, to_utf8

import numpy as np

__version__ = '0.0.1'

INTEGERTYPE = 1
LONGINTEGER = 2
FLOATTYPE = 3
REALTYPE = 5
DOUBLETYPE = 11
INT64TYPE = 13
CHARTYPE = 16
STRINGTYPE = 17
ADDRTYPE = 18
MODIDTYPE = 19

ONOFFTYPE = 21
PMATRIXTYPE = 22
DAUTYPE = 23
ENUMERATIONTYPE = 24
DAUDATATYPE = 25


Device = namedtuple('Device', 'abslimits offset precision timeout')
Timer = namedtuple('Timer', 'value')


class CaressScanfileSinkHandler(DataSinkHandler):

    _wrote_header = False
    _scan_file = False
    _detvalues = None
    _buffer = ''
    _scan_type = 'SGEN1'

    def _file_tell(self):
        return self._file.tell()

    def _file_write(self, buf):
        self._file.write(buf)
        self._buffer += buf

    def _flush(self):
        # self._file.write(self._buffer)
        self._buffer = ''

    def _string(self, value):
        buf = '%c%s%s' % (CHARTYPE, self._len(len(value)),
                          to_utf8(value.upper()))
        self._file_write(buf)

    def _len(self, val):
        if val < 128:
            return '%c' % val
        elif val < 65536:
            return '%c%s' % (0x80 | INTEGERTYPE, struct.pack('h', val))
        else:
            return '%c%s' % (0x80 | LONGINTEGER, struct.pack('i', val))

    def _defcmd(self, cmd):
        buf = 'DEFCMD %s' % cmd
        self._string(buf)

    def _defdata(self, value):
        buf = 'DEFDAT %s' % value
        self._string(buf)

    def _write_string(self, key, data):
        self._defcmd(key)
        self._string(key)
        buf = '%c%c%c%s%s' % (0x80, CHARTYPE, 0x81, self._len(len(data)),
                              to_utf8(data))
        self._file_write(buf)

    def _write_integer(self, value, key=None):
        if key:
            self._defcmd(key)
            self._string(key)
        buf = '%c%c%s' % (LONGINTEGER, 1, struct.pack('i', int(value)))
        self._file_write(buf)

    def _write_short(self, value):
        buf = '%c%c%s' % (INTEGERTYPE, 1, struct.pack('h', int(value)))
        self._file_write(buf)

    def _write_float(self, value, key=None):
        if key:
            self._defcmd(key)
            self._string(key)
        buf = '%c%c%s' % (FLOATTYPE, 1, struct.pack('f', float(value)))
        self._file_write(buf)

    def _write_exptype(self, l):
        data = 'EXPTYPE'
        self._defcmd(data)
        self._string(data)
        buf = '%c' % 0x80
        for i in l:
            buf += '%c%c%c%c' % (0x80, CHARTYPE, 0x81, len(i))
        buf += '%c%c' % (0x81, 1)
        buf += '%s' % ''.join(l)
        self._file_write(buf)

    def _write_bls(self, d):
        data = 'BLS'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        buf = ''
        for i in d.values():
            buf += '%c%c%s%s' % (FLOATTYPE, 2, struct.pack('f', float(i[0])),
                                 struct.pack('f', float(i[1])))
        self._file_write(buf)

    def _write_float_group(self, group, d):
        data = group
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        for i in d.values():
            self._write_float(i)

    def _write_sof(self, d):
        self._write_float_group('SOF', d)

    def _write_tol(self, d):
        self._write_float_group('TOL', d)

    def _write_tmo(self, d):
        self._write_float_group('TMO', d)

    def _write_read(self, d):
        data = 'READ'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        for i in d.values():
            if not isinstance(i, string_types):
                self._write_float(i)

    def _write_mm1(self, d):
        data = 'MM1'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        for i in d.values():
            self._write_integer(i)

    def _write_sl1(self, d):
        data = 'SL1'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        buf = '%c' * len(d) % ((0, ) * len(d))
        self._file_write(buf)

    def _write_rela(self, d):
        data = 'RELA'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        buf = ''
        for i in d.values():
            value = i
            if not isinstance(value, tuple):
                value = (value, )
            buf += '%c%c' % (FLOATTYPE, len(value))
            for j in value:
                buf += struct.pack('f', float(j))
        self._file_write(buf)

    def _write_winda(self, d):
        data = 'WINDA'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        buf = ''
        for i in d.values():
            value = i
            if not isinstance(value, tuple):
                value = (value, )
            while len(value) < 4:
                value += (0, )
            buf += '%c%c' % (INTEGERTYPE, len(value))
            for j in value:
                buf += struct.pack('h', j)
        self._file_write(buf)

    def _write_setv(self, d):
        data = 'SETV'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        self._write_short(d['STEP'])
        buf = '%c' % 0  # no value for the scanning value
        self._file_write(buf)

    def _write_sgen(self, d):
        data = self._scan_type
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        self._write_short(d['STEP'])
        buf = '%c%c' % (FLOATTYPE, 2, )
        for i in d.keys():
            if i != 'STEP':
                for v in d[i]:
                    buf += struct.pack('f', float(v))
        self._file_write(buf)

    def _write_spec(self):
        data = 'SPEC'
        self._defcmd(data + '( %s)' % 'ADET')
        self._string(data)
        buf = '%c%c' % (0, 0)
        self._file_write(buf)

    def _write_setvalue(self, d):
        data = 'SETVALUE'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        self._write_short(d['STEP'])
        # buf = '%c' % 0)
        # self._file_write(buf)

    def _write_user_proposal(self, valuelist=None):
        for device, key, value in valuelist:
            if device == 'Exp' and key == 'users':
                self._write_string('USN', value)
        for device, key, value in valuelist:
            if device == 'Exp' and key == 'proposal':
                self._write_string('PROPOSAL', value)

    def _write_comment(self, valuelist=None):
        comment = self.dataset.info.split('-')
        if len(comment) > 1:
            comment = comment[0].strip()
        else:
            for device, key, value in valuelist:
                if device == 'Exp' and key == 'remark':
                    comment = value
                    break
        self._write_string('COM', comment)

    def _write_sample(self, valuelist):
        for device, key, value in valuelist:
            if device == 'Sample' and key == 'samplename':
                self._write_string('SAM', value)

    def _write_title(self, valuelist):
        for device, key, value in valuelist:
            if device == 'Exp' and key == 'title':
                self._write_string('TITLE', value)

    def _write_version(self):
        self._write_string('VERSIONTEXT', 'NICOS %s(%s); Data Sink %s' %
                           (nicos_version, custom_version, __version__))

    def _write_instrument(self, valuelist=None):
        return

    def _write_offsets(self, valuelist=None):
        d = OrderedDict()
        for device, _key, value in valuelist:
            d[device] = value
        self._write_sof(d)

    def _write_limits(self, valuelist=None):
        d = OrderedDict()
        for device, key, value in valuelist:
            if key == 'userlimits':
                d[device] = value
        self._write_bls(d)

    def _write_tolerances(self, valuelist=None):
        d = OrderedDict()
        for device, _key, value in valuelist:
            d[device] = value
        self._write_tol(d)

    def _write_timeouts(self, valuelist=None):
        d = OrderedDict()
        for device, _key, _value in valuelist:
            d[device] = 1.0
        self._write_tmo(d)

    def _write_wavelength(self, valuelist=None):
        for device, key, value in valuelist:
            if device == 'wav' and key == 'value':
                self._write_float(value, 'WAV')

    def _write_general(self, valuelist=None):
        d = OrderedDict()
        ds = self.dataset
        d['STEP'] = ds.npoints
        d[ds.devices[0].name.upper()] = 0
        self._write_setv(d)
        d1 = OrderedDict()
        d1.clear()
        for device, key, value in valuelist:
            if key == 'value':
                if device == 'slits':
                    d1['SLITS_X'] = 0.
                    d1['SLITS_Y'] = 0.
                    d1['SLITS_W'] = value[0]
                    d1['SLITS_H'] = value[1]
                elif device == 'slitm':
                    d1['SLITM_U'] = value[0] / 2.
                    d1['SLITM_D'] = -value[0] / 2.
                    d1['SLITM_R'] = value[1] / 2.
                    d1['SLITM_L'] = -value[1] / 2.
                elif device == 'slite':
                    d1['SLITM_E'] = value
                elif device not in ['UBahn', 'wav', 'ysd']:
                    try:
                        d1[device] = value
                    except ValueError:
                        # print('%s.%s = %r' % (device, key, value))
                        d1[device.name] = 0.
        self._write_read(d1)
        d[ds.devices[0].name.upper()] = (float(ds.startpositions[0][0]),
                                         float(ds.startpositions[-1][0]))
        self._write_sgen(d)
        self._write_spec()
        self._write_string('DATE', time.strftime('%d-%b-%Y'))
        self._write_string('TIME', time.strftime('%H:%M:%S'))

    def _write_defdata(self, dev, master):
        devname = dev.name.upper()
        self._defdata('SETVALUES(%s)' % ' '.join(['STEP', devname]))
        if self._scan_type == 'SGEN2':
            mastervalues = 'SL1(TTHS ADET CHIS %s TIM1 MON)' % devname
        else:
            mastervalues = 'MM1(%s)SL1(TTHS ADET MON)' % master
        self._defdata('MASTER1VALUES(%s)' % mastervalues)

    def _write_status(self, valuelist=None):
        # print 'STATUS: %r' % valuelist
        return

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self.log.debug('detector %r' % detector)
        self.log.debug('init: %r' % dataset.settype)
        self._file = None
        self._fname = None
        self._template = sink.filenametemplate
        self._wrote_header = False
        self._scan_file = False

    def prepare(self):
        self.log.debug('prepare: %r' % self.dataset.settype)
        session.data.assignCounter(self.dataset)
        _file = None
        if self.dataset.settype == SCAN:
            _file = session.data.createDataFile(self.dataset,
                                                self._template[0])
            self._scan_file = True
#       elif not self._scan_file:
#           _file = session.data.createDataFile(self.dataset,
#                                               self._template[0])
        if _file:
            self._file = _file
        self.log.debug('%s %r %r' % (self.dataset.settype, self._scan_file,
                                     self._file.filepath))

    def begin(self):
        ds = self.dataset
        if ds.info.startswith('contscan'):
            self._scan_type = 'SGEN2'
        elif ds.info.startswith('scan'):
            self._scan_type = 'SGEN1'
        else:
            self._scan_type = 'SGEN1'
        if self._file:
            self._write_string('DAT', self._file.filepath)
            self._write_integer(self.dataset.counter, 'NUMOR')
            if self._scan_type == 'SGEN2':
                exptype = ['M2', 'A2', 'ADET', 'ALLMOTS', 'TRANS']
            else:
                exptype = ['M2', 'A2', 'ADET', 'ALLMOTS', 'MOT1', 'TRANS']
            self._write_exptype(exptype)
        self._detvalues = None

    def putMetainfo(self, metainfo):
        self.log.debug('put meta info: %r' % metainfo)
        for dev, key in metainfo:
            self.log.debug('put meta info: %s.%s = %r' %
                           (dev, key, metainfo[dev, key][0]))
        self._write_header(metainfo)
        return

    def _write_header(self, metainfo):
        if self._wrote_header:
            return
        bycategory = {}
        for (dev, key), (v, _, _, cat) in iteritems(metainfo):
            if dev == 'adet':
                pass
            if cat:
                bycategory.setdefault(cat, []).append((dev, key, v,))
        if 'experiment' in bycategory:
            self._write_user_proposal(bycategory['experiment'])
        if 'limits' in bycategory:
            self._write_limits(bycategory['limits'])
        if 'offsets' in bycategory:
            self._write_offsets(bycategory['offsets'])
        if 'precisions' in bycategory:
            self._write_tolerances(bycategory['precisions'])
        if 'general' in bycategory:
            self._write_wavelength(bycategory['general'])
            self._write_timeouts(bycategory['general'])

        d = OrderedDict()
        master = None
        if self._scan_type != 'SGEN2':
            if 'presets' in bycategory:
                for device, key, value in bycategory['presets']:
                    # self.log.info('%s.%s = %r' % (device, key, value))
                    if device == 'adet' and key == 'preset':
                        if self.dataset.metainfo[device, 'mode'][1] == 'time':
                            master = 'TIM1'
                        else:
                            master = 'MON'
                        d[master] = value
                        self._write_mm1(d)
                        break

        d.clear()
        d['TTHS'] = 0
        d['ADET'] = 0
        if self._scan_type == 'SGEN2':
            d['CHIS'] = 0
            for dev in self.dataset.devices:
                d[dev.name.upper()] = 0
            d['TIM1'] = 0
        d['MON'] = 0
        self._write_sl1(d)

        d.clear()
        d['TTHS'] = (256., 128., 0.85)
        d['NYS'] = (256., 128., 0.85)
        d['YSD'] = (0)
        self._write_rela(d)

        d.clear()
        d['W1'] = (1, 256, 1, 256)
        d['W2'] = (0, 0, 0, 0)
        d['W3'] = (0, 0, 0, 0)
        d['W4'] = (0, 0, 0, 0)
        self._write_winda(d)

        if 'sample' in bycategory:
            self._write_sample(bycategory['sample'])
        if 'experiment' in bycategory:
            self._write_title(bycategory['experiment'])
        self._write_version()
        if 'instrument' in bycategory:
            self._write_instrument(bycategory['instrument'])
        if 'status' in bycategory:
            self._write_status(bycategory['status'])
        if 'general' in bycategory:
            self._write_general(bycategory['general'])
        if 'experiment' in bycategory:
            self._write_comment(bycategory['experiment'])
        self._write_defdata(self.dataset.devices[0], master)
        self._flush()
        self._wrote_header = True

    def putValues(self, value):
        if self.dataset.settype == POINT:
            return
        self.log.info('put values (%s): %r' % (self.dataset.settype, value))

    def addSubset(self, point):
        self.log.debug('add subset: %s' % point.settype)
        if point.settype != POINT:
            return

        self.log.debug('%r - %r' % (self.dataset.detvalueinfo,
                                    point.detvaluelist))

        # the image data are hopefully always at this place
        try:
            self._detvalues = point.results.values()[0][1][0]
        except Exception:
            try:
                # try to read image date ourselves
                self._detvalues = session.getDevice('image').readArray(FINAL)
            except Exception:
                # create empty data set
                self.log.error('Could not get the image data!')
                self._detvalues = np.array([[1, ], ])
                self._detvalues.resize((256, 256))
        self.log.debug('storing results %r' % self._detvalues)

        self._write_header(point.metainfo)

        self._string('SETVALUES')
        self._write_integer(point.number)
        self._write_float(point.devvaluelist[0])
        self._string('MASTER1VALUES')
        for (info, val) in zip(self.dataset.detvalueinfo, point.detvaluelist):
            if info.type == 'time':
                if self._scan_type == 'SGEN1':
                    self._write_integer((100 * val) / 100)
                else:
                    tim1 = 100 * val
        tths = session.getDevice('tths').read()
        try:
            chis = session.getDevice('chis').read()
        except ConfigurationError:
            chis = 0
        for (dev, key), (v, _, _, _) in iteritems(self.dataset.metainfo):
            if key == 'value':
                if dev == 'tths':
                    tths = v
                elif dev == 'chis':
                    chis = v
        self._write_float(tths)
        for (info, val) in zip(self.dataset.detvalueinfo, point.detvaluelist):
            self.log.debug('%s: %r' % (info.type, val))
            if info.type == 'counter':
                addvalues = (tths, )
                buf = '%c' % 0x80
                if len(addvalues) > 0:
                    buf += '%c%c%c' % (0x80, FLOATTYPE, 0x81)
                    buf += '%s' % self._len(len(addvalues))
                buf += '%c%c%c' % (0x80, LONGINTEGER, 0x81)
                if self._detvalues is None:
                    self.log.error('No detector data!')
                else:
                    self.log.debug('%r' % self._detvalues.size)
                    buf += '%s%c' % (self._len(self._detvalues.size), 0x81)
                buf += '%s' % self._len(1)
                for v in addvalues:
                    buf += '%s' % struct.pack('f', v)
                if self._detvalues is not None:
                    for i in np.nditer(self._detvalues.T):
                        buf += '%s' % struct.pack('i', i)
                self._file_write(buf)
        if self._scan_type == 'SGEN2':
            self._write_float(chis)
            self._write_float(point.devvaluelist[0])
            self._write_integer(tim1)
        for (info, val) in zip(self.dataset.detvalueinfo, point.detvaluelist):
            if info.type == 'monitor':
                self._write_integer(val)
        self._detvalues = None

    def putResults(self, quality, results):
        self.log.info('put results (%r): %r' % (quality, results))
        if quality != FINAL and self.dataset.settype != POINT:
            return

    def end(self):
        self._write_string('DATE', time.strftime('%d-%b-%Y'))
        self._write_string('TIME', time.strftime('%H:%M:%S'))

        buf = '%c' % 0xc0
        t = self._file_tell() + 1
        t = 512 - (t % 512)
        buf += '%c' * t % ((0, ) * t)
        self._file_write(buf)
        self._flush()
        self._file = None
        self._wrote_header = False
        self._scan_file = False
        self._detvalues = None


class CaressScanfileSink(FileSink):
    """A data sink that writes the CARESS file format."""

    handlerclass = CaressScanfileSinkHandler

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
        # 'settypes': Override(default=[SCAN, SUBSCAN, POINT]),
        'filenametemplate': Override(default=['m2%(pointcounter)08d.dat',
                                              'm2%(scancounter)08d.dat']),
    }
