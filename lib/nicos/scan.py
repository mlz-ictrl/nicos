#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Scan classes for NICOS."""

__version__ = "$Revision$"

import time

from nicos import session, status
from nicos.utils import Repeater
from nicos.errors import NicosError, LimitError, FixedError, UsageError
from nicos.device import Readable
from nicos.commands.output import printwarning
from nicos.commands.measure import _count


INFO_CATEGORIES = [
    ('experiment', 'Experiment information'),
    ('sample', 'Sample and alignment'),
    ('instrument', 'Instrument setup'),
    ('offsets', 'Offsets'),
    ('limits', 'Limits'),
    ('precisions', 'Precisions'),
    ('status', 'Instrument status'),
    ('general', 'Instrument state at first scan point'),
]


class Scan(object):
    """
    Represents a general scan over some devices with a specified detector.
    """

    def __init__(self, devices, positions, firstmoves=None, multistep=None,
                 detlist=None, envlist=None, preset=None, scaninfo=None,
                 scantype=None):
        if session.mode == 'slave':
            raise UsageError('cannot scan in slave mode')
        self.dataset = session.experiment.createDataset(scantype)
        if not detlist:
            detlist = session.experiment.detectors
        if not detlist:
            printwarning('Scanning without detector, use SetDetectors() '
                         'to select which detector(s) you want to use')
        if envlist is None:
            envlist = session.experiment.sampleenv
        self._firstmoves = firstmoves
        self._multistep = self.dataset.multistep = multistep
        if self._multistep:
            self._mscount = len(multistep[0][1])
            self._mswhere = [[(mse[0], mse[1][i]) for mse in multistep]
                             for i in range(self._mscount)]
        self._devices = self.dataset.devices = devices
        self._positions = self.dataset.positions = positions
        self._detlist = self.dataset.detlist = detlist
        self._envlist = self.dataset.envlist = envlist
        self._preset = self.dataset.preset = preset
        self.dataset.scaninfo = scaninfo
        self._sinks = self.dataset.sinks
        try:
            self._npoints = len(positions)  # can be zero if not known
        except TypeError:
            self._npoints = 0

    def prepareScan(self, positions):
        session.action('Moving to start')
        can_measure = True
        # the move-before devices
        if self._firstmoves:
            can_measure = self.moveDevices(self._firstmoves)
        # the scanned-over devices
        can_measure &= self.moveTo(positions)
        return can_measure

    def beginScan(self):
        dataset = self.dataset
        session.experiment._last_datasets.append(dataset)
        dataset.results = []
        dataset.sinkinfo = []
        dataset.xnames, dataset.xunits = [], []
        for dev in self._devices + self._envlist:
            dataset.xnames.append(dev.name)
            dataset.xunits.append(dev.unit)
        dataset.yvalueinfo = sum((det.valueInfo() for det in dataset.detlist), ())
        dataset.yunits = [val.unit for val in dataset.yvalueinfo]
        if self._multistep:
            dataset.ynames = []
            for i in range(self._mscount):
                addname = '_' + '_'.join('%s_%s' % (mse[0], mse[1][i])
                                         for mse in self._multistep)
                dataset.ynames.extend(val.name + addname
                                      for val in dataset.yvalueinfo)
            dataset.yvalueinfo = dataset.yvalueinfo * self._mscount
            dataset.yunits = dataset.yunits * self._mscount
        else:
            dataset.ynames = [val.name for val in dataset.yvalueinfo]
        dataset.sinkinfo = {}
        for sink in self._sinks:
            sink.prepareDataset(dataset)
        for sink in self._sinks:
            sink.beginDataset(dataset)
        bycategory = {}
        for name, device in sorted(session.devices.iteritems()):
            if device.lowlevel:
                continue
            for category, key, value in device.info():
                bycategory.setdefault(category, []).append((device, key, value))
        for catname, catinfo in INFO_CATEGORIES:
            if catname not in bycategory:
                continue
            for sink in self._sinks:
                sink.addInfo(dataset, catinfo, bycategory[catname])

    def preparePoint(self, num, xvalues):
        session.beginActionScope('Point %d/%d' % (num, self._npoints))
        self.dataset.curpoint = num

    def addPoint(self, xvalues, yvalues):
        self.dataset.results.append(yvalues)
        for sink in self._sinks:
            sink.addPoint(self.dataset, xvalues, yvalues)

    def finishPoint(self):
        session.endActionScope()
        session.breakpoint(2)

    def endScan(self):
        for sink in self._sinks:
            sink.endDataset(self.dataset)
        session.breakpoint(1)

    def handleError(self, dev, val, err):
        """Handle an error occurring during positioning for a point.
        If the return value is True, continue measuring this point even if
        the device has not arrived.  If it is False, continue with the next
        point.  If the scan should be aborted, the exception is reraised.
        """
        if isinstance(err, LimitError):
            printwarning('Skipping data point', exc=1)
            return False
        elif isinstance(err, FixedError):
            raise
        else:
            # consider all other errors to be fatal
            raise

    def moveTo(self, position):
        """Move scan devices to *position*, a list of positions."""
        return self.moveDevices(zip(self._devices, position))

    def moveDevices(self, where):
        """Move to *where*, which is a list of (dev, position) tuples.
        On errors, call handleError, which decides when the scan may continue.
        """
        waitdevs = []
        for dev, val in where:
            try:
                dev.start(val)
            except NicosError, err:
                # handleError can reraise for fatal error, return False
                # to skip this point and True to measure anyway
                return self.handleError(dev, val, err)
            else:
                waitdevs.append((dev, val))
        for dev, val in waitdevs:
            try:
                dev.wait()
            except NicosError, err:
                return self.handleError(dev, val, err)
        return True

    def readPosition(self):
        return [dev.read() for dev in self._devices]

    def readEnvironment(self, start, finished):
        # XXX take history mean, warn if values deviate too much?
        return [dev.doRead() for dev in self._envlist]

    def run(self):
        session.beginActionScope('Scan')
        try:
            self._inner_run()
        finally:
            session.endActionScope()

    def _inner_run(self):
        # move all devices to starting position before starting scan
        can_measure = self.prepareScan(self._positions[0])
        self.beginScan()
        try:
            for i, position in enumerate(self._positions):
                self.preparePoint(i+1, position)
                try:
                    if position:
                        session.action('Positioning')
                        if i > 0:
                            can_measure = self.moveTo(position)
                        if not can_measure:
                            continue
                    started = time.time()
                    actualpos = self.readPosition()
                    if self._multistep:
                        result = []
                        for i in range(self._mscount):
                            self.moveDevices(self._mswhere[i])
                            session.action('Counting (step %s)' % (i+1))
                            result.extend(_count(self._detlist, self._preset))
                    else:
                        session.action('Counting')
                        result = list(_count(self._detlist, self._preset))
                    finished = time.time()
                    actualpos += self.readEnvironment(started, finished)
                    self.addPoint(actualpos, result)
                finally:
                    self.finishPoint()
        finally:
            self.endScan()


class ElapsedTime(Readable):
    temporary = True
    def doRead(self):
        return 0
    def doStatus(self):
        return status.OK, ''

class TimeScan(Scan):
    """
    Special scan class for time scans with elapsed time counter.
    """

    def __init__(self, numsteps, firstmoves=None, multistep=None,
                 detlist=None, envlist=None, preset=None, scaninfo=None,
                 scantype=None):
        self._etime = ElapsedTime('etime', unit='s', fmtstr='%.1f')
        self._started = time.time()
        if envlist is None:
            envlist = list(session.experiment.sampleenv)
        envlist.insert(0, self._etime)
        if numsteps < 0:
            steps = Repeater([])
        else:
            steps = [[]] * numsteps
        Scan.__init__(self, [], steps, firstmoves, multistep,
                      detlist, envlist, preset, scaninfo, scantype)

    def readEnvironment(self, started, finished):
        ret = Scan.readEnvironment(self, started, finished)
        ret[0] = finished - self._started
        return ret

    def endScan(self):
        Scan.endScan(self)
        self._etime.shutdown()


class ManualScan(Scan):
    """
    Special scan class for "manual" scans.
    """

    def __init__(self, firstmoves=None, multistep=None, detlist=None,
                 envlist=None, preset=None, scaninfo=None, scantype=None):
        Scan.__init__(self, [], Repeater([]), firstmoves, multistep,
                      detlist, envlist, preset, scaninfo, scantype)
        self._curpoint = 0

    def manualBegin(self):
        session.beginActionScope('Scan')
        self.beginScan()

    def manualEnd(self):
        self.endScan()
        session.endActionScope()

    def step(self, **preset):
        preset = preset or self._preset
        self._curpoint += 1
        self.preparePoint(self._curpoint, [])
        try:
            started = time.time()
            actualpos = self.readPosition()
            if self._multistep:
                result = []
                for i in range(self._mscount):
                    self.moveDevices(self._mswhere[i])
                    session.action('Counting (step %s)' % (i+1))
                    result.extend(_count(self._detlist, preset))
            else:
                session.action('Counting')
                result = list(_count(self._detlist, preset))
            finished = time.time()
            actualpos += self.readEnvironment(started, finished)
            self.addPoint(actualpos, result)
        finally:
            self.finishPoint()


class QScan(Scan):
    """
    Special scan class for scans with a triple axis instrument in Q/E space.
    """

    def __init__(self, positions, firstmoves=None, multistep=None,
                 detlist=None, envlist=None, preset=None, scaninfo=None,
                 scantype=None):
        inst = session.instrument
        Scan.__init__(self, [inst.h, inst.k, inst.l, inst.E], positions,
                      firstmoves, multistep, detlist, envlist, preset,
                      scaninfo, scantype)
        self._envlist[0:0] = [inst._adevs['mono'], inst._adevs['ana'],
                              inst._adevs['psi'], inst._adevs['phi']]

    def beginScan(self):
        if len(self._positions) > 1:
            # determine first varying index as the plotting index
            for i in range(4):
                if self._positions[0][i] != self._positions[1][i]:
                    self.dataset.xindex = i
                    break
        Scan.beginScan(self)

    def moveTo(self, position):
        # move instrument en-bloc, not individual Q indices
        return self.moveDevices([(session.instrument, position)])


class ContinuousScan(Scan):
    """
    Special scan class for scans with one axis moving continuously (used for
    peak search).
    """

    def __init__(self, device, start, end, speed, firstmoves=None, detlist=None,
                 scaninfo=None):
        self._startpos = start
        self._endpos = end
        if speed is None:
            self._speed = device.speed / 5.
        else:
            self._speed = speed

        Scan.__init__(self, [device], [], firstmoves, None, detlist, [],
                      None, scaninfo)

    def run(self):
        device = self._devices[0]
        detlist = self._detlist
        can_measure = self.prepareScan([self._startpos])
        if not can_measure:
            return
        self.beginScan()
        session.action('Scanning')
        original_speed = device.speed
        try:
            device.speed = self._speed
            device.move(self._endpos)
            preset = abs(self._speed * (self._endpos - self._startpos)) * 5
            for det in detlist:
                det.start(t=preset)
            last = sum((det.read() for det in detlist), ())
            while device.doStatus()[0] == status.BUSY:
                time.sleep(1)
                session.breakpoint(2)
                devpos = device.doRead()
                read = sum((det.read() for det in detlist), ())
                diff = [read[i] - last[i]
                        if isinstance(i, (int, long, float)) else read[i]
                        for i in range(len(read))]
                self.addPoint([devpos], diff)
                last = read
            for det in detlist:
                det.stop()
        finally:
            device.stop()
            device.speed = original_speed
            self.endScan()
