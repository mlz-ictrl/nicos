# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

import time
from datetime import datetime
from os import path

import numpy as np

from nicos import session
from nicos.core import Override, Param, PointDataset, ScanDataset, Value, \
    listof, nicosdev
from nicos.core.constants import POINT, SCAN
from nicos.core.data import DataSinkHandler, ScanData
from nicos.core.errors import InvalidValueError
from nicos.devices.datasinks import FileSink
from nicos.devices.datasinks.image import ReaderMeta
from nicos.devices.tas import TASSample


class ILLAsciiHandler(DataSinkHandler):
    """
    This saves the data while the scan is running in an
    internal data structure and then proceeds to write the
    file in end()
    """
    scanvalues = {}
    _header = None

    def _getMLZCryst(self):
        result = {}
        scat = self._findValue(session.instrument.name, 'scatteringsense')
        result['ss'] = scat[1]
        mode = self._findValue(session.instrument.name, 'scanmode')
        if mode == 'CKI':
            result['FX'] = 2
        else:
            result['FX'] = 1
        result['KFIX'] = self._findValue(session.instrument.name,
                                         'scanconstant')
        sample = session.getDevice('Sample')
        result['V1'] = getattr(sample, 'orient1')
        result['V2'] = getattr(sample, 'orient2')
        result['CELL'] = getattr(sample, 'lattice') + \
            getattr(sample, 'angles')
        return result

    def _getUBCryst(self):
        result = {}
        refs = self._findValue(session.instrument.name,
                               'orienting_reflections')
        # It can happen that the orienting reflections are ill defined
        if len(refs) == 2:
            rlist = session.getDevice('ublist')
            try:
                rfl = rlist.get_reflection(refs[0])
                result['V1'] = list(rfl[0])
            except InvalidValueError:
                result['V1'] = [0, 0, 0]
            try:
                rfl = rlist.get_reflection(refs[1])
                result['V2'] = list(rfl[0])
            except InvalidValueError:
                result['V2'] = [0, 0, 0]
        else:
            result['V1'] = [0, 0, 0]
            result['V2'] = [0, 0, 0]
        mode = self._findValue(session.instrument.name, 'emode')
        if mode == 'FKI':
            result['FX'] = 2
            result['KFIX'] = self._findValue('mono', 'value')
        else:
            result['FX'] = 1
            result['KFIX'] = self._findValue('ana', 'value')
        result['ss'] = self._findValue(session.instrument.name,
                                       'scattering_sense')
        result['CELL'] = [self._findValue('Sample', p) for p in
                          ['a', 'b', 'c', 'alpha', 'beta', 'gamma']]
        result['UB'] = self._findValue('Sample', 'ubmatrix')
        result['PN'] = self._findValue(session.instrument.name,
                                       'plane_normal')
        return result

    def _getCrystData(self):
        # TAS in NICOS can use the traditional and the UB matrix TAS
        # calculus. Thus the place where crystallographic information is
        # stored is different. This routine gets the stuff and returns
        # it in a dictionary.
        if isinstance(session.experiment.sample, TASSample):
            return self._getMLZCryst()
        else:
            return self._getUBCryst()

    def _prepareDictionaries(self):
        for dev in self.dataset.devices:
            self.scanvalues[dev.name] = []

        for dev in self.dataset.environment:
            self.scanvalues[dev.name] = []

        for det in self.sink.scaninfo:
            self.scanvalues[det] = []

    def _appendVariaAndZeros(self):
        self._header += 'VARIA:'
        count = 0
        for name in self.sink.varia:
            val = self._findValue(name, 'value')
            if val != 'UNKNOWN' and val is not None:
                self._header += ' %-8s=%8.4f,' % (name.upper(), float(val))
                count += 1
                if count == 3:
                    count = 0
                    self._header += '\nVARIA:'
        if not self._header.endswith('\n'):
            self._header += '\n'

        self._header += 'ZEROS:'
        count = 0
        for name in self.sink.varia:
            val = self._findValue(name, 'offset')
            if val != 'UNKNOWN' and val is not None:
                self._header += ' %-8s=%8.4f,' % (name.upper(), float(val))
                count += 1
                if count == 3:
                    count = 0
                    self._header += '\nZEROS:'
        if not self._header.endswith('\n'):
            self._header += '\n'

    def _initHeader(self):
        self._header = 'R'*80 + '\n'
        counters = self.manager.getCounters()
        self._header += '%8d%8d%8d\n' % (counters['scancounter'], 1, 0)
        self._header += 'ILL TAS data in the new ASCII format follow after ' \
                        'the line VV...V\n'
        self._header += 'A'*80 + '\n'
        self._header += '%8d%8d\n' % (42, 0)
        time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(time.time()))
        self._header += '%-10s%-12s%-s\n' % (session.instrument.name,
                                             self._findValue('Exp', 'users'),
                                             time_str)
        self._header += 'V'*80 + '\n'

        self._header += 'INSTR: %s\n' % session.instrument.name
        self._header += 'EXPNO: %s\n' % self._findValue('Exp', 'proposal')
        self._header += 'USER_: %s\n' % self._findValue('Exp', 'users')
        self._header += 'LOCAL: %s\n' % self._findValue('Exp', 'localcontact')
        self._header += 'FILE_: %s\n' % str(counters['scancounter'])
        self._header += 'DATE_: %s\n' % time_str
        self._header += 'TITLE: %s\n' % self._findValue('Exp', 'title')
        self._header += 'COMND: %s\n' % session._currentscan._scaninfo
        qe = session.instrument.read(0)
        self._header += 'POSQE: QH=%8.4f, QK=%8.4f, QL=%8.4f, EN=%8.4f, ' \
                        'UN=MEV\n' % tuple(qe)
        self._header += 'STEPS: '
        devidx = 0
        positions = self.dataset.startpositions
        for dev in self.dataset.devices:
            if len(positions) > 1:
                pnext = positions[1][devidx]
                start = positions[0][devidx]
                if isinstance(start, tuple):
                    # This happens in qscans
                    names = ['QH', 'QK', 'QL', 'EN']
                    for name, s, n in zip(names, start, pnext):
                        self._header += 'D%s= %8.4f, ' % (name, n - s)
                    devidx += 1
                    continue
                step = pnext - start
            else:
                step = .0
            self._header += 'D%s= %8.4f, ' % (dev.name.upper(), step)
            devidx += 1
        self._header += '\n'
        cryst = self._getCrystData()
        self._header += 'PARAM: DM=%8.4f, DA=%8.4f, SM=%2d, SS=%2d, SA=%2d\n' \
                        % (float(self._findValue('mono', 'dvalue')),
                           float(self._findValue('ana', 'dvalue')),
                           int(self._findValue('mono', 'scatteringsense')),
                           int(cryst['ss']),
                           int(self._findValue('ana', 'scatteringsense')))
        self._header += 'PARAM: FX=%3d, KFIX=%8.4f\n' % (int(cryst['FX']),
                                                         float(cryst['KFIX']))
        cell = cryst['CELL']
        self._header += 'PARAM: AS=%8.4f, BS=%8.4f, CS=%8.4f\n' % \
                        (cell[0], cell[1], cell[2])
        self._header += 'PARAM: AA=%8.4f, BB=%8.4f, CC=%8.4f\n' % \
                        (cell[3], cell[4], cell[5])
        vec = cryst['V1']
        self._header += 'PARAM: AX=%8.4f, AY=%8.4f, AZ=%8.4f\n' % \
                        (vec[0], vec[1], vec[2])
        vec = cryst['V2']
        self._header += 'PARAM: BX=%8.4f, BY=%8.4f, BZ=%8.4f\n' % \
                        (vec[0], vec[1], vec[2])
        if 'UB' in cryst:
            ub = cryst['UB']
            self._header += 'PARAM: UB11=%8.4f, UB12=%8.4f, UB13=%8.4f\n' \
                            % (ub[0], ub[1], ub[2])
            self._header += 'PARAM: UB21=%8.4f, UB22=%8.4f, UB23=%8.4f\n' \
                            % (ub[3], ub[4], ub[4])
            self._header += 'PARAM: UB31=%8.4f, UB32=%8.4f, UB33=%8.4f\n' \
                            % (ub[0], ub[1], ub[2])
            pn = cryst['PN']
            self._header += 'PARAM: PN1=%8.4f, PN2=%8.4f, PN3=%8.4f\n' % \
                            (pn[0], pn[1], pn[2])

        self._appendVariaAndZeros()

        if 't' in self.dataset.preset:
            self._header += 'PARAM: TI=%8.4f\n' % self.dataset.preset['t']
        else:
            self._header += 'PARAM: MN=%8d\n' % self.dataset.preset['m']

        self._prepareDictionaries()

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        self.manager.getFilenames(self.dataset, self.sink.filenametemplate,
                                  self.sink.subdir)

    def _findValue(self, dev, par):
        return self.dataset.metainfo.get((dev, par), ['UNKNOWN', 'UNKNOWN'])[0]

    def addSubset(self, subset):
        if subset.settype != POINT:
            return

        if subset.number == 1:
            self._initHeader()

        for i in range(len(self.dataset.devices)):
            dev = self.dataset.devices[i]
            if dev == session.instrument:
                self.scanvalues[dev.name].append(tuple(subset.devvaluelist))
            else:
                self.scanvalues[dev.name].append(subset.devvaluelist[i])

        for dev, value in zip(self.dataset.environment,
                              subset.envvaluelist):
            self.scanvalues[dev.name].append(value)

        for det in self.sink.scaninfo:
            if det in subset.values:
                self.scanvalues[det].append(subset.values[det])
            else:
                # contscan: try finding the value in results
                for idx, v in enumerate(subset.detvalueinfo):
                    if v.name == det:
                        self.scanvalues[det].append(
                            subset.results[subset.detectors[0].name][0][idx])
                        break
                else:
                    # arcane python: this is executed when the
                    # break in the loop above did not occur
                    session.log.warning('Detector %s not found when'
                                        'saving scan data', det)

    def end(self):
        with open(self.dataset.filepaths[0], 'w', encoding='utf-8') as out:
            out.write(self._header)

            # Build format line and header
            fmt = '(I4,1X,'
            header = ' PNT'
            for dev in self.dataset.devices:
                if dev == session.instrument:
                    fmt += 'F9.41X,F9.41X,F9.41X,F9.4IX'
                    header += '         H         K         L        EN'
                else:
                    fmt += 'F9.4,1X'
                    header += ' %9s' % dev.name.upper()
            fmt += 'F8.0,1X,F8.0,1X,F9.2,1X,F8.0,1X,F8.0,1X,'
            header += '      M1       M2       TIME     CNTS       M3'
            for dev in self.dataset.environment:
                fmt += 'F9.4,1X'
                header += ' %9s' % dev.name.upper()
            fmt += ')'
            out.write('FORMT: %s\nDATA_:\n%s\n' % (fmt, header))

            # Fix for cases where dataset.npoints is wrong: either
            # points were skipped or it is manualscan
            name = self.sink.scaninfo[0]
            np = len(self.scanvalues[name])
            for i in range(np):
                line = '%4d ' % (i + 1)
                for dev in self.dataset.devices:
                    # For compatibility with old files we want the
                    # %9.4f format wherever possible. The dev.format()
                    # is a fallback
                    if dev == session.instrument:
                        line += '%9.4f %9.4f %9.4f %9.4f ' % self.scanvalues[
                            dev.name][i]
                    else:
                        try:
                            line += '%9.4f ' % self.scanvalues[dev.name][i]
                        except TypeError:
                            line += dev.format(self.scanvalues[dev.name][i])

                # There is a tight correlation between this and sink.scaninfo!
                name = self.sink.scaninfo[0]
                m1 = self.scanvalues[name][i]
                name = self.sink.scaninfo[1]
                m2 = self.scanvalues[name][i]
                name = self.sink.scaninfo[2]
                cts = self.scanvalues[name][i]
                name = self.sink.scaninfo[3]
                time = self.scanvalues[name][i]
                name = self.sink.scaninfo[4]
                m3 = self.scanvalues[name][i]
                line += '%8ld %8ld %9.2f %8ld %8ld ' % (m1, m2, time, cts, m3)

                for dev in self.dataset.environment:
                    # See above regarding formatting
                    try:
                        line += '%9.4f ' % self.scanvalues[dev.name][i]
                    except TypeError:
                        line += dev.format(self.scanvalues[dev.name][i])
                out.write(line + '\n')


class ILLAsciiSink(FileSink):
    """
    This writes ASCII files in the ancient ILL format so beloved by the
    TAS'lers.
    """
    parameters = {
        'scaninfo': Param('NICOS devices for M1, M2, CNTS, TIME and M3 in '
                          'that order',
                          type=listof(nicosdev),
                          mandatory=True),
        'varia': Param('List of variables to write', type=listof(str),
                       mandatory=True),
    }

    parameter_overrides = {
        'settypes': Override(default=[SCAN]),
    }

    handlerclass = ILLAsciiHandler


def _drop_pre_header(f):
    while True:
        line = f.readline()
        if not line.strip() or line.startswith('VVV'):
            return


def _parse_header(f, dataset):

    def _make_time(created, ds):
        TIMEFMT = '%Y-%m-%d %H:%M:%S'
        TIMEFMT_OLD = '%d-%b-%Y %H:%M:%S'
        try:
            started = datetime.strptime(created, TIMEFMT)
        except ValueError:
            started = datetime.strptime(created, TIMEFMT_OLD)

        ds.started = time.mktime(started.timetuple())

    def _make_info(text, ds):
        ds.info = text.strip().rstrip()

    def _make_number(number, ds):
        ds.counter = int(number.strip().rstrip())

    def _make_devices(text, _):
        lines = text.replace('=', ',')
        return set([ll.strip() for ll in lines.split(',') if ll][0:-1:2])

    header_processors = {
        'DATE_': _make_time,
        'FILE_': _make_number,
        'VARIA': _make_devices,
        'COMND': _make_info,
    }

    devices = set()
    while True:
        line = f.readline()
        if not line.strip() or line.startswith('DATA_'):
            return devices
        splitline = [ll.strip() for ll in line.split(':')]

        key, text = splitline[0], ':'.join(splitline[1:])
        if key in header_processors:
            header_processors[key](text, dataset)


def _parse_data(f, dataset):

    detectors = ['M1', 'M2', 'TIME', 'CNTS', 'M3', 'M4']

    class DevFake:
        def __init__(self, name):
            self.name = name

    def get_dets_devs(names):
        devs = [DevFake(name) for name in names if name not in detectors]
        dets = [DevFake(name) for name in names if name in detectors]
        return devs, dets

    header = [h.strip().rstrip() for h in f.readline().split()]
    _raw = np.loadtxt(f)

    devs, dets = get_dets_devs(header)
    dataset.devvalueinfo = [Value(d.name, unit='') for d in devs]
    dataset.detvalueinfo = [Value(d.name, unit='') for d in dets]
    dataset.envvalueinfo = []

    def make_datapoint(row):
        pds = PointDataset(devices=devs, detectors=dets)
        for name, value in zip(header, row):
            pds._addvalues({name: (None, value)})
            pds.results.update({name: [value]})
            pds.finished = True
        return pds

    for row in _raw:
        dataset.subsets.append(make_datapoint(row))


def readFile(filename, dataset):
    with open(filename, 'r', encoding="utf8") as f:
        _drop_pre_header(f)
        _parse_header(f, dataset)
        _parse_data(f, dataset)


class ILLAsciiScanfileReader(metaclass=ReaderMeta):
    filetypes = [('illscan', 'SINQ TAS files (*.dat *.scn)')]

    def __init__(self, filename):
        self.scandataset = ScanDataset()
        self.metainfo = {}
        self.scandataset.filenames = [filename.split('/')[:-1]]
        self.scandataset.filepaths = [path.basename(filename)]
        readFile(filename, self.scandataset)

    @property
    def scandata(self):
        return ScanData(self.scandataset)
