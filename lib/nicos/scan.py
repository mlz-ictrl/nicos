#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

from nicos import session
from nicos.tas import TAS
from nicos.core import status, Readable, NicosError, LimitError, \
     ModeError, InvalidValueError, PositionError, CommunicationError, \
     TimeoutError, ComputationError, MoveError, INFO_CATEGORIES
from nicos.utils import Repeater
from nicos.commands.output import printwarning
from nicos.commands.measure import _count


class SkipPoint(Exception):
    """Custom exception class to skip a scan point."""

class StopScan(Exception):
    """Custom exception class to stop the rest of the scan."""


class Scan(object):
    """
    Represents a general scan over some devices with a specified detector.
    """

    shortdesc = None

    def __init__(self, devices, positions, firstmoves=None, multistep=None,
                 detlist=None, envlist=None, preset=None, scaninfo=None,
                 scantype=None):
        if session.mode == 'slave':
            raise ModeError('cannot scan in slave mode')
        self.dataset = session.experiment.createDataset(scantype)
        if not detlist:
            detlist = session.experiment.detectors
        if not detlist:
            printwarning('scanning without detector, use SetDetectors() '
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
        self.dataset.sinkinfo = {}
        try:
            self._npoints = len(positions)  # can be zero if not known
        except TypeError:
            self._npoints = 0

    def prepareScan(self, positions):
        session.action('Moving to start')
        # the move-before devices
        if self._firstmoves:
            self.moveDevices(self._firstmoves)
        # the scanned-over devices
        self.moveTo(positions)

    def beginScan(self):
        dataset = self.dataset
        session.experiment._last_datasets.append(dataset)
        dataset.xresults = []
        dataset.yresults = []
        dataset.xvalueinfo = sum((dev.valueInfo()
                                  for dev in self._devices + self._envlist), ())
        dataset.yvalueinfo = sum((det.valueInfo()
                                  for det in dataset.detlist), ())
        if self._multistep:
            dataset.yvalueinfo = dataset.yvalueinfo * self._mscount
        for sink in self._sinks:
            sink.prepareDataset(dataset)
        for sink in self._sinks:
            sink.beginDataset(dataset)
        bycategory = {}
        for _, device in sorted(session.devices.iteritems()):
            if device.lowlevel:
                continue
            for category, key, value in device.info():
                bycategory.setdefault(category, []).append((device, key, value))
        for catname, catinfo in INFO_CATEGORIES:
            if catname not in bycategory:
                continue
            for sink in self._sinks:
                sink.addInfo(dataset, catinfo, bycategory[catname])
        session.elog_event('scanbegin', dataset)

    def preparePoint(self, num, xvalues):
        session.beginActionScope('Point %d/%d' % (num, self._npoints))
        self.dataset.curpoint = num

    def addPoint(self, xvalues, yvalues):
        self.dataset.xresults.append(xvalues)
        self.dataset.yresults.append(yvalues)
        for sink in self._sinks:
            sink.addPoint(self.dataset, xvalues, yvalues)

    def finishPoint(self):
        session.endActionScope()
        session.breakpoint(2)

    def endScan(self):
        for sink in self._sinks:
            sink.endDataset(self.dataset)
        session.elog_event('scanend', self.dataset)
        session.breakpoint(1)

    def handleError(self, what, dev, val, err):
        """Handle an error occurring during positioning or readout for a point.

        This method can do several things:

        - re-raise the current exception to abort everything
        - raise `StopScan` to end the current scan with an error, but not
          raise an exception in the script
        - raise `SkipPoint` to skip current point and continue with next point
        - return: to ignore error and continue with current point
        """
        if isinstance(err, (PositionError, MoveError, TimeoutError)):
            # continue counting anyway
            if what == 'read':
                printwarning('Readout problem', exc=1)
            else:
                printwarning('Positioning problem, continuing', exc=1)
            return
        elif isinstance(err, (InvalidValueError, LimitError,
                              CommunicationError, ComputationError)):
            if what == 'read':
                printwarning('Readout problem', exc=1)
            else:
                printwarning('Skipping data point', exc=1)
                raise SkipPoint
        # would also be possible:
        # elif ...:
        #     raise StopScan
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
                self.handleError('move', dev, val, err)
            else:
                waitdevs.append((dev, val))
        for dev, val in waitdevs:
            try:
                dev.wait()
            except NicosError, err:
                self.handleError('wait', dev, val, err)

    def readPosition(self):
        # XXX read() or read(0)
        # using read() assumes all devices have updated cached value on wait()
        ret = []
        for dev in self._devices:
            try:
                val = dev.read()
            except NicosError, err:
                self.handleError('read', dev, None, err)
                val = [None] * len(dev.valueInfo())
            if isinstance(val, list):
                ret.extend(val)
            else:
                ret.append(val)
        return ret

    def readEnvironment(self, start, finished):
        # XXX take history mean, warn if values deviate too much?
        ret = []
        for dev in self._envlist:
            try:
                val = dev.read(0)
            except NicosError, err:
                self.handleError('read', dev, None, err)
                val = [None] * len(dev.valueInfo())
            if isinstance(val, list):
                ret.extend(val)
            else:
                ret.append(val)
        return ret

    def shortDesc(self):
        return 'Scan %s' % ', '.join(map(str, self._devices))

    def run(self):
        session.beginActionScope(self.shortDesc())
        try:
            self._inner_run()
        finally:
            session.endActionScope()

    def _inner_run(self):
        # move all devices to starting position before starting scan
        try:
            self.prepareScan(self._positions[0])
        except StopScan:
            return
        except SkipPoint:
            can_measure = False
        else:
            can_measure = True
        self.beginScan()
        try:
            for i, position in enumerate(self._positions):
                self.preparePoint(i+1, position)
                try:
                    if position:
                        session.action('Positioning')
                        if i != 0:
                            self.moveTo(position)
                        elif not can_measure:
                            continue
                    started = time.time()
                    actualpos = self.readPosition()
                    if self._multistep:
                        result = []
                        for i in range(self._mscount):
                            self.moveDevices(self._mswhere[i])
                            session.action('Counting (step %s)' % (i+1))
                            # XXX handle errors in _count
                            result.extend(_count(self._detlist, self._preset))
                    else:
                        session.action('Counting')
                        result = _count(self._detlist, self._preset)
                    finished = time.time()
                    actualpos += self.readEnvironment(started, finished)
                    self.addPoint(actualpos, result)
                except SkipPoint:
                    pass
                finally:
                    self.finishPoint()
        except StopScan:
            pass
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
        self._numsteps = numsteps
        if envlist is None:
            envlist = list(session.experiment.sampleenv)
        envlist.insert(0, self._etime)
        if numsteps < 0:
            steps = Repeater([])
        else:
            steps = [[]] * numsteps
        Scan.__init__(self, [], steps, firstmoves, multistep,
                      detlist, envlist, preset, scaninfo, scantype)

    def shortDesc(self):
        return 'Time scan'

    def readEnvironment(self, started, finished):
        ret = Scan.readEnvironment(self, started, finished)
        ret[0] = finished - self._started
        return ret

    def endScan(self):
        Scan.endScan(self)
        self._etime.shutdown()

    def preparePoint(self, num, xvalues):
        Scan.preparePoint(self, num, xvalues)
        if session.mode == 'simulation':
            self._sim_start = session.clock.time

    def finishPoint(self):
        Scan.finishPoint(self)
        if session.mode == 'simulation':
            if self._numsteps > 1:
                session.log.info('skipping %d steps...' % (self._numsteps - 1))
                duration = session.clock.time - self._sim_start
                session.clock.tick(duration * (self._numsteps - 1))
            elif self._numsteps < 0:
                session.log.info('would scan indefinitely, skipping...')
            raise StopScan


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
                result = _count(self._detlist, preset)
            finished = time.time()
            actualpos += self.readEnvironment(started, finished)
            self.addPoint(actualpos, result)
            return result
        except SkipPoint:
            pass
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
        if not isinstance(inst, TAS):
            raise NicosError('cannot do a Q scan, your instrument device '
                             'is not a triple axis device')
        Scan.__init__(self, [inst], positions,
                      firstmoves, multistep, detlist, envlist, preset,
                      scaninfo, scantype)
        self._envlist[0:0] = [inst._adevs['mono'], inst._adevs['ana'],
                              inst._adevs['psi'], inst._adevs['phi']]

    def shortDesc(self):
        return 'Qscan'

    def beginScan(self):
        if len(self._positions) > 1:
            # determine first varying index as the plotting index
            for i in range(4):
                if self._positions[0][0][i] != self._positions[1][0][i]:
                    self.dataset.xindex = i
                    self.dataset.xrange = (self._positions[0][0][i],
                                           self._positions[-1][0][i])
                    break
        Scan.beginScan(self)


class ContinuousScan(Scan):
    """
    Special scan class for scans with one axis moving continuously (used for
    peak search).
    """

    DELTA = 1.0

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

    def shortDesc(self):
        return 'Continuous scan %s' % self._devices[0]

    def run(self):
        device = self._devices[0]
        detlist = self._detlist
        try:
            self.prepareScan([self._startpos])
        except (StopScan, SkipPoint):
            return
        self.beginScan()
        original_speed = device.speed
        session.beginActionScope(self.shortDesc())
        try:
            device.speed = self._speed
            device.move(self._endpos)
            preset = max(abs(self._endpos - self._startpos) /
                         self._speed * 5, 3600)
            for det in detlist:
                det.start(t=preset)
            last = sum((det.read() for det in detlist), [])
            while device.status(0)[0] == status.BUSY:
                time.sleep(self.DELTA)
                session.breakpoint(2)
                devpos = device.read(0)
                read = sum((det.read() for det in detlist), [])
                diff = [read[i] - last[i]
                        if isinstance(read[i], (int, long, float)) else read[i]
                        for i in range(len(read))]
                self.dataset.curpoint += 1
                self.addPoint([devpos], diff)
                last = read
            for det in detlist:
                det.stop()
        finally:
            session.endActionScope()
            device.stop()
            device.speed = original_speed
            self.endScan()


class TwoDimScan(Scan):
    """
    Special scan class for two-dimensional scans.
    """

    def __init__(self, dev1, start1, step1, numsteps1,
                 dev2, start2, step2, numsteps2,
                 firstmoves=None, multistep=None, detlist=None,
                 envlist=None, preset=None, scaninfo=None):
        scantype = '2D'
        devices = [dev1, dev2]
        positions = []
        for i in range(numsteps1):
            dev1value = start1 + i*step1
            # move dev2 forward in one row, then move it back in the next row
            if i % 2 == 0:
                positions.extend([dev1value, start2 + j*step2]
                                 for j in range(numsteps2))
            else:
                positions.extend([dev1value, start2 + (numsteps2-j-1)*step2]
                                 for j in range(numsteps2))
        self._pointsperrow = numsteps1
        Scan.__init__(self, devices, positions, firstmoves, multistep,
                      detlist, envlist, preset, scaninfo, scantype)

    def preparePoint(self, num, xvalues):
        if num > 1 and (num-1) % self._pointsperrow == 0:
            for sink in self._sinks:
                sink.addBreak(self.dataset)
        Scan.preparePoint(self, num, xvalues)
