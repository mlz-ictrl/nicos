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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#
# *****************************************************************************
"""PUMA specific command for the multi detector/analyzer setup."""

from __future__ import absolute_import, division, print_function

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.scan import _infostr
from nicos.core.constants import BLOCK, FINAL, POINT, SCAN, SUBSCAN
from nicos.core.data.dataset import PointDataset, ScanDataset
from nicos.core.params import Value
from nicos.core.scan import Scan, SkipPoint, StopScan, SweepScan
from nicos.utils import lazy_property

__all__ = (
    'multiadscan', 'timeadscan',
)


class ADPointDataset(PointDataset):

    settype = POINT
    countertype = POINT

    def __init__(self, **kwds):
        self.valuelist = kwds.pop('parameters', ())
        PointDataset.__init__(self, **kwds)

    @lazy_property
    def devvaluelist(self):
        ret = [self.canonical_values[v.name] for v in self.valuelist]
        return ret

    @lazy_property
    def devvalueinfo(self):
        return sum((dev.valueInfo() for dev in self.devices), self.valuelist)

    @lazy_property
    def detvalueinfo(self):
        return (Value('timer', unit='s', fmtstr='%.1f'),
                Value('monitor', unit='cts', fmtstr='%d'),
                Value('ctr', unit='cts', fmtstr='%d'))

    @lazy_property
    def detvaluelist(self):
        return self.results['det'][0]


class ADScanDataset(ScanDataset):

    settype = SCAN
    countertype = SCAN

    def __init__(self, **kwds):
        self.valuelist = kwds.get('parameters', ())
        if self.valuelist:
            kwds.pop('parameters')
        ScanDataset.__init__(self, **kwds)

    @lazy_property
    def devvalueinfo(self):
        return sum((dev.valueInfo() for dev in self.devices), self.valuelist)

    @lazy_property
    def detvalueinfo(self):
        return (Value('timer', unit='s', fmtstr='%.1f'),
                Value('monitor', unit='cts', fmtstr='%d'),
                Value('ctr', unit='cts', fmtstr='%d'))


class MultiADScan(Scan):

    def __init__(self, info_header, parnames, parlist, psipos, phipos, monopos,
                 cadpos, preset, detseq=1):
        detlist = [session.getDevice('det')]
        move = [[session.getDevice(devname), pos]
                for devname, pos in zip(['psi', 'phi', 'mono', 'cad'],
                                        [psipos, phipos, monopos, cadpos])]
        Scan.__init__(self, [], [[]], preset={'t': preset}, detlist=detlist,
                      scaninfo=info_header, firstmoves=move)
        self._detseq = detseq
        self._parnames = [(v.split('/')[0:] or [''])[0] for v in parnames]
        self._parunits = [(v.split('/')[1:] or [''])[0] for v in parnames]
        self._paraValueinfo = tuple(Value(n, unit=u if u else 'rlu',
                                          fmtstr='%.2f') for n, u in
                                    zip(self._parnames, self._parunits)) + \
                              (Value('rd', unit='deg', fmtstr='%.2f'),
                               Value('rg', unit='deg', fmtstr='%.2f'))
        self._parlist = parlist
        self._point = None
        self._data = session.experiment.data

    def beginScan(self):
        # Copy of the data.manager.beginScan with s/ScanDataset/ADScanDataset/
        self._data._clean((BLOCK,))
        dataset = ADScanDataset(
            subscan=self._subscan,
            devices=self._devices,
            environment=self._envlist,
            detectors=self._detlist,
            preset=self._preset,
            info=self._scaninfo,
            npoints=self._npoints,
            xindex=self._xindex,
            startpositions=self._startpositions,
            endpositions=self._endpositions,
            continuation=self._continuation,
            cont_direction=self._cont_direction,
            parameters=self._paraValueinfo,
        )
        for sink in session.datasinks:
            if sink.isActive(dataset):
                handlers = sink.createHandlers(dataset)
                dataset.handlers.extend(handlers)
        if self._data._current:
            self._data._current.subsets.append(dataset)
            dataset.number = len(self._data._current.subsets)
        self._data._stack.append(dataset)
        # self.dataset = self._data._init(dataset)
        # XXX: when to clean these up?
        self.dataset = dataset
        self._data._last_scans.append(self.dataset)
        self.dataset.dispatch('prepare')
        self.dataset.dispatch('begin')
        session.elogEvent('scanbegin', self.dataset)

    def beginTemporaryPoint(self, **kwds):
        """Create and begin a point dataset that does not use datasinks."""
        self._data._clean((BLOCK, SCAN, SUBSCAN))
        self._data._updatePointKeywords(kwds)
        return self._data._init(ADPointDataset(**kwds), skip_handlers=True)

    def beginPoint(self, **kwds):
        """Create and begin a point dataset."""
        self._data._clean((BLOCK, SCAN, SUBSCAN))
        self._data._updatePointKeywords(kwds)
        return self._data._init(ADPointDataset(**kwds))

    def finishPoint(self):
        self._data.finishPoint()
        Scan.finishPoint(self)

    def finishTemporaryPoint(self):
        """Remove the current point dataset."""
        if self._data._current.settype != POINT:
            session.log.warning('no data point to finish here')
            return
        point = self._data._stack.pop()
        point.trimResult()
        self._data._current.subsets.pop()

    def _inner_run(self):
        try:
            self.prepareScan(self._startpositions[0])
        except StopScan:
            return
        except SkipPoint:
            return

        det = self._detlist[0]
        detname = self._detlist[0].name
        try:
            self.preparePoint(0, [])
            self.beginScan()
            point = self.beginTemporaryPoint(detectors=self._detlist)
            self.acquire(point, self._preset)
            self.finishTemporaryPoint()
        finally:
            result = det.read()
            ct = result[0:2]  # timer, monitor
            if det._attached_images:  # setup with an image
                result = det.readArrays(FINAL)[0][0].astype('f').tolist()
            else:
                result = result[-11:]
            if self._detseq == -1:
                result = list(reversed(result))
        try:
            for i, v in enumerate(result):
                self._point = i
                with self.pointScope(i + 1):
                    point = self.beginPoint(parameters=self._paraValueinfo)
                    if i == 0:
                        self._data.updateMetainfo()
                    self._data.putResults(FINAL, {detname: (ct + [v], [])})
                    self.readEnvironment()
                    self.finishPoint()
        finally:
            self._point = None
            self.endScan()

    def readEnvironment(self):
        Scan.readEnvironment(self)
        values = {}
        for n, pv in zip(self._parnames, self._parlist[self._point]):
            values[n] = (None, pv)
        for dev in 'rd', 'rg':
            n = '%s%d' % (dev, self._point + 1)
            values[dev] = (None, session.getDevice(n).read(0))
        self._data.putValues(values)


@usercommand
@helparglist('infoheader, parnames, parlist, psi, phi, mono, cad, preset, '
             '[detseq=1]')
def multiadscan(info_header, parnames, parlist, psipos, phipos, monopos,
                cadpos, preset, detseq=1):
    """Multi analyzer 'scan'.

    This is a single point scan. The detector data (monitor, timer, and the
    counters) will be rearranged as a 11 point scan.

    * infoheader - additional header (maybe stored in data file)
    * parnames - additional parameters (stored in data file)
    * parlist - values to additional parnames (stored in data files), must have
                a length of 11 (one for each detector) and each entry must have
                the length of the parnames list
    * psipos - target position of psi device
    * phipos - target position of phi device
    * monopos - target position of mono device
    * cadpos - target position of cad device
    * preset - time to count per point
    * detseq - 1 if detector numbers in ascending order otherwise -1

    Example:

    >>> multiadscan('The following configs are selected: configuration 419 '
                    'ki= 5.40  Psi = 151.22  Phi0 = 65.50  CAD = -7.83  '
                    'tilt =-2.00 config-type 2',
                    ['h', 'k', 'l', 'ny/THz', 'x/cm', 'y/cm',  'theta/deg',
                     'phi/deg'],
                    [
                     [-4.68, 2.97, 0.00, -6.64, 10.00, 2.00, -8.27, 71.89],
                     [-4.51, 2.73, 0.00, -4.54, 8.00, 1.60, -8.71, 70.59],
                     [-4.37, 2.52, 0.00, -2.76, 6.00, 1.20, -9.15, 69.31],
                     [-4.23, 2.33, 0.00, -1.24, 4.00, 0.80, -9.58, 68.03],
                     [-4.11, 2.16, 0.00, 0.07, 2.00, 0.40, -10.01, 66.76],
                     [-4.00, 2.00, 0.00, 1.20, 0.00, 0.00, -10.43, 65.50],
                     [-3.90, 1.85, 0.00, 2.18, -2.00, -0.40, -10.84, 64.25],
                     [-3.80, 1.72, 0.00, 3.05, -4.00, -0.80, -11.24, 63.01],
                     [-3.72, 1.60, 0.00, 3.80, -6.00, -1.20, -11.63, 61.79],
                     [-3.64, 1.48, 0.00, 4.47, -8.00, -1.60, -12.01, 60.58],
                     [-3.56, 1.38, 0.00, 5.07, -10.00, -2.00, -12.39, 59.38],
                    ], 276.25, 19.995, 3.235, -0.8016, 1)
    """
    MultiADScan(info_header, parnames, parlist, psipos, phipos, monopos,
                cadpos, preset, detseq).run()


class TimeADScan(SweepScan):

    def __init__(self, header, parnames, parlist, numpoints, firstmoves=None,
                 multistep=None, detlist=None, envlist=None, preset=None,
                 scaninfo=None, subscan=False, xindex=None):

        self._parlist = parlist
        self._parnames = [(v.split('/')[0:] or [''])[0] for v in parnames]
        self._parunits = [(v.split('/')[1:] or [''])[0] for v in parnames]
        self._valueInfo = tuple(Value(n, unit=u if u else 'rlu', fmtstr='%.2f')
                                for n, u in zip(self._parnames, self._parunits))
        SweepScan.__init__(self, [], [], numpoints, firstmoves, multistep,
                           detlist, envlist, preset, scaninfo, subscan,
                           xindex)

    def readEnvironment(self):
        SweepScan.readEnvironment(self)
        self._init_par_values()

    def _init_par_values(self):
        newinfo = {}
        for i, values in enumerate(self._parlist):
            for name, value, unit in zip(self._parnames, values,
                                         self._parunits):
                if name in ('rd', 'rg'):
                    continue
                strvalue = '%.2f' % value
                newinfo['%s%d' % (name, i + 1), 'value'] = (value, strvalue,
                                                            unit, 'general')
        session.experiment.data.putMetainfo(newinfo)


@usercommand
@helparglist('numpoints, header, parnames, parlist, psipos, phipos, monopos, '
             'cadpos, timepreset')
def timeadscan(numpoints, header, parnames, parlist, psi, phi, mono, cad, t):
    """Time scan in multianalyzer setup.

    Count a number of times without moving devices, except the 'psi', 'phi',
    'mono', and 'cad' before counting the first time.

    * numpoints - number of repititions can be -1 to scan for unlimited points
                  (break using Ctrl-C or the GUI to quit).
    * header - additional header (maybe stored in data file)
    * parnames - additional parameters (stored in data file)
    * parlist - values to additional parnames (stored in data files), must have
                a length of 11 (one for each detector) and each entry must have
                the length of the parnames list
    * psipos - target position of psi device
    * phipos - target position of phi device
    * monopos - target position of mono device
    * cadpos - target position of cad device
    * timepreset - time to count per point

    Example:

    >>> timeadscan(5, 'The following configs are selected: configuration 419 '
                   'ki= 5.40  Psi = 151.22  Phi0 = 65.50  CAD = -7.83  '
                   'tilt =-2.00 config-type 2',
                   ['h', 'k', 'l', 'ny/THz', 'x/cm', 'y/cm',  'theta/deg',
                    'phi/deg'],
                   [
                    [-4.68, 2.97, 0.00, -6.64, 10.00, 2.00, -8.27, 71.89],
                    [-4.51, 2.73, 0.00, -4.54, 8.00, 1.60, -8.71, 70.59],
                    [-4.37, 2.52, 0.00, -2.76, 6.00, 1.20, -9.15, 69.31],
                    [-4.23, 2.33, 0.00, -1.24, 4.00, 0.80, -9.58, 68.03],
                    [-4.11, 2.16, 0.00, 0.07, 2.00, 0.40, -10.01, 66.76],
                    [-4.00, 2.00, 0.00, 1.20, 0.00, 0.00, -10.43, 65.50],
                    [-3.90, 1.85, 0.00, 2.18, -2.00, -0.40, -10.84, 64.25],
                    [-3.80, 1.72, 0.00, 3.05, -4.00, -0.80, -11.24, 63.01],
                    [-3.72, 1.60, 0.00, 3.80, -6.00, -1.20, -11.63, 61.79],
                    [-3.64, 1.48, 0.00, 4.47, -8.00, -1.60, -12.01, 60.58],
                    [-3.56, 1.38, 0.00, 5.07, -10.00, -2.00, -12.39, 59.38],
                   ], 276.25, 19.995, 3.235, -0.8016, 1)
    """
    preset = {'t': t}
    scanstr = _infostr('timeadscan',
                       (numpoints,) + (psi, phi, mono, cad),
                       preset)
    move = [[session.getDevice(devname), pos]
            for devname, pos in zip(['psi', 'phi', 'mono', 'cad'],
                                    [psi, phi, mono, cad])]

    scan = TimeADScan(header, parnames, parlist, numpoints, move,
                      preset=preset, scaninfo='%s %s' % (scanstr, header))
    scan.run()
