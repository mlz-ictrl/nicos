#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import os
import time

from nicos import session
from nicos.core import Param
from nicos.core.data.sink import DataSink

from nicos_sinq.devices.sinqasciisink import SINQAsciiSink, \
    SINQAsciiSinkHandler
from nicos_sinq.sxtal.util import window_integrate


class SxtalScanSink(SINQAsciiSink):
    """
    This sink just suppresses the creation of ASCII scan files
    when measuring reflection lists.
    """

    def createHandlers(self, dataset):
        if session.instrument.ccl_file:
            return None
        return DataSink.createHandlers(self, dataset)


class CCLSinkHandler(SINQAsciiSinkHandler):
    """
    This implements CCL and intensity file writing. The CCL file format
    saves the scan made for each reflection in a very compact format.
    """

    _ccl_file = None
    _rfl_file = None
    header = None
    headerWritten = False
    scanvalues = {}
    _count = 0
    _scandataset = None
    _lastsubscan = None

    def prepare(self):
        if self.dataset.settype == 'scan':
            # Assign the counter
            self.manager.assignCounter(self.dataset)

            # Generate the filenames, only if not set
            if not self.dataset.filepaths:
                self.manager.getFilenames(self.dataset,
                                          self.sink.filenametemplate,
                                          self.sink.subdir)
            self._scandataset = self.dataset

    def begin(self):
        if not self._ccl_file:
            self._ccl_file = open(self.dataset.filepaths[0], 'w')  # pylint: disable=consider-using-with
            base = os.path.splitext(self.dataset.filepaths[0])[0]
            rflfile = base + '.rfl'
            self._rfl_file = open(rflfile, 'w')  # pylint: disable=consider-using-with
            self._rfl_file.write('%s\n' % rflfile)

    def addSubset(self, point):
        # Prevent unwelcome things from happening in the base class
        pass

    def _write_profile(self):
        # Write first profile header line
        hkl = session.instrument.read(0)
        ang = session.instrument._readPos(0)
        # Collect profile
        detinfo = self.dataset.detvalueinfo
        detID = 0
        for det in detinfo:
            if det.name == self.sink.detector:
                break
            detID += 1
        counts = []
        subdata = self.dataset.detvaluelists
        for sub in subdata:
            counts.append(sub[detID])
        ok, reason, intensity, sigma = window_integrate(counts)
        if not ok:
            session.log.warning(' Failed integration of %f %f %f with %s',
                                hkl[0], hkl[1], hkl[2], reason)
        if len(ang) > 3:
            self._ccl_file.write(
                '%4d %7.3f %7.3f %7.3f %7.2f '
                '%7.2f %7.2f %7.0f %7.2f\n' %
                (self._count, hkl[0], hkl[1], hkl[2],
                 ang[0], ang[1], ang[2], intensity, sigma))
        else:
            self._ccl_file.write(
                '%4d %7.3f %7.3f %7.3f %7.2f '
                '%7.2f %7.2f %7.2f %7.0f %7.2f\n' %
                (self._count, hkl[0], hkl[1], hkl[2],
                 ang[0], ang[1], ang[2], ang[3], intensity, sigma))
        # Second profile header line
        np = len(self.dataset.subsets)
        keys = list(self.dataset.preset.keys())
        preset = self.dataset.preset[keys[0]]
        devvals = self.dataset.devvaluelists
        step = devvals[1][0] - devvals[0][0]
        time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(time.time()))
        # Find environment information
        evlist = self.dataset.envvalueinfo
        evvallist = self.dataset.envvaluelists[-1]
        temp = 0
        mf = 0
        idx = 0
        for ev in evlist:
            if ev.name == 't' or ev.name == 'temp' or ev.name == 'temperature':
                temp = evvallist[idx]
            if ev.name == 'mf':
                mf = evvallist[idx]
            idx += 1
        self._ccl_file.write('%3d %7.4f %9.0f %7.3f %12f %s\n' %
                             (np, step, preset, temp, mf, time_str))
        # Print profile
        printed = 0
        for c in counts:
            self._ccl_file.write('%7d' % c)
            printed += 1
            if printed >= 10:
                self._ccl_file.write('\n')
                printed = 0
        if printed < 10:
            self._ccl_file.write('\n')
        # Write RFL line
        if len(ang) < 4:
            # Hack for NB where there are only 3 angles
            ll = list(ang)
            ll.append(.0)
            ang = tuple(ll)
        self._rfl_file.write('%5d %6.2f %6.2f %6.2f %7.2f %7.2f '
                             '%7.2f %7.2f %7.0f %7.2f\n'
                             % (self._count, hkl[0], hkl[1], hkl[2],
                                ang[0], ang[1], ang[2], ang[3],
                                intensity, sigma))
        self._rfl_file.flush()
        self._ccl_file.flush()
        self._count += 1

    def _write_rfl_header(self):
        time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(time.time()))
        self._rfl_file.write('filetime = %s\n' % time_str)
        self._rfl_file.write('lambda = %f Angstroem\n' %
                             session.instrument.wavelength)
        sample = session.getDevice('Sample')
        self._rfl_file.write('UB = %s\n' % (' '.join(format(x, '8.4f')
                                                     for x
                                                     in sample.ubmatrix)))
        self._rfl_file.write('sample = %s\n' % sample.name)
        self._rfl_file.write('user = %s\n' % session.experiment.users)

    def end(self):
        if self.dataset.settype == 'subscan' and \
                self.dataset.npoints == len(self.dataset.subsets):
            # The observation is that end() is called two times
            # with a settype of subscan. This code is a hack to
            # ensure that we close the file on the second one.
            # This should not be necessary: the expected settype is scan
            # from the HKLScan. I debugged this to Dataset.dispatch().
            # Before getattr(method)(args) the settype is scan but
            # afterwards it is subscan. May be, the NICOS team has an
            # opinion on why this happens. Anyway, ths now works.
            if self._lastsubscan == self.dataset:
                self._ccl_file.close()
                self._rfl_file.close()
                self._ccl_file = None
                self.sink.end()
                return
            self._lastsubscan = self.dataset
            if not self.headerWritten:
                self.dataset.filepaths = self._scandataset.filepaths
                self._initHeader()
                self._ccl_file.write(self.header)
                self._write_rfl_header()
                self.headerWritten = True
            self._write_profile()
            return

        if self.dataset.settype == 'scan':
            # This is not executed but should...
            self._ccl_file.close()
            self._rfl_file.close()
            self._ccl_file = None
            self.sink.end()
            self._lastsubscan = None


class CCLSink(SINQAsciiSink):
    """
    This is a sink for writing single crystal CCL and
    reflection files. It reuses the template of SINQASCIISink,
    this is why it derives from it.
    """
    parameters = {
        'detector': Param('The detector to write as profile counts',
                          type=str),
    }

    handlerclass = CCLSinkHandler
    _handlerObj = None

    def createHandlers(self, dataset):
        if not session.instrument.ccl_file:
            return []
        if self._handlerObj is None:
            self._handlerObj = self.handlerclass(self, dataset, None)
        else:
            self._handlerObj.dataset = dataset
        return [self._handlerObj]

    def end(self):
        self._handlerObj = None
