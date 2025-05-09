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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Scan classes, new API."""

from contextlib import contextmanager
from time import time as currenttime

from numpy import array_equal, ndarray

from nicos import session
from nicos.core import status
from nicos.core.acquire import CountResult, DevStatistics, acquire, \
    read_environment, stop_acquire_thread
from nicos.core.constants import FINAL, INTERMEDIATE, SIMULATION, SLAVE
from nicos.core.errors import LimitError, ModeError, NicosError, UsageError
from nicos.core.mixins import HasLimits
from nicos.core.params import Value
from nicos.core.utils import CONTINUE_EXCEPTIONS, SKIP_EXCEPTIONS, multiWait, \
    waitForCompletion
from nicos.protocols.daemon import BREAK_AFTER_LINE, BREAK_AFTER_STEP
from nicos.utils import Repeater, number_types


class SkipPoint(Exception):
    """Custom exception class to skip a scan point."""


class StopScan(Exception):
    """Custom exception class to stop the rest of the scan."""


class Scan:
    """
    Represents a general scan over some devices with specified detectors.
    """

    def __init__(self, devices, startpositions, endpositions=None,
                 firstmoves=None, multistep=None, detlist=None, envlist=None,
                 preset=None, scaninfo=None, subscan=False, xindex=None):
        if session.mode == SLAVE:
            raise ModeError('cannot scan in slave mode')
        self.dataset = None
        if detlist is None:
            detlist = session.experiment.detectors
            if not detlist:
                session.log.warning('scanning without detector, '
                                    'use SetDetectors() to select which '
                                    'detector(s) you want to use')
        # check preset names for validity
        # (XXX duplication with count() command!)
        if detlist and preset:
            names = set(preset)
            for det in detlist:
                names.difference_update(det.presetInfo())
            if names:
                session.log.warning('these preset keys were not recognized by '
                                    'any of the detectors: %s -- detectors are'
                                    ' %s', ', '.join(names),
                                    ', '.join(map(str, detlist)))
        if preset is None:
            preset = {}
        if not preset:
            for det in detlist:
                preset.update(det.preset())
        if envlist == []:
            # special value [] to suppress all envlist devices
            allenvlist = []
        else:
            allenvlist = session.experiment.sampleenv
            if envlist is not None:
                allenvlist.extend(dev for dev in envlist
                                  if dev not in allenvlist)
        self._firstmoves = firstmoves
        # convert multistep to device positions
        self._primary_devicesindex = len(devices)
        self._mscount = 1
        if multistep:
            self._mscount = mscount = len(multistep[0][1])
            mspos = [[multistep[i][1][j]
                      for i in range(len(multistep))]
                     for j in range(mscount)]
            for dev, _ in multistep:
                devices.append(dev)
            new_startpositions = []
            for pos in startpositions:
                for i in range(mscount):
                    new_startpositions.append(list(pos) + mspos[i])
            startpositions = new_startpositions
            if endpositions:
                new_endpositions = []
                for pos in endpositions:
                    for i in range(mscount):
                        new_endpositions.append(list(pos) + mspos[i])
                endpositions = new_endpositions
        self._devices = devices
        self._startpositions = startpositions
        self._endpositions = endpositions
        self._detlist = detlist
        self._envlist = allenvlist
        self._preset = preset or {}
        self._scaninfo = scaninfo
        self._subscan = subscan
        self._guessPlotIndex(xindex)
        self._chain = []
        self._chain_direction = None
        try:
            self._npoints = len(startpositions)  # can be zero if not known
        except TypeError:
            self._npoints = 0

    def _guessPlotIndex(self, xindex):
        if xindex is not None:
            self._xindex = xindex
            return
        self._xindex = 0
        if len(self._startpositions) <= self._mscount:
            return
        # iterate over devices (only primary scan devices)
        for j, dev in enumerate(self._devices[:self._primary_devicesindex]):
            valueInfo = dev.valueInfo()
            subvals = len(valueInfo)
            st0 = self._startpositions[0][j]
            st1 = self._startpositions[self._mscount][j]
            if isinstance(st0, ndarray):
                if not array_equal(st0, st1):
                    break
            elif st0 != st1:
                break
            # if the device has multiple values, use the first as default.
            self._xindex += subvals
        else:
            self._xindex = 0
        session.log.debug('using field %d as primary x-axis for plotting',
                          self._xindex)

    @contextmanager
    def pointScope(self, num):
        if self.dataset.npoints == 0:
            session.beginActionScope('Point %d' % num)
        else:
            session.beginActionScope('Point %d/%d' %
                                     (num, self.dataset.npoints))
        try:
            yield
        finally:
            session.endActionScope()

    def prepareScan(self, position):
        # XXX with actionscope
        session.beginActionScope('Moving to start')
        try:
            # the move-before devices
            if self._firstmoves:
                fm_devs, fm_pos = zip(*self._firstmoves)
                self.moveDevices(fm_devs, fm_pos)
            # the scanned-over devices
            self.moveDevices(self._devices, position)
        finally:
            session.endActionScope()

    def beginScan(self):
        self.dataset = session.experiment.data.beginScan(
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
            chain=self._chain,
            chain_direction=self._chain_direction,
        )
        session.elogEvent('scanbegin', self.dataset)

    def preparePoint(self, num, xvalues):
        # called before moving to current scanpoint
        pass

    def finishPoint(self):
        session.breakpoint(BREAK_AFTER_STEP)

    def endScan(self):
        session.experiment.data.finishScan()
        try:
            from nicos.core.data import ScanData
            session.elogEvent('scanend', ScanData(self.dataset))
        except Exception:
            session.log.debug('could not add scan to electronic logbook',
                              exc=1)
        session.breakpoint(BREAK_AFTER_LINE)

    def handleError(self, what, err):
        """Handle an error occurring during positioning or readout for a point.

        This method can do several things:

        - re-raise the current exception to abort everything
        - raise `StopScan` to end the current scan with an error, but not
          raise an exception in the script
        - raise `SkipPoint` to skip current point and continue with next point
        - return: to ignore error and continue with current point
        """
        if isinstance(err, CONTINUE_EXCEPTIONS):
            # continue counting anyway
            if what == 'read':
                session.log.warning('Readout problem', exc=1)
            elif what == 'count':
                session.log.warning('Counting problem', exc=1)
            elif what == 'prepare':
                session.log.warning('Prepare problem, skipping point', exc=1)
                # no point in measuring this point in any case
                raise SkipPoint
            else:
                session.log.warning('Positioning problem, continuing', exc=1)
            return
        elif isinstance(err, SKIP_EXCEPTIONS):
            if what == 'read':
                session.log.warning('Readout problem', exc=1)
            elif what == 'count':
                session.log.warning('Counting problem', exc=1)
                # point is already skipped, no need to raise...
            elif what == 'prepare':
                session.log.warning('Prepare problem, skipping point', exc=1)
                raise SkipPoint
            else:
                session.log.warning('Skipping data point', exc=1)
                raise SkipPoint
        # would also be possible:
        # elif ...:
        #     raise StopScan
        else:
            # consider all other errors to be fatal
            # XXX raise NicosError ?
            raise  # pylint: disable=misplaced-bare-raise

    def moveDevices(self, devices, positions, wait=True):
        """Move a given list of *devices* to the given list of *positions*.
        On errors, call handleError, which decides when the scan may continue.

        If *wait* is true, returns ``{devname: (None, final position)}``.
        This is intended to be given to `DataManager.putValues` which expects
        ``{devname: (timestamp or None, value)}``.  Else ``None``.
        """
        skip = None
        waitdevs = []
        for dev, val in zip(devices, positions):
            try:
                dev.start(val)
            except NicosError as err:
                try:
                    # handleError can reraise for fatal error, raise SkipPoint
                    # to skip this point or return to measure anyway
                    self.handleError('move', err)
                except SkipPoint:
                    skip = True
            else:
                waitdevs.append(dev)
        if not wait:
            return None
        waitresults = {}

        try:
            # remember the read values so they can be used for the data point
            for (dev, value) in multiWait(waitdevs).items():
                # (None, value): None identifies the 'main' value
                waitresults[dev.name] = (None, value)
        except NicosError as err:
            self.handleError('wait', err)

        if skip:
            raise SkipPoint

        for dev in waitdevs:
            # if devices failed to move but we continue, get some read values
            if dev.name in waitresults:
                continue
            try:
                waitresults[dev.name] = (None, dev.read())
            except NicosError:
                dev.log.warning('Readout problem, continuing', exc=1)
                waitresults[dev.name] = (None, [None] * len(dev.valueInfo()))

        return waitresults

    def readPosition(self):
        actualpos = {}
        try:
            # remember the read values so that they can be used for the
            # data point
            for dev in self._devices:
                actualpos[dev.name] = (None, dev.read(0))
        except NicosError as err:
            self.handleError('read', err)
            # XXX(dataapi): at least read the remaining devs?
        return actualpos

    def shortDesc(self):
        if self.dataset and self.dataset.counter > 0:
            return 'Scan %s #%s' % (','.join(map(str, self._devices)),
                                    self.dataset.counter)
        return 'Scan %s' % ','.join(map(str, self._devices))

    def run(self):
        if not self._subscan and (getattr(session, '_currentscan', None) or
                                  getattr(session, '_manualscan', None)):
            raise NicosError('cannot start scan while another scan is running')
        # stop previous inner_count / acquisition thread if available
        stop_acquire_thread()

        session._currentscan = self
        # XXX(dataapi): this is too early, dataset has no number yet
        session.beginActionScope(self.shortDesc())
        try:
            self._inner_run()
        finally:
            session.endActionScope()
            session._currentscan = None
        return self.dataset

    def readEnvironment(self):
        read_environment(self._envlist)

    def acquireCompleted(self):
        """Stops the internal acquire loop when returning `True`. Overwrite
        this method e.g. to finish acquisition when the scanned axis has
        finished movement although the preset has not yet been fulfilled.

        """
        return False

    def acquire(self, point, preset):
        preset.pop('live', None)
        acquire(point, preset, iscompletefunc=self.acquireCompleted)

    def _inner_run(self):
        dataman = session.experiment.data
        # move all devices to starting position before starting scan
        skip_first_point = False
        if self._startpositions:
            try:
                self.prepareScan(self._startpositions[0])
            except StopScan:
                return
            except SkipPoint:
                skip_first_point = True
        # if the scan was already aborted, we haven't started writing
        self.beginScan()
        try:
            for i, position in enumerate(self._startpositions):
                with self.pointScope(i + 1):
                    try:
                        self.preparePoint(i + 1, position)
                        if i == 0 and skip_first_point:
                            continue
                        waitresults = self.moveDevices(self._devices, position,
                                                       wait=True)
                        # start moving to end positions
                        if self._endpositions:
                            self.moveDevices(self._devices,
                                             self._endpositions[i], wait=False)
                    except SkipPoint:
                        session.breakpoint(BREAK_AFTER_STEP)
                        continue
                    except BaseException as err:
                        try:
                            self.finishPoint()
                        except Exception:
                            session.log.exception('could not finish point')
                        raise err
                    try:
                        # measure...
                        # XXX(dataapi): is target= needed?
                        point = dataman.beginPoint(target=position,
                                                   preset=self._preset)
                        dataman.putValues(waitresults)
                        self.readEnvironment()
                        try:
                            self.acquire(point, self._preset)
                        finally:
                            dataman.finishPoint()
                    except NicosError as err:
                        self.handleError('count', err)
                    except SkipPoint:
                        pass
                    finally:
                        self.finishPoint()
        except StopScan:
            pass
        finally:
            self.endScan()


class ElapsedTime(DevStatistics):
    statname = 'elapsedtime'
    started = 0

    def __init__(self, name):
        DevStatistics.__init__(self, None)
        self.devname = name

    def retrieve(self, *ignored):
        return currenttime() - self.started

    def valueInfo(self):
        return (Value('etime', unit='s', fmtstr='%.1f'),)


class SweepScan(Scan):
    """
    Special scan class for "sweeps" (i.e., start device(s) and scan until they
    arrive at their targets.)  The number of points, if > 0, is a maximum of
    points, after which the scan will stop.

    If no devices are given, acts as a "time scan", i.e. just counts the given
    number of points (or indefinitely) with an elapsed time counter.
    """

    def __init__(self, devices, startend, numpoints, firstmoves=None,
                 multistep=None, detlist=None, envlist=None, preset=None,
                 scaninfo=None, subscan=False, xindex=None):
        self._etime = ElapsedTime('SweepScan')
        # for sweeps the dry run usually shows only one step; in the case of
        # multisteps we take the first N
        self._simpoints = 1
        self._numpoints = numpoints
        if multistep:
            self._simpoints = len(multistep[0][1])
            self._numpoints = numpoints * self._simpoints
        self._sweepdevices = devices
        if numpoints < 0:
            points = Repeater([])
        else:
            points = [[]] * numpoints
        # start for sweep devices are "firstmoves"
        firstmoves = firstmoves or []
        self._sweeptargets = []
        for dev, (start, end) in zip(devices, startend):
            if start is not None:
                firstmoves.append((dev, start))
            self._sweeptargets.append(end)
        # sweep scans support a special "delay" and "minstep" presets
        self._delay = preset.pop('delay', 0)
        self._minstep = preset.pop('minstep', 0)
        if not isinstance(self._minstep, list):
            self._minstep = [self._minstep] * len(devices)
        elif len(self._minstep) != len(devices):
            raise UsageError('Invalid number of minstep values. For each '
                             'device a minstep value must be given!')
        Scan.__init__(self, [], points, [], firstmoves, multistep,
                      detlist, envlist, preset, scaninfo, subscan, xindex)
        # XXX(dataapi): devices should be in devlist, not envlist
        if not devices:
            self._envlist.insert(0, self._etime)
        else:
            for dev in devices[::-1]:
                if dev in self._envlist:
                    self._envlist.remove(dev)
                self._envlist.insert(0, dev)

    def shortDesc(self):
        if not self._sweepdevices:
            stype = 'Time scan'
        else:
            stype = 'Sweep %s' % ','.join(map(str, self._sweepdevices))
        if self.dataset and self.dataset.counter > 0:
            return '%s #%s' % (stype, self.dataset.counter)
        return stype

    def preparePoint(self, num, xvalues):
        if session.mode == SIMULATION and num > self._simpoints:
            session.log.info('skipping %d points...',
                             self._numpoints - self._simpoints)
            duration = session.clock.time - self._sim_start
            session.clock.tick(duration * (self._numpoints -
                                           self._simpoints))
            if self._numpoints < 0 and not self._sweepdevices:
                session.log.info('would scan indefinitely, skipping...')
            raise StopScan
        if num == 1:
            self._etime.started = currenttime()
            if self._sweeptargets:
                try:
                    self.moveDevices(self._sweepdevices, self._sweeptargets,
                                     wait=False)
                except SkipPoint:
                    raise StopScan  # pylint:disable=raise-missing-from
            if self._minstep:
                self._laststep = [dev.read() for dev in self._sweepdevices]
        else:
            if self._delay:
                # wait between points, but only from the second point on
                session.action('Delay')
                session.delay(self._delay)
            if self._sweepdevices and self._minstep:
                # wait until next step
                while True:
                    position = [dev.read() for dev in self._sweepdevices]
                    l = list(zip(self._laststep, position, self._minstep))
                    if any(abs(x-y) > z for x,y,z in l):
                        break
                    if not any(dev.status()[0] == status.BUSY
                               for dev in self._sweepdevices):
                        break
                self._laststep = [(x + z if x < y else x - z) for x,y,z in l]
        Scan.preparePoint(self, num, xvalues)
        if session.mode == SIMULATION:
            self._sim_start = session.clock.time

    def finishPoint(self):
        Scan.finishPoint(self)
        if self._sweepdevices:
            if not any(dev.status()[0] == status.BUSY
                       for dev in self._sweepdevices):
                if session.mode == SIMULATION:
                    for dev in self._sweepdevices:
                        dev.wait()
                raise StopScan


class ContinuousScan(Scan):
    """
    Special scan class for scans with one axis moving continuously (used for
    peak search).
    """

    def __init__(self, device, start, end, speed, timedelta=None,
                 firstmoves=None, detlist=None, envlist=None, scaninfo=None,
                 xindex=None):

        self._speed = device.speed / 5. if speed is None else speed
        self._timedelta = timedelta or 1.0

        Scan.__init__(self, [device], [[start]], [[end]], firstmoves, None,
                      detlist, envlist, None, scaninfo, xindex)

    def shortDesc(self):
        if self.dataset and self.dataset.counter > 0:
            return 'Continuous scan %s #%s' % (self._devices[0],
                                               self.dataset.counter)
        return 'Continuous scan %s' % self._devices[0]

    def beginScan(self):
        device = self._devices[0]
        self._original_speed = device.speed
        device.speed = self._speed
        Scan.beginScan(self)

    def endScan(self):
        device = self._devices[0]
        device.speed = self._original_speed
        Scan.endScan(self)

    def acquire(self, point, preset):
        pass

    def prepareScan(self, position):
        device = self._devices[0]
        start, end = self._startpositions[0][0], self._endpositions[0][0]
        self._distance = abs(end - start)
        direction = int(end > start)  # 1 if positive, 0 if negative

        ok, why = device.isAllowed(start)
        if not ok:
            if isinstance(device, HasLimits):
                start = device.userlimits[1 - direction]
                ok, why = device.isAllowed(start)
                if ok:
                    self._startpositions[0][0] = start
                    session.log.warning('Scan start restricted to limits (%s)',
                                        device.format(start, unit=True))
            if not ok:
                raise LimitError('Cannot move to start value for %s: %s' %
                                 (device, why))
        ok, why = device.isAllowed(end)
        if not ok:
            if isinstance(device, HasLimits):
                end = device.userlimits[direction]
                ok, why = device.isAllowed(end)
                if ok:
                    self._endpositions[0][0] = end
                    session.log.warning('Scan end restricted to limits (%s)',
                                        device.format(end, unit=True))
            if not ok:
                raise LimitError('Cannot move to end value for %s: %s' %
                                 (device, why))
        Scan.prepareScan(self, position)

        # guess the number of points
        self._npoints = int(self._distance / self._speed / self._timedelta) + 1

    def _calculate_diff(self, last, current):
        res = {}
        for (detname, (vals, images)) in current.items():
            values = [val - last[detname][0][i]
                      if isinstance(val, number_types) else val
                      for i, val in enumerate(vals)]
            imgs = [image - last[detname][1][i]
                    if (image is not None and last[detname][1][i] is not None)
                    else None
                    for i, image in enumerate(images)]
            res[detname] = (values, imgs)
        return res

    def _inner_run(self):
        try:
            self.prepareScan(self._startpositions[0])
        except (StopScan, SkipPoint, LimitError):
            return

        dataman = session.experiment.data
        self.beginScan()

        device = self._devices[0]
        detlist = self._detlist
        point = 0
        try:
            if session.mode == SIMULATION:
                preset = 1  # prevent all contscans taking 1 hour
            else:
                preset = max(self._distance / (self._speed or 0.1) * 5, 3600)

            devpos = device.read(0)

            self.preparePoint(None, None)

            for det in detlist:
                det.prepare()
            for det in detlist:
                waitForCompletion(det)
            for det in detlist:
                det.start(t=preset)
            device.move(self._endpositions[0][0])
            starttime = looptime = currenttime()

            last = {det.name: (det.read(), det.readArrays(INTERMEDIATE))
                    for det in detlist}

            while device.status(0)[0] == status.BUSY:
                session.breakpoint(BREAK_AFTER_STEP)
                sleeptime = max(0, looptime + self._timedelta - currenttime())
                session.log.debug('sleep time: %f', sleeptime)
                with self.pointScope(point + 1):
                    session.delay(sleeptime)
                    looptime = currenttime()
                    new_devpos = device.read(0)
                    read = {det.name: (det.read(),
                                       det.readArrays(INTERMEDIATE))
                            for det in detlist}
                    actualpos = [0.5 * (devpos + new_devpos)]
                    dataman.beginTemporaryPoint()
                    if point == 0:
                        dataman.updateMetainfo()
                    dataman.putValues({device.name: (None, actualpos)})
                    self.readEnvironment()
                    # TODO: if the data sink needs it ?
                    # dataman.updateMetainfo()
                    dataman.putResults(FINAL, self._calculate_diff(last, read))
                    dataman.finishPoint()
                    last = read
                    devpos = new_devpos
                    for det in detlist:
                        det.duringMeasureHook(looptime - starttime)
                    point += 1
            device.wait()  # important for simulation
        finally:
            session.endActionScope()
            for det in detlist:
                try:
                    det.finish()
                except Exception:
                    session.log.warning('could not stop %s', det, exc=1)
            try:
                device.stop()
                device.wait()
            except Exception:
                device.log.warning('could not stop %s', device, exc=1)
            self.endScan()


class ManualScan(Scan):
    """
    Special scan class for "manual" scans.
    """

    def __init__(self, firstmoves=None, multistep=None, detlist=None,
                 envlist=None, preset=None, scaninfo=None, subscan=False,
                 xindex=None):
        # put mentioned envlist devices first in envlist (usually the desired
        # X-axis is among them)
        envlist = envlist or []
        envlist.extend(dev for dev in session.experiment.sampleenv
                       if dev not in envlist)
        Scan.__init__(self, [], Repeater([]), Repeater([]), firstmoves,
                      None, detlist, envlist, preset, scaninfo,
                      subscan, xindex)
        self._envlist = envlist
        self._multistep = multistep
        if multistep:
            for dev, _ in multistep:
                self._devices.append(dev)
            self._mscount = len(multistep[0][1])
            self._mspos = [[multistep[i][1][j]
                            for i in range(len(multistep))]
                           for j in range(self._mscount)]
        self._curpoint = 0

    def manualBegin(self):
        session.beginActionScope('Scan')
        self.beginScan()

    def manualEnd(self):
        session.endActionScope()
        self.endScan()

    def step(self, **preset):
        if not self._multistep:
            return self._step_inner(preset)
        else:
            results = []
            for i in range(self._mscount):
                self.moveDevices(self._devices, self._mspos[i])
                results.append(self._step_inner(preset))
            return results

    def _step_inner(self, preset):
        dataman = session.experiment.data
        preset = preset or self._preset
        self.dataset.preset = preset
        self._curpoint += 1
        self.preparePoint(self._curpoint, [])
        try:
            point = dataman.beginPoint()
            point.preset = preset
            actualpos = self.readPosition()
            dataman.putValues(actualpos)
            try:
                acquire(point, preset)
            finally:
                self.readEnvironment()
                dataman.finishPoint()
        except SkipPoint:
            pass
        finally:
            self.finishPoint()
        return CountResult.from_point(point)[0]


class QScan(Scan):
    """
    Special scan class for scans with a triple axis instrument in Q/E space.
    """

    def __init__(self, positions, firstmoves=None, multistep=None,
                 detlist=None, envlist=None, preset=None, scaninfo=None,
                 subscan=False):
        from nicos.devices.tas import TAS
        inst = session.instrument
        if not isinstance(inst, TAS):
            raise NicosError('cannot do a Q scan, your instrument device '
                             'is not a triple axis device')
        self._xindex = 0
        Scan.__init__(self, [inst], positions, [],
                      firstmoves, multistep, detlist, envlist, preset,
                      scaninfo, subscan)
        if inst.scanmode == 'DIFF':
            self._envlist[0:0] = [inst._attached_mono,
                                  inst._attached_psi, inst._attached_phi]
        else:
            self._envlist[0:0] = [inst._attached_mono, inst._attached_ana,
                                  inst._attached_psi, inst._attached_phi]
        if inst in self._envlist:
            self._envlist.remove(inst)

    def shortDesc(self):
        comps = []
        if len(self._startpositions) > 1:
            for i in range(4):
                if self._startpositions[0][0][i] != \
                   self._startpositions[1][0][i]:
                    comps.append('HKLE'[i])
        if self.dataset and self.dataset.counter > 0:
            return 'Scan %s #%s' % (','.join(comps) or 'Q',
                                    self.dataset.counter)
        return 'Scan %s' % (','.join(comps) or 'Q')

    def _guessPlotIndex(self, _xindex):
        if len(self._startpositions) > 1:
            # determine first varying index as the plotting index
            for i in range(4):
                if self._startpositions[0][0][i] != \
                   self._startpositions[1][0][i]:
                    self._xindex = i
                    break
