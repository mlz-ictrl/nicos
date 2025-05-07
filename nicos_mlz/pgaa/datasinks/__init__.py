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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************

"""PGAA specific data sink(s)."""

import struct
from array import array
from csv import DictWriter
from datetime import datetime
from io import FileIO, TextIOWrapper
from os import path

import numpy as np

from nicos import session
from nicos.core import Override, Param
from nicos.core.constants import POINT
from nicos.core.data.sink import DataSinkHandler
from nicos.devices.datasinks import FileSink
from nicos.devices.datasinks.image import ImageFileReader, \
    SingleFileSinkHandler
from nicos.devices.datasinks.special import LiveViewSink as BaseLiveViewSink, \
    LiveViewSinkHandler as BaseLiveViewSinkHandler
from nicos.utils import enableDisableFileItem

__all__ = ('MCASink', 'MCAFileReader', 'CHNSink', 'CHNFileReader',
           'CSVDataSink', 'LiveViewSink')


class SinkHandler(SingleFileSinkHandler):
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

    defer_file_creation = True

    accecpt_final_images_only = True

    def __init__(self, sink, dataset, detector):
        SingleFileSinkHandler.__init__(self, sink, dataset, detector)

    def _createFile(self, **kwargs):
        if self._file is None:
            self.manager.assignCounter(self.dataset)
            addinfo = self._addinfo.copy()
            addinfo.update(self.manager.getCounters())
            templates = [t + '%s%s' % (path.extsep, self.filetype)
                         for t in self.sink.filenametemplate]
            self._file = self.manager.createDataFile(
                self.dataset, templates, self.sink.subdir,
                fileclass=self.fileclass, filemode=self.sink.filemode,
                logger=self.sink.log, additionalinfo=addinfo)
        return self._file

    def putMetainfo(self, metainfo):

        def _value(dev):
            return metainfo[dev, 'value'][0]

        self._addinfo = self.dataset.preset.copy()
        code = ''
        for i, item in enumerate(self.atts[_value('att')]):
            code += '%d' % (i + 1) if item == 'in' else ''
        self._addinfo['Attenuator'] = code
        self._addinfo['ElCol'] = _value('ellcol')[:1]
        self._addinfo['Beam'] = 'O' if metainfo[
                self.detector.name, 'enablevalues'][0][0] == 'closed' else ''
        self._addinfo['Vacuum'] = \
            'V' if _value('chamber_pressure') < 10. else ''
        self._addinfo['Prefix'] = self.detector.prefix
        self._addinfo['Pos'] = metainfo.get(('sc', 'value'), [0])[0]
        self._addinfo['Name'] = metainfo['Sample', 'samplename'][0]
        if 'Comment' not in self._addinfo:
            self._addinfo['Comment'] = self.dataset.preset.get('info', '')

    def writeData(self, fp, image):
        spectrum = image.tolist()
        for i, vi in enumerate(self.detector.valueInfo()):
            if vi.name == 'truetim':
                truetime = self.dataset.detvaluelist[i]
            elif vi.name == 'livetim':
                livetime = self.dataset.detvaluelist[i]

        ecalintercept = float(self.detector.ecalintercept)
        ecalslope = float(self.detector.ecalslope)

        self._write_file(self._file, self._addinfo, livetime, truetime,
                         spectrum, ecalslope, ecalintercept)

    def _write_file(self, fp, addinfo, livetime, truetime, spectrum, ecalslope,
                    ecalintercept):
        raise NotImplementedError('Implement "_write_file" in subclasses.')


class MCASinkHandler(SinkHandler):
    """Data sink handler for the Ortec MCA files."""

    filetype = 'mca'

    def _write_file(self, fp, addinfo, livetime, truetime, spectrum, ecalslope,
                    ecalintercept):
        tb_time = array('i', [int(self.dataset.started)])
        tb_fill = array('h', [0, 0, 0])  # millitm, timezone, dstflag
        timeb = [tb_time, tb_fill]

        # Type elap:
        el_time = array('i', [int(livetime * 100), int(truetime * 100)])
        el_fill_1 = array('i', [0])  # sweeps
        el_fill_2 = array('d', [0])  # comp
        elap = [el_time, el_fill_1, el_fill_2]

        # Type xcal:
        ec_fill_1 = array('f', [0, ecalslope, ecalintercept])
        # !! exchange sinkinfo with preset when scan command is used
        unit = array('b', '{:<5}'.format('').encode())  # empty unit
        ec_fill_2 = array('b', '\t\t\t'.encode())  # unittype, cformat, corder
        xcal = [ec_fill_1, unit, ec_fill_2]

        # Type mcahead:
        mc_fill = array('h', [0, 1, 0])  # readtype, mca number, readregion
        mc_fill2 = array('i', [0])  # tag no

        spectr_name = array(
            'b', '{:<26}'.format(addinfo.get('Name', '')[:26]).encode())
        mc_fill3 = array('h', [0])  # acq mode
        filler = array('h', [0 for _i in range(19)])  # filler
        nchans = array('H', [len(spectrum)])  # number of channels
        filedata = [mc_fill, mc_fill2, spectr_name, mc_fill3]
        filedata.extend(timeb)
        filedata.extend(elap)
        filedata.extend(xcal)
        filedata.extend([filler, nchans])

        if spectrum:
            filedata.append(array('i', spectrum))

        self.log.debug('write mca file: %s', fp.name)
        for data in filedata:
            data.tofile(fp)


class MCAFileReader(ImageFileReader):

    filetypes = [('mca', 'ORTEC MCA Data File (*.mca)')]

    @classmethod
    def fromfile(cls, filename):
        with open(filename, 'rb') as f:
            f.seek(126)
            numchannels = struct.unpack('H', f.read(2))[0]
            spectrum = np.zeros(numchannels, '<i4')
            for i in range(numchannels):
                spectrum[i] = struct.unpack('I', f.read(4))[0]
            return spectrum


class CHNSinkHandler(SinkHandler):
    """Data sink handler for the channel data files."""

    filetype = 'chn'

    def _write_file(self, fp, addinfo, livetime, truetime, spectrum, ecalslope,
                    ecalintercept):
        # header
        version = array('h', [-1])
        detnumber = array('h', [1 if addinfo['Prefix'] == 'P' else 3])
        segmentnumber = array('h', [0])
        s = '{:2}'.format(
            datetime.fromtimestamp(int(self.dataset.started)).strftime('%S'))
        seconds = array('b', s.encode())
        self.log.debug('started: %s', s)
        truetime = array('i', [int(truetime * 50)])
        livetime = array('i', [int(livetime * 50)])
        s = '{:8}'.format(
            datetime.fromtimestamp(int(self.dataset.started)).strftime(
                '%d%b%y1'))
        startdate = array('b', s.encode())
        s = '{:4}'.format(
            datetime.fromtimestamp(int(self.dataset.started)).strftime('%H%M'))
        starttime = array('b', s.encode())

        channeloffset = array('h', [0])
        numchannels = array('H', [len(spectrum)])
        filedata = [version, detnumber, segmentnumber, seconds, truetime,
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
        reserved = array('b', '{:228}'.format('').encode())
        detdesclen = array('b', '{:1}'.format('1').encode())
        detdesc = array('b', '{:63}'.format('d').encode())
        sampledesclen = array('b', '{:1}'.format('1').encode())
        sampledesc = array('b', '{:63}'.format('s').encode())
        res2 = array('b', '{:128}'.format('').encode())

        filedata += [mustbes, res1, ecalzero, ecalslope, ecalquadr,
                     peakshapecalzero, peakshapecalslope, peakshapecalquadr,
                     reserved, detdesclen, detdesc, sampledesclen, sampledesc,
                     res2]

        self.log.debug('write chn file: %s', fp.name)
        for data in filedata:
            data.tofile(fp)


class CHNFileReader(ImageFileReader):

    filetypes = [('chn', 'ORTEC CHN Integer Data File (*.chn)')]

    @classmethod
    def fromfile(cls, filename):
        with open(filename, 'rb') as f:
            f.seek(30)
            # pylint: disable=unused-variable
            # version = struct.unpack('h', f.read(2))[0]
            # detnumber = struct.unpack('h', f.read(2))[0]
            # segmentnumber = struct.unpack('h', f.read(2))[0]
            # seconds = f.read(2).decode()
            # truetime = struct.unpack('I', f.read(4))[0]
            # livetime = struct.unpack('I', f.read(4))[0]
            # startdate = f.read(8).decode()
            # starttime = f.read(4).decode()
            # channeloffset = struct.unpack('h', f.read(2))[0]
            # pylint: enable=unused-variable
            numchannels = struct.unpack('H', f.read(2))[0]
            spectrum = np.zeros(numchannels, '<i4')
            for i in range(numchannels):
                spectrum[i] = struct.unpack('I', f.read(4))[0]
            return spectrum


class Sink(FileSink):
    """Write spectrum to file in specific format."""

    parameter_overrides = {
        'settypes': Override(default=[POINT]),
        'filenametemplate': Override(
            default=['%(Prefix)s%(pointcounter)05d_%(Pos)02d-%(Name)s_'
                     '%(Comment)s__%(Attenuator)s%(ElCol)s%(Beam)s%(Vacuum)s'
                     '%(Filename)s']),
    }

    handlerclass = SinkHandler


class MCASink(Sink):
    """Write spectrum to file in Ortec format."""

    handlerclass = MCASinkHandler


class CHNSink(Sink):
    """Write spectrum to file in channel format."""

    handlerclass = CHNSinkHandler


class CSVDataFile(TextIOWrapper):
    """Represents a csv data file."""

    def __init__(self, shortpath, filepath, filemode=None, logger=None):
        TextIOWrapper.__init__(self, FileIO(filepath, 'a'), encoding='utf-8')
        self.shortpath = shortpath
        self.filepath = filepath
        self._log = logger
        self._filemode = filemode

    def close(self):
        TextIOWrapper.close(self)
        if self._filemode is not None:
            enableDisableFileItem(self.filepath, self._filemode,
                                  logger=self._log)


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
        self._metainfo = {}
        self._template = sink.filenametemplate

    def putMetainfo(self, metainfo):
        self._metainfo = metainfo.copy()

    def _value(self, dev):
        return self._metainfo[dev, 'value'][0]

    def end(self):
        if not self._metainfo or self.sink.wasUsed(self.dataset):
            return

        self.manager.assignCounter(self.dataset)
        counters = self.manager.getCounters()

        self.sink._setROParam('filecount', counters.get('pointcounter', 0))
        addinfo = counters.copy()
        addinfo.update(self.dataset.preset)
        addinfo['Attenuator'] = self._value('att')
        addinfo['ElCol'] = self._value('ellcol')
        addinfo['Beam'] = self._metainfo[self.detector.name,
                                         'enablevalues'][0][0]

        for cond in ['LiveTime', 'TrueTime', 'counts']:
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
        addinfo['Pos'] = self._metainfo.get(('sc', 'value'), [0])[0]
        addinfo['Name'] = self._metainfo['Sample', 'samplename'][0]
        if 'Comment' not in addinfo:
            addinfo['Comment'] = self.dataset.preset.get('info', '')

        with self.manager.createDataFile(self.dataset, self._template,
                                         self.sink.subdir,
                                         fileclass=CSVDataFile) as fp:
            fname = path.basename(self.dataset.filenames[0])
            addinfo['Filename'] = fname[1:fname.rfind(path.extsep)]
            self.dataset.preset['FILENAME'] = addinfo['Filename']

            fieldnames = ('Filename', 'Attenuator', 'ElCol', 'Beam', 'started',
                          'cond', 'value', 'stopped', 'Detectors', 'Pressure')
            writer = DictWriter(fp, fieldnames=fieldnames,
                                extrasaction='ignore')
            if not fp.tell():
                writer.writeheader()
            writer.writerow(addinfo)

        # add some members to the dataset to fake the point dataset as a scan
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


class LiveViewSinkHandler(BaseLiveViewSinkHandler):

    def getLabelArrays(self, result):
        ds = self.dataset
        detname = self.detector.name
        slope = ds.metainfo.get((detname, 'ecalslope'), [0.178138])[0]
        start = ds.metainfo.get((detname, 'ecalintercept'), [0.563822])[0]
        steps = ds.metainfo.get((detname, 'size'), [[65535]])[0][0]
        erange = np.linspace(start, start + slope * (steps - 1), steps)
        self.log.debug('start: %s, end: %s', erange[0], erange[-1])
        return [erange]

    def getLabelDescs(self, result):
        return {
            'x': {
                'title': 'energy [keV]',
                'define': 'array',
                'dtype': 'float64',
                'index': 0,
            },
            'y': {'define': 'classic', 'title': 'counts'},
        }


class LiveViewSink(BaseLiveViewSink):
    """A data sink that sends images to attached clients for live preview."""

    handlerclass = LiveViewSinkHandler
