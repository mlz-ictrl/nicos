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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************

"""PGAA specific data sink(s)."""

import time

import csv

from array import array
from datetime import datetime

from nicos import session
from nicos.core import Attach, Measurable, Param, Readable
from nicos.core.data.dataset import ScanData
from nicos.core.data.sink import DataSink, DataSinkHandler
from nicos.core.errors import NicosError


class PGAASinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        super(PGAASinkHandler, self).__init__(sink, dataset, detector)

    def end(self):
        # self.log.warning('dataset inc %s%s', self, self.detector)

        self.dataset.preset['stopped'] = time.time()

        vacval = self.sink._attached_vac.read(0)

        for det in (self.sink._attached_det1, self.sink._attached_det2):
            if det not in self.dataset.preset['Detectors']:
                continue
            try:
                spectrum = det.getvals()
                truetime = det.gettrue()
                livetime = det.getlive()
                prefix = det.prefix
                ecalintercept, ecalslope = det.getEcal().split()[:2]
            except NicosError:
                self.log.warning('error saving spectrum data ')
                continue
            ecalslope = float(ecalslope)
            ecalintercept = float(ecalintercept)
            mcafiledata = self.MCAFile(livetime, truetime, spectrum,
                                       ecalslope, ecalintercept)
            chnfiledata = self.CHNFile(livetime, truetime, spectrum, prefix,
                                       ecalslope, ecalintercept)

            # dir_ = os.path.dirname(__file__)
            filename = self.filename(prefix, vacval)
            mcafilename = filename + '.mca'
            chnfilename = filename + '.chn'
            # mcafilename = "logfiles/" + filename + ".mca"
            # chnfilename = "logfiles/" + filename + ".chn"

            # path = os.path.join(dir_, filename)
            try:
                with open(mcafilename, 'wb') as f:
                    for data in mcafiledata:
                        data.tofile(f)
            except IOError:
                pass

            try:
                with open(chnfilename, 'wb') as f:
                    for data in chnfiledata:
                        data.tofile(f)
            except IOError:
                pass

        self.dataset.info = self.dataset.preset

        list2str = '['
        for item in self.dataset.preset['Detectors']:
            list2str += '%s,' % item.name
        list2str += ']'

        # self.dataset.info['started'] = self.dataset.started
        self.dataset.info['Detectors'] = list2str
        self.dataset.info['Pressure'] = str(vacval) + 'mBar'
        self.dataset.info['Filename'] = self.filename('', str(vacval))
        self.dataset.info['stop by'] = self.dataset.info['cond']
        self.dataset.info['at/after'] = self.dataset.info['value']
        session.emitfunc('dataset', ScanData(self.dataset))

        with open('logfiles/logbook.csv', 'a') as file:
            fieldnames = ('Filename', 'Attenuator', 'ElCol', 'Beam', 'started',
                          'cond', 'value', 'stopped', 'Detectors', 'Pressure')
            writer = csv.DictWriter(file, fieldnames=fieldnames,
                                    extrasaction='ignore')
            row = self.dataset.info.copy()
            row['started'] = datetime.fromtimestamp(
                self.dataset.started).strftime("%Y-%m-%d %H:%M:%S")
            row['stopped'] = datetime.fromtimestamp(
                row['stopped']).strftime("%Y-%m-%d %H:%M:%S")
            row.update({'Pressure': vacval})
            writer.writerow(row)

        self.sink.filecount += 1

    def filename(self, prefix, vac):
        code = ''
        atts = {
            100.: ('out', 'out', 'out'),
            47.: ('out', 'in', 'out'),
            16.: ('in', 'out', 'out'),
            7.5: ('in', 'in', 'out'),
            5.9: ('out', 'out', 'in'),
            3.5: ('out', 'in', 'in'),
            2.7: ('in', 'out', 'in'),
            1.6: ('in', 'in', 'in')
        }[self.dataset.preset['Attenuator']]

        for i, item in enumerate(atts):
            if item == 'in':
                code += str(i + 1)
        code += 'E' if self.dataset.preset['ElCol'] == 'Ell' else 'C'
        if self.dataset.preset['Beam'] == 'closed':
            code += 'O'
        if vac < 10.:
            code += 'V'
        code += self.dataset.preset['Filename']
        # filename = '%s%s_%s-%s_%s__%s' % (
        filename = 'logfiles/%s%s_%s-%s_%s__%s' % (
            prefix, '{:05d}'.format(self.sink.filecount),
            '{:02d}'.format(self.dataset.preset['Position']),
            self.dataset.preset['Name'],
            self.dataset.preset['Comment'], code)
        return filename

    def MCAFile(self, livetime, truetime, spectrum_, ecalslope_,
                ecalintercept_):
        filedata = []
        timeb = []
        tb_time = array('i', [int(self.dataset.started)])
        tb_fill = array('h', [0, 0, 0])
        timeb.extend([tb_time, tb_fill])

        # Type elap:
        elap = []
        el_time = array('i', [int(livetime * 100), int(truetime * 100)])
        el_fill_1 = array('i', [0])
        el_fill_2 = array('d', [0])
        elap.extend([el_time, el_fill_1, el_fill_2])

        # Type xcal:
        xcal = []
        ec_fill_1 = array('f', [0, ecalslope_, ecalintercept_])
        # !! exchange sinkinfo with preset when scan command is used
        unit = array('c', '{:<5}'.format(''))
        ec_fill_2 = array('c', '\t\t\t')
        xcal.extend([ec_fill_1, unit, ec_fill_2])

        # Type mcahead:
        mcahead = []
        mc_fill = array('h', [0, 1, 0])
        mc_fill2 = array('i', [0])

        spectr_name = array('c', '{:<26}'.format(
            self.dataset.preset['Name'][:26]))
        mc_fill3 = array('h', [0])
        filler = array('h', [0 for _i in range(19)])
        nchans = array('h', [16384])
        mcahead.extend([mc_fill, mc_fill2, spectr_name, mc_fill3])
        mcahead.extend(timeb)
        mcahead.extend(elap)
        mcahead.extend(xcal)
        mcahead.extend([filler, nchans])

        filedata.extend(mcahead)
        if spectrum_:
            spectrum = array('i', spectrum_)
            filedata.append(spectrum)
        return filedata

    def CHNFile(self, livetime, truetime, spectrum_, prefix, ecalslope_,
                ecalintercept_):
        filedata = []

        # header
        mustbe = array('h', [-1])
        detnumber = array('h', [1 if prefix == 'P' else 3])
        self.log.debug('detnumber: %s', detnumber)
        segmentnumber = array('h', [0])
        seconds = array('c', '{:2}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%S')))
        self.log.debug('started: {:2}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%S')))
        truetime = array('i', [int(truetime * 50)])
        livetime = array('i', [int(livetime * 50)])
        startdate = array('c', '{:8}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%d%b%y1')))
        self.log.debug('startde: {:8}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%d%b%y1')))
        starttime = array('c', '{:4}'.format(datetime.fromtimestamp(
            int(self.dataset.started)).strftime('%H%M')))
        channeloffset = array('h', [0])
        numchannels = array('h', [16384])
        chnheader = [mustbe, detnumber, segmentnumber, seconds, truetime,
                     livetime, startdate, starttime, channeloffset,
                     numchannels]
        filedata.extend(chnheader)

        if spectrum_:
            spectrum = array('i', spectrum_)
            filedata.append(spectrum)

        # suffix
        mustbes = array('h', [-102])
        res1 = array('h', [0])
        ecalzero = array('f', [ecalintercept_])
        ecalslope = array('f', [ecalslope_])
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

        chnsuffix = [mustbes, res1, ecalzero, ecalslope, ecalquadr,
                     peakshapecalzero, peakshapecalslope, peakshapecalquadr,
                     reserved, detdesclen, detdesc, sampledesclen, sampledesc,
                     res2]
        filedata.extend(chnsuffix)
        return filedata


class PGAASink(DataSink):
    """Write spectrum to file in specific format."""

    attached_devices = {
        'det1': Attach('', Measurable),
        'det2': Attach('', Measurable),
        'vac': Attach('', Readable)
    }

    parameters = {
        'filecount': Param('filecount',
                           type=int, mandatory=False, settable=True,
                           prefercache=True, default=1),
        'ecalslope': Param('Energy Calibration Slope',
                           type=int, mandatory=False, settable=True,
                           prefercache=True, default=1),
        'ecalintercept': Param('Energy Calibration Slope',
                               type=int, mandatory=False, settable=True,
                               prefercache=True, default=1),
    }

    handlerclass = PGAASinkHandler
