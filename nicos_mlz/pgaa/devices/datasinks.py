#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************

"""PGAA specific data sink(s)."""

from __future__ import absolute_import, division, print_function

import csv
from array import array
from datetime import datetime
from os import path

from nicos import session
from nicos.core import Override, Param
from nicos.core.constants import FINAL, POINT
from nicos.core.data.sink import DataSinkHandler
from nicos.core.errors import NicosError
from nicos.devices.datasinks import FileSink
from nicos.pycompat import File

__all__ = ('MCASink', 'CHNSink', 'CSVDataSink')


class PGAASinkHandler(DataSinkHandler):
    """Base data sink handler for the PGAA files."""

    atts = {
        100.: ('out', 'out', 'out'),
        47.: ('out', 'in', 'out'),
        16.: ('in', 'out', 'out'),
        7.5: ('in', 'in', 'out'),
        5.9: ('out', 'out', 'in'),
        3.5: ('out', 'in', 'in'),
        2.7: ('in', 'out', 'in'),
        1.6: ('in', 'in', 'in'),
    }

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._counters = {}
        self._template = sink.filenametemplate

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        # save the counters since the counters are lost in 'end' but needed for
        # filename creation
        self._counters = self.manager.getCounters()

    def _createFile(self, ext, **kwargs):
        templates = [t + '%s%s' % (path.extsep, ext) for t in self._template]
        _file = self.manager.createDataFile(
            self.dataset, templates, self.sink.subdir,
            additionalinfo=kwargs)
        return _file

    def putResults(self, quality, results):
        if quality == FINAL:
            self.log.debug('results: %r', results)
            if self.detector.name in results:
                self.results = results[self.detector.name]

    def _value(self, dev):
        return self.dataset.metainfo[dev, 'value'][0]

    def end(self):
        if not self.sink.isActive(self.dataset):
            return

        self.log.debug('device value list: %r', self.dataset.devvaluelist)
        self.log.debug('%r', self.dataset.envvaluelist)
        self.log.debug('%r', self.dataset.detvaluelist)
        self.log.debug('%r', self.dataset.detvalueinfo)
        self.log.debug('type: %r', self.dataset.settype)

        try:
            spectrum = self.results[1][0].tolist()
            for i, vi in enumerate(self.detector.valueInfo()):
                if vi.name == 'truetim':
                    truetime = self.results[0][i]
                elif vi.name == 'livetim':
                    livetime = self.results[0][i]
            ecalintercept = float(self.detector.ecalintercept)
            ecalslope = float(self.detector.ecalslope)
        except NicosError:
            self.log.warning('error saving spectrum data ')
            return

        addinfo = self._counters.copy()
        addinfo.update(self.dataset.preset)
        code = ''
        for i, item in enumerate(self.atts[self._value('att')]):
            code += '%d' % (i + 1) if item == 'in' else ''
        addinfo['Attenuator'] = code
        addinfo['ElCol'] = self._value('ellcol')[:1]
        addinfo['Beam'] = 'O' if self.dataset.metainfo[
            self.detector.name, 'enablevalues'][0][0] == 'closed' else ''
        addinfo['Vacuum'] = 'V' if self._value('chamber_pressure') < 10. else ''
        addinfo['Prefix'] = self.detector.prefix
        addinfo['Pos'] = self.dataset.metainfo.get(('sc', 'value'), [0])[0]
        addinfo['Name'] = self.dataset.metainfo['Sample', 'samplename'][0]
        if 'Comment' not in addinfo:
            addinfo['Comment'] = self.dataset.preset.get('info', '')

        self._write_file(addinfo, livetime, truetime, spectrum, ecalslope,
                         ecalintercept)

    def _write_file(self, addinfo, livetime, truetime, spectrum, ecalslope,
                    ecalintercept):
        raise NotImplementedError('Implement "_write_file" in subclasses.')


class MCASinkHandler(PGAASinkHandler):
    """Data sink handler for the Ortec MCA files."""

    def _write_file(self, addinfo, livetime, truetime, spectrum, ecalslope,
                    ecalintercept):
        tb_time = array('i', [int(self.dataset.started)])
        tb_fill = array('h', [0, 0, 0])
        timeb = [tb_time, tb_fill]

        # Type elap:
        el_time = array('i', [int(livetime * 100), int(truetime * 100)])
        el_fill_1 = array('i', [0])
        el_fill_2 = array('d', [0])
        elap = [el_time, el_fill_1, el_fill_2]

        # Type xcal:
        ec_fill_1 = array('f', [0, ecalslope, ecalintercept])
        # !! exchange sinkinfo with preset when scan command is used
        unit = array('c', '{:<5}'.format(''))
        ec_fill_2 = array('c', '\t\t\t')
        xcal = [ec_fill_1, unit, ec_fill_2]

        # Type mcahead:
        mc_fill = array('h', [0, 1, 0])
        mc_fill2 = array('i', [0])

        spectr_name = array('c', '{:<26}'.format(addinfo.get('Name', '')[:26]))
        mc_fill3 = array('h', [0])
        filler = array('h', [0 for _i in range(19)])
        nchans = array('h', [16384])
        filedata = [mc_fill, mc_fill2, spectr_name, mc_fill3]
        filedata.extend(timeb)
        filedata.extend(elap)
        filedata.extend(xcal)
        filedata.extend([filler, nchans])

        if spectrum:
            filedata.append(array('i', spectrum))

        try:
            with self._createFile('mca', **addinfo) as f:
                self.log.debug('write mca file: %s', f.name)
                for data in filedata:
                    data.tofile(f)
        except IOError:
            pass


class CHNSinkHandler(PGAASinkHandler):
    """Data sink handler for the channel data files."""

    def _write_file(self, addinfo, livetime, truetime, spectrum, ecalslope,
                    ecalintercept):
        # header
        mustbe = array('h', [-1])
        detnumber = array('h', [1 if addinfo['Prefix'] == 'P' else 3])
        segmentnumber = array('h', [0])
        seconds = array('c', '{:2}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%S')))
        self.log.debug('started: {:2}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%S')))
        truetime = array('i', [int(truetime * 50)])
        livetime = array('i', [int(livetime * 50)])
        startdate = array('c', '{:8}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%d%b%y1')))
        self.log.debug('started: {:8}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%d%b%y1')))
        starttime = array('c', '{:4}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%H%M')))
        channeloffset = array('h', [0])
        numchannels = array('h', [16384])
        filedata = [mustbe, detnumber, segmentnumber, seconds, truetime,
                    livetime, startdate, starttime, channeloffset,
                    numchannels]

        if spectrum:
            filedata.append(array('i', spectrum))

        # suffix
        mustbes = array('h', [-102])
        res1 = array('h', [0])
        ecalzero = array('f', [ecalintercept])
        ecalslope = array('f', [ecalslope])
        ecalquadr = array('f', [0.0])
        peakshapecalzero = array('f', [1.0])
        peakshapecalslope = array('f', [0.0])
        peakshapecalquadr = array('f', [0.0])
        reserved = array('c', '{:228}'.format(''))
        detdesclen = array('c', '{:1}'.format('1'))
        detdesc = array('c', '{:63}'.format('d'))
        sampledesclen = array('c', '{:1}'.format('1'))
        sampledesc = array('c', '{:63}'.format('s'))
        res2 = array('c', '{:128}'.format(''))

        filedata += [mustbes, res1, ecalzero, ecalslope, ecalquadr,
                     peakshapecalzero, peakshapecalslope, peakshapecalquadr,
                     reserved, detdesclen, detdesc, sampledesclen, sampledesc,
                     res2]

        try:
            with self._createFile('chn', **addinfo) as f:
                self.log.debug('write chn file: %s', f.name)
                for data in filedata:
                    data.tofile(f)
        except IOError:
            pass


class PGAASink(FileSink):
    """Write spectrum to file in specific format."""

    parameter_overrides = {
        'settypes': Override(default=[POINT]),
        'filenametemplate': Override(
            default=['%(Prefix)s%(pointcounter)05d_%(Pos)02d-%(Name)s_'
                     '%(Comment)s__%(Attenuator)s%(ElCol)s%(Beam)s%(Vacuum)s'
                     '%(Filename)s']),
    }

    handlerclass = PGAASinkHandler


class MCASink(PGAASink):
    """Write spectrum to file in Ortec format."""

    handlerclass = MCASinkHandler


class CHNSink(PGAASink):
    """Write spectrum to file in channel format."""

    handlerclass = CHNSinkHandler


class CSVDataFile(File):
    """Represents a csv data file."""

    def __init__(self, shortpath, filepath):
        self.shortpath = shortpath
        self.filepath = filepath
        File.__init__(self, filepath, 'a')


class CSVSinkHandler(DataSinkHandler):

    atts = {
        100.: ('out', 'out', 'out'),
        47.: ('out', 'in', 'out'),
        16.: ('in', 'out', 'out'),
        7.5: ('in', 'in', 'out'),
        5.9: ('out', 'out', 'in'),
        3.5: ('out', 'in', 'in'),
        2.7: ('in', 'out', 'in'),
        1.6: ('in', 'in', 'in'),
    }

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._counters = {}
        self._template = sink.filenametemplate

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        # save the counters since the counters are lost in 'end' but needed for
        # filename creation
        self._counters = self.manager.getCounters()

    def _value(self, dev):
        return self.dataset.metainfo[dev, 'value'][0]

    def end(self):
        if self.sink.wasUsed(self.dataset):
            return

        self.sink._setROParam('filecount', self._counters.get('pointcounter',
                                                              0))
        addinfo = self._counters.copy()
        addinfo.update(self.dataset.preset)
        addinfo['Attenuator'] = self._value('att')
        addinfo['ElCol'] = self._value('ellcol')
        addinfo['Beam'] = self.dataset.metainfo[self.detector.name,
                                                'enablevalues'][0][0]

        for cond in ['LiveTime', 'TrueTime', 'ClockTime', 'counts']:
            if cond in self.dataset.preset:
                addinfo['cond'] = cond
                addinfo['value'] = self.dataset.preset[cond]

        addinfo['Detectors'] = '[%s]' % ','.join(
            [d.name for d in self.dataset.detectors])
        addinfo['Pressure'] = '%.3f' % self._value('chamber_pressure')
        addinfo['started'] = datetime.fromtimestamp(
            self.dataset.started).strftime('%Y-%m-%d %H:%M:%S')
        addinfo['stopped'] = datetime.fromtimestamp(
            self.dataset.finished).strftime('%Y-%m-%d %H:%M:%S')
        addinfo['Pos'] = self.dataset.metainfo.get(('sc', 'value'), [0])[0]
        addinfo['Name'] = self.dataset.metainfo['Sample', 'samplename'][0]
        if 'Comment' not in addinfo:
            addinfo['Comment'] = self.dataset.preset.get('info', '')

        fname = path.basename(self.dataset.filenames[0])
        addinfo['Filename'] = fname[1:fname.rfind(path.extsep)]

        self.dataset.preset['FILENAME'] = addinfo['Filename']

        with self.manager.createDataFile(self.dataset, self._template,
                                         self.sink.subdir,
                                         fileclass=CSVDataFile) as fp:
            self.log.debug('appending csv file: %s', fp.name)
            fieldnames = ('Filename', 'Attenuator', 'ElCol', 'Beam', 'started',
                          'cond', 'value', 'stopped', 'Detectors', 'Pressure')
            writer = csv.DictWriter(fp, fieldnames=fieldnames,
                                    extrasaction='ignore')
            writer.writerow(addinfo)

        # add some members to the datase to fake the point dataset as a scan
        # point dataset to make the DataHandler happy
        ds = self.dataset
        ds.xindex = 0
        ds.xnames = ['channels']
        ds.xunits = ['']
        ds.ynames = ['counts']
        ds.yunits = ['']
        ds.xvalueinfo = ds.devvalueinfo + ds.envvalueinfo
        ds.yvalueinfo = ds.detvalueinfo
        ds.xresults = [ds.devvaluelist + ds.envvaluelist]
        ds.yresults = [ds.detvaluelist]

        # Update the log view
        session.emitfunc('dataset', ds)

        # Clean up point dataset
        del ds.yresults
        del ds.xresults
        del ds.yvalueinfo
        del ds.xvalueinfo
        del ds.yunits
        del ds.ynames
        del ds.xunits
        del ds.xnames
        del ds.xindex
        ds.preset.pop('FILENAME')


class CSVDataSink(FileSink):
    """Appends dataset information to a CSV file."""

    parameters = {
        'lastuid': Param('UUID of the last handled dataset',
                         settable=False, type=str, internal=True,
                         mandatory=False, default=''),
        'filecount': Param('Last value of the point counter',
                           settable=False, type=int, internal=True,
                           mandatory=False, default=0),
        'datafilenametemplate': Param('Template for data file name',
                                      type=str, settable=False,
                                      prefercache=False,
                                      default='%(pointcounter)05d_%(Pos)02d-'
                                              '%(Name)s_%(Comment)s'
                                              '__%(Attenuator)s%(ElCol)s'
                                              '%(Beam)s%(Vacuum)s%(Filename)s',
                                      ),
    }
    parameter_overrides = {
        'settypes': Override(default=[POINT]),
        'filenametemplate': Override(default=['logbook.csv']),
    }

    handlerclass = CSVSinkHandler

    def wasUsed(self, dataset):
        if self.lastuid == str(dataset.uid):
            return True
        self._setROParam('lastuid', str(dataset.uid))
        return False
