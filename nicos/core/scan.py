#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""Scan classes, new API."""

from time import time as currenttime
from contextlib import contextmanager

from nicos.commands.output import printwarning

from nicos import session
from nicos.core.errors import CommunicationError, ComputationError, \
    InvalidValueError, LimitError, ModeError, MoveError, NicosError, \
    PositionError, TimeoutError
from nicos.core.constants import SLAVE
from nicos.core.utils import waitForStatus, multiWait
from nicos.core.data import dataman
from nicos.pycompat import iteritems
from nicos.commands.measure import acquire


# Exceptions at which a scan point is measured anyway.
CONTINUE_EXCEPTIONS = (PositionError, MoveError, TimeoutError)
# Exceptions at which a scan point is skipped.
SKIP_EXCEPTIONS = (InvalidValueError, LimitError, CommunicationError,
                   ComputationError)


class SkipPoint(Exception):
    """Custom exception class to skip a scan point."""


class StopScan(Exception):
    """Custom exception class to stop the rest of the scan."""


class Scan(object):
    """
    Represents a general scan over some devices with specified detectors.
    """

    def __init__(self, devices, startpositions, endpositions=None,
                 firstmoves=None, multistep=None, detlist=None, envlist=None,
                 preset=None, scaninfo=None, subscan=False):
        if session.mode == SLAVE:
            raise ModeError('cannot scan in slave mode')
        self.dataset = None
        if not detlist:
            detlist = session.experiment.detectors
        if not detlist:
            printwarning('scanning without detector, use SetDetectors() '
                         'to select which detector(s) you want to use')
        # check preset names for validity (XXX duplication with count() command!)
        elif preset:
            names = set(preset)
            for det in detlist:
                names.difference_update(det.presetInfo())
            if names:
                printwarning('these preset keys were not recognized by any of '
                             'the detectors: %s -- detectors are %s' %
                             (', '.join(names), ', '.join(map(str, detlist))))
        if envlist == []:
            # special value [] to suppress all envlist devices
            allenvlist = []
        else:
            allenvlist = session.experiment.sampleenv
            if envlist is not None:
                allenvlist.extend(dev for dev in envlist if dev not in allenvlist)
        self._firstmoves = firstmoves
        # convert multistep to device positions
        if multistep:
            mscount = len(multistep[0][1])
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
        try:
            self._npoints = len(startpositions)  # can be zero if not known
        except TypeError:
            self._npoints = 0

    @contextmanager
    def pointScope(self, num):
        if self.dataset.npoints == 0:
            session.beginActionScope('Point %d' % num)
        else:
            session.beginActionScope('Point %d/%d' % (num,
                                                      self.dataset.npoints))
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
        self.dataset = dataman.beginScan(
            subscan=self._subscan,
            devices=self._devices,
            environment=self._envlist,
            detectors=self._detlist,
            info=self._scaninfo,
            npoints=self._npoints,
            startpositions=self._startpositions,
            endpositions=self._endpositions,
        )
        session.elogEvent('scanbegin', self.dataset)

    def preparePoint(self, num, xvalues):
        # called before moving to current scanpoint
        # XXX prepare
        try:
            for det in self._detlist:
                # preparation before count command
                det.prepare()
            # wait for preparation has been finished.
            for det in self._detlist:
                waitForStatus(det)
        except NicosError as err:
            self.handleError('prepare', err)

    def finishPoint(self):
        session.breakpoint(2)

    def endScan(self):
        dataman.finishScan()
        try:
            session.elogEvent('scanend', self.dataset)
        except Exception:
            session.log.debug('could not add scan to electronic logbook', exc=1)
        session.breakpoint(1)

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
                printwarning('Readout problem', exc=1)
            elif what == 'count':
                printwarning('Counting problem', exc=1)
            elif what == 'prepare':
                printwarning('Prepare problem, skipping point', exc=1)
                # no point in measuring this point in any case
                raise SkipPoint
            else:
                printwarning('Positioning problem, continuing', exc=1)
            return
        elif isinstance(err, SKIP_EXCEPTIONS):
            if what == 'read':
                printwarning('Readout problem', exc=1)
            elif what == 'count':
                printwarning('Counting problem', exc=1)
                # point is already skipped, no need to raise...
            elif what == 'prepare':
                printwarning('Prepare problem, skipping point', exc=1)
                raise SkipPoint
            else:
                printwarning('Skipping data point', exc=1)
                raise SkipPoint
        # would also be possible:
        # elif ...:
        #     raise StopScan
        else:
            # consider all other errors to be fatal
            # XXX raise NicosError ?
            raise  # pylint: disable=misplaced-bare-raise

    def moveDevices(self, devices, positions, wait=True):
        """Move to *where*, which is a list of (dev, position) tuples.
        On errors, call handleError, which decides when the scan may continue.

        Returns a dictionary mapping devices to timestamp and final positions
        if *wait* is True, and None otherwise.
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
            return
        waitresults = {}
        try:
            # remember the read values so that they can be used for the data point
            for (dev, value) in iteritems(multiWait(waitdevs)):
                waitresults[dev.name] = (currenttime(), value)
        except NicosError as err:
            self.handleError('wait', err)
            # XXX: at least read the remaining devs?
        if skip:
            raise SkipPoint
        return waitresults

    # XXX: move to data manager
    def readEnvironment(self):
        values = {}
        for dev in self._envlist:
            try:
                # XXX
                #if isinstance(dev, DevStatistics):
                #    val = dev.read(point.started, currenttime())
                #else:
                val = dev.read(0)
            except NicosError as err:
                self.handleError('read', err)
                val = [None] * len(dev.valueInfo())
            values[dev.name] = (currenttime(), val)
        dataman.putValues(values)

    def shortDesc(self):
        if self.dataset and self.dataset.counter > 0:
            return 'Scan %s #%s' % (','.join(map(str, self._devices)),
                                    self.dataset.counter)
        return 'Scan %s' % ','.join(map(str, self._devices))

    def run(self):
        if not self._subscan and getattr(session, '_currentscan', None):
            raise NicosError('cannot start scan while another scan is running')
        session._currentscan = self
        # XXX(dataapi): this is too early, dataset has no number yet
        session.beginActionScope(self.shortDesc())
        try:
            self._inner_run()
        finally:
            session.endActionScope()
            session._currentscan = None
        return self.dataset

    def acquire(self, point, preset):
        acquire(point, preset)

    def _inner_run(self):
        # move all devices to starting position before starting scan
        try:
            self.prepareScan(self._startpositions[0])
            skip_first_point = False
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
                        continue
                    except:
                        self.finishPoint()
                        raise
                    try:
                        # measure...
                        point = dataman.beginPoint(target=position)
                        dataman.putValues(waitresults)
                        try:
                            self.acquire(point, self._preset)
                        finally:
                            # read environment at least once
                            self.readEnvironment()
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


class SweepScan(Scan):
    pass


class ContinuousScan(Scan):
    pass


class ManualScan(Scan):
    pass


class QScan(Scan):
    pass
