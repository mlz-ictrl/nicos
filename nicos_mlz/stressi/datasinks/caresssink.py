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
"""The STRESSI specific CARESS data writing module."""

import numbers
import time
from collections import OrderedDict, namedtuple
from struct import pack

import numpy as np

from nicos import get_custom_version, nicos_version, session
from nicos.core import Override, Param, dictof
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos.core.data import DataSinkHandler
from nicos.devices.datasinks import FileSink

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
    """CARESS compatible datafile writing class."""

    _scan_file = False
    _detvalues = None
    _buffer = b''
    _scan_type = 'SGEN1'

    def _file_tell(self):
        return self._file.tell() if self._file else 0

    def _file_write(self, buf):
        if self._file:
            self._file.write(buf)
        self._buffer += buf

    def _file_close(self):
        if self._file:
            self._file.close()
            self._file = None

    def _flush(self):
        # self._file.write(self._buffer)
        self._buffer = b''

    def _string(self, value):
        value = value.encode()
        buf = pack('B', CHARTYPE) + self._len(len(value)) + value.upper()
        self._file_write(buf)

    def _len(self, val):
        if val < 128:
            return pack('B', val)
        elif val < 65536:
            return pack('<Bh', 0x80 | INTEGERTYPE, val)
        else:
            return pack('<Bi', 0x80 | LONGINTEGER, val)

    def _defcmd(self, cmd):
        buf = 'DEFCMD %s' % cmd
        self._string(buf)

    def _defdata(self, value):
        buf = 'DEFDAT %s' % value
        self._string(buf)

    def _write_string(self, key, data):
        self._defcmd(key)
        self._string(key)
        data = data.encode()
        buf = pack('BBB', 0x80, CHARTYPE, 0x81) + self._len(len(data)) + data
        self._file_write(buf)

    def _write_integer(self, value, key=None):
        if value is None:
            self.log.error("write_integer: Found 'None' value for %s",
                           key if key else '')
            return
        if key:
            self._defcmd(key)
            self._string(key)
        buf = pack('<BBi', LONGINTEGER, 1, int(value))
        self._file_write(buf)

    def _write_short(self, value):
        buf = pack('<BBh', INTEGERTYPE, 1, int(value))
        self._file_write(buf)

    def _write_float(self, value, key=None):
        if value is None:
            self.log.error("write_float: Found 'None' value for %s",
                           key if key else '')
            return
        if key:
            self._defcmd(key)
            self._string(key)
        buf = pack('<BBf', FLOATTYPE, 1, float(value))
        self._file_write(buf)

    def _write_exptype(self, types):
        data = 'EXPTYPE'
        self._defcmd(data)
        self._string(data)
        buf = b'\x80'
        sbuf = b''
        for item in types:
            item = item.encode()
            buf += pack('BBBB', 0x80, CHARTYPE, 0x81, len(item))
            sbuf += item
        buf += b'\x81\x01'
        self._file_write(buf + sbuf)

    def _write_bls(self, d):
        data = 'BLS'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        buf = b''
        for i in d.values():
            buf += pack('<BBff', FLOATTYPE, 2, float(i[0]), float(i[1]))
        self._file_write(buf)

    def _remove_none_values(self, d):
        nonelist = []
        for k, v in d.items():
            if v is None:
                self.log.warning('Found %r value for %r', v, k)
                nonelist += [k]
        for i in nonelist:
            d.pop(i)
        return d

    def _write_float_group(self, group, d):
        data = group
        d = self._remove_none_values(d)
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        for v in d.values():
            self._write_float(v)

    def _write_sof(self, d):
        self._write_float_group('SOF', d)

    def _write_tol(self, d):
        self._write_float_group('TOL', d)

    def _write_tmo(self, d):
        self._write_float_group('TMO', d)

    def _write_read(self, d):
        data = 'READ'
        d = self._remove_none_values(d)
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        for k, v in d.items():
            if isinstance(v, numbers.Real):
                self._write_float(v)
            elif isinstance(v, str) and (v in self.sink.mapping):
                self.log.debug('%s = %r -> %r', k, v, self.sink.mapping[v])
                self._write_float(self.sink.mapping[v])
            else:  # some values are not convertable into a number: lists, ...
                self.log.debug('%s = %r', k, v)
                self._write_float(0)

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
        buf = b'\x00' * len(d)
        self._file_write(buf)

    def _write_rela(self, d):
        data = 'RELA'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        buf = b''
        for i in d.values():
            value = i
            if not isinstance(value, tuple):
                value = (value, )
            buf += pack('BB', FLOATTYPE, len(value))
            for j in value:
                buf += pack('<f', float(j))
        self._file_write(buf)

    def _write_winda(self, d):
        data = 'WINDA'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        buf = b''
        for i in d.values():
            value = i
            if not isinstance(value, tuple):
                value = (value, )
            while len(value) < 4:
                value += (0, )
            buf += pack('BB', INTEGERTYPE, len(value))
            for j in value:
                buf += pack('<h', j)
        self._file_write(buf)

    def _write_setv(self, d):
        data = 'SETV'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        self._write_short(d['STEP'])
        buf = b'\x00'  # no value for the scanning value
        self._file_write(buf)

    def _write_sgen(self, d):
        data = self._scan_type
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        self._write_short(d['STEP'])
        d.pop('STEP')
        for key in d.keys():
            buf = pack('BB', FLOATTYPE, 2)
            for v in d[key]:
                buf += pack('<f', float(v))
            self._file_write(buf)

    def _write_spec(self):
        data = 'SPEC'
        self._defcmd(data + '( %s)' % 'ADET')
        self._string(data)
        buf = b'\x00\x00'
        self._file_write(buf)

    def _write_setvalue(self, d):
        data = 'SETVALUE'
        self._defcmd(data + '(%s)' % ' '.join(d.keys()))
        self._string(data)
        self._write_short(d['STEP'])
        # buf = b'\x00'
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
                           (nicos_version, get_custom_version(), __version__))

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
        if ds.devvalueinfo:
            for dev in ds.devvalueinfo:
                d[dev.name.upper()] = 0
        else:
            d['TIM'] = 0
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
                elif device == 'slitp':
                    d1['SLITP_U'] = value[0] / 2.
                    d1['SLITP_D'] = -value[0] / 2.
                    d1['SLITP_R'] = value[1] / 2.
                    d1['SLITP_L'] = -value[1] / 2.
                elif device == 'slite':
                    d1['SLITM_E'] = value
                elif device == 'transm':
                    # XXX: should be fixable now?
                    # The position of the moveable is needed, which is normally
                    # lowlevel and therefore not added to the metadata
                    d1[device] = session.getDevice(device). \
                        _attached_moveable.read()
                    self.log.debug('TRANSM value %f', d1[device])
                elif device == 'wav':
                    d1[device] = value or 0.
                elif device not in ['UBahn', 'wav', 'ysd']:
                    try:
                        d1[device] = value
                    except ValueError:
                        # print('%s.%s = %r' % (device, key, value))
                        d1[device.name] = 0.
        self._write_read(d1)
        if ds.devvalueinfo:
            for i, dev in enumerate(ds.devvalueinfo):
                d[dev.name.upper()] = (float(ds.startpositions[0][i]),
                                       float(ds.startpositions[-1][i]))
        else:
            d['TIM'] = (0, 1000000)
        self._write_sgen(d)
        self._write_spec()
        self._write_string('DATE', time.strftime('%d-%b-%Y'))
        self._write_string('TIME', time.strftime('%H:%M:%S'))

    def _write_defdata(self, dev, master):
        if isinstance(dev, str):
            devnames = [dev.upper()]
        elif isinstance(dev, (list, tuple)):
            devnames = [d.name.upper() for d in dev]
        else:
            devnames = [dev.name.upper()]
        self._defdata('SETVALUES(%s)' % ' '.join(['STEP'] + devnames))
        if self._scan_type == 'SGEN2':
            mastervalues = 'SL1(TTHS ADET '
            if ('chis', 'value') in self.dataset.metainfo:
                self.log.debug('%r', self.dataset.metainfo[('chis', 'value')])
                if self.dataset.metainfo[('chis', 'value')][0] is not None:
                    mastervalues += 'CHIS '
            mastervalues += '%s TIM1 MON)' % ' '.join(devnames)
        else:
            mastervalues = 'MM1(%s)SL1(TTHS ADET MON' % master
            for d in self.dataset.detvalueinfo:
                if d.name not in ['adet', 'tim1', 'mon'] and \
                   not d.name.endswith('.sum'):
                    mastervalues += ' %s' % d.name.upper()
            for d in self.dataset.environment:
                if hasattr(d, 'name') and \
                   d.name != 'etime' and \
                   not d.name.endswith(':elapsedtime'):
                    mastervalues += ' %s' % d.name.upper()
            mastervalues += ')'
        self._defdata('MASTER1VALUES(%s)' % mastervalues)

    def _write_status(self, valuelist=None):
        # print 'STATUS: %r' % valuelist
        return

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self.log.debug('detector %r', detector)
        self.log.debug('init: %r', dataset.settype)
        self._file = None
        self._fname = None
        self._template = sink.filenametemplate
        self._scan_file = False

    def prepare(self):
        self.log.debug('prepare: %r', self.dataset.settype)
        self.manager.assignCounter(self.dataset)
        _file = None
        if self.dataset.settype == SCAN:
            _file = self.manager.createDataFile(self.dataset,
                                                self._template[0])
            self._scan_file = True
#       elif not self._scan_file:
#           _file = self.manager.createDataFile(self.dataset,
#                                               self._template[0])
        if _file:
            self._file = _file
        self.log.debug('%s %r %r', self.dataset.settype, self._scan_file,
                       self._file.filepath)

    def begin(self):
        ds = self.dataset
        self.log.debug('begin: %r', ds.settype)
        scaninfo = ds.info.split('-')[-1].strip()
        if scaninfo.startswith('contscan'):
            self._scan_type = 'SGEN2'
        elif scaninfo.startswith('scan'):
            self._scan_type = 'SGEN1'
        else:
            self._scan_type = 'SGEN1'
        self._write_string('DAT', self._file.filepath if self._file else '')
        self._write_integer(self.dataset.counter, 'NUMOR')
        if self._scan_type == 'SGEN2':
            exptype = ['M2', 'A2', 'ADET', 'ALLMOTS', 'TRANS']
        else:
            exptype = ['M2', 'A2', 'ADET', 'ALLMOTS', 'MOT1', 'TRANS']
        self._write_exptype(exptype)
        self._detvalues = None

    def putMetainfo(self, metainfo):
        self.log.debug('putMetainfo: %r', metainfo)
        for dev, key in metainfo:
            self.log.debug('putMetainfo: %s.%s = %r',
                           dev, key, metainfo[dev, key][0])

    def _write_header(self, point):
        self.log.debug('_write_header: %r', point.settype)
        bycategory = {}
        for (dev, key), info in point.metainfo.items():
            if dev == 'adet':
                pass
            if info.category:
                bycategory.setdefault(info.category, []).append(
                    (dev, key, info.value,))
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
                    # self.log.info('%s.%s = %r', device, key, value)
                    if device == 'adet' and key == 'preset':
                        if point.metainfo[device, 'mode'][1] == 'time':
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
            for dev in point.devices:
                d[dev.name.upper()] = 0
            d['TIM1'] = 0
        d['MON'] = 0
        if self._scan_type != 'SGEN2':
            # Add environment devices to the SL1 (slaves)
            for dev in point.environment:
                if hasattr(dev, 'name') and \
                   dev.name != 'etime' and \
                   not dev.name.endswith(':elapsedtime'):
                    d[dev.name.upper()] = 0
        self._write_sl1(d)

        d.clear()
        # Get pixel size
        xpix, ypix = point.metainfo.get(
            ('image', 'pixel_size'), ((0.85, 0.85), ))[0]
        d['TTHS'] = (256., 128., xpix)
        d['NYS'] = (256., 128., ypix)
        d['YSD'] = (point.metainfo.get(('ysd', 'value'), [0])[0],)
        if self._detvalues is not None:
            if len(self._detvalues.shape) == 2:
                d['NYS'] = (float(self._detvalues.shape[0]),
                            self._detvalues.shape[0] / 2, xpix)
                d['TTHS'] = (float(self._detvalues.shape[1]),
                             self._detvalues.shape[1] / 2, ypix)
            elif len(self._detvalues.shape) == 1:
                d['TTHS'] = (float(self._detvalues.shape[0]),
                             self._detvalues.shape[0] / 2, xpix)
                d['NYS'] = (1., 1 / 2, ypix)
        self._write_rela(d)

        d.clear()
        d['W1'] = (1, 256, 1, 256)
        d['W2'] = (0, 0, 0, 0)
        d['W3'] = (0, 0, 0, 0)
        d['W4'] = (0, 0, 0, 0)
        if self._detvalues is not None:
            if len(self._detvalues.shape) == 2:
                d['W1'] = (
                    1, self._detvalues.shape[0], 1, self._detvalues.shape[1])
            elif len(self._detvalues.shape) == 1:
                d['W1'] = (1, 1, 1, self._detvalues.shape[0])
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
        if point.devvalueinfo:
            self._write_defdata(point.devvalueinfo, master)
        else:
            self._write_defdata('TIM', master)
        self._flush()

    def addSubset(self, subset):
        self.log.debug('add subset: %s, #%d', subset.settype, subset.number)
        if subset.settype != POINT:
            return

        point = subset

        self.log.debug('%r - %r', point.detvalueinfo, point.detvaluelist)

        # the image data are hopefully always at this place
        try:
            if not self.sink.detectors:
                det = session.experiment.detectors[0].name
            else:
                det = self.sink.detectors[0]
            self._detvalues = point.results[det][1][0]
        except (IndexError, KeyError):
            # create empty data set
            self.log.error('Could not get the image data from %s', det)
            self._detvalues = np.zeros((256, 256))

        if point.number == 1:
            self._write_header(point)

        self.log.debug('storing results %r', self._detvalues)

        self._string('SETVALUES')
        self._write_integer(point.number)
        if point.devvaluelist:
            for v in point.devvaluelist:
                self._write_float(v)
        else:
            self._write_float(0.)
        self._string('MASTER1VALUES')
        for (info, val) in zip(point.detvalueinfo, point.detvaluelist):
            if info.type == 'time':
                if self._scan_type == 'SGEN1':
                    self._write_integer(val)
                else:
                    tim1 = 100 * val
        tths = point.metainfo.get(('tths', 'value'), [0])[0]
        self._write_float(tths)
        for (info, val) in zip(point.detvalueinfo, point.detvaluelist):
            self.log.debug('%s (%s): %r', info.name, info.type, val)
            if info.type == 'counter' and info.name.endswith('.sum'):
                addvalues = (tths, )
                buf = b'\x80'
                if addvalues:
                    buf += pack('BBB', 0x80, FLOATTYPE, 0x81)
                    buf += self._len(len(addvalues))
                buf += pack('BBB', 0x80, LONGINTEGER, 0x81)
                if self._detvalues is None:
                    self.log.error('No detector data!')
                else:
                    self.log.debug('%r', self._detvalues.size)
                    buf += self._len(self._detvalues.size) + b'\x81'
                buf += self._len(1)
                for v in addvalues:
                    buf += pack('<f', v)
                if self._detvalues is not None:
                    if self.sink.flipimage:
                        for i in np.nditer(np.flipud(self._detvalues.T)):
                            buf += pack('<i', i)
                    else:
                        for i in np.nditer(self._detvalues.T):
                            buf += pack('<i', i)
                self._file_write(buf)
        if self._scan_type == 'SGEN2':
            chis = point.metainfo.get(('chis', 'value'), [None])[0]
            if chis is None:
                self.log.debug('CHIS value is None, ignore it')
            else:
                self._write_float(chis)
            if point.canonical_values:
                self._write_float(point.devvaluelist[0])
            else:
                self._write_float(0.0)
            self._write_integer(tim1)
        for (info, val) in zip(point.detvalueinfo, point.detvaluelist):
            if info.type == 'monitor':
                self._write_integer(val)
            elif info.type == 'counter' and not info.name.endswith('.sum'):
                self._write_integer(val)
        if self._scan_type != 'SGEN2':
            for (info, val) in zip(point.envvalueinfo, point.envvaluelist):
                if (hasattr(info, 'name') and info.name != 'etime' and not
                        info.name.endswith(':elapsedtime')):
                    if isinstance(val, numbers.Real):
                        self._write_float(val)
                    else:
                        self.log.info("Ignoring environment device '%s' "
                                      "returning non-number value", info.name)
        self._detvalues = None

    def end(self):
        self._write_string('DATE', time.strftime('%d-%b-%Y'))
        self._write_string('TIME', time.strftime('%H:%M:%S'))

        buf = b'\xc0'
        t = self._file_tell() + 1
        t = 512 - (t % 512)
        buf += b'\x00' * t
        self._file_write(buf)
        self._flush()
        self._file_close()
        self._scan_file = False
        self._detvalues = None


class CaressScanfileSink(FileSink):
    """A data sink that writes the CARESS file format."""

    handlerclass = CaressScanfileSinkHandler

    parameters = {
        # Since some devices return strings as read values, but the CARESS
        # format does not accept strings they must be mapped to numbers
        'mapping': Param('Mapping of (string) device values to float values',
                         unit='', settable=False,
                         type=dictof(str, float),
                         default={'on': 1,
                                  'off': 0,
                                  'open': 1,
                                  'closed': 0}),
        'flipimage': Param('Flipping image bottom-top before writing',
                           type=bool, default=False, settable=False,
                           userparam=False),
    }

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
        # 'settypes': Override(default=[SCAN, SUBSCAN, POINT]),
        'filenametemplate': Override(default=['m2%(pointcounter)08d.dat',
                                              'm2%(scancounter)08d.dat']),
    }
