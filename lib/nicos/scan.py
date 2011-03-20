#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""Scan classes for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicos import session
from nicos.errors import NicosError, LimitError, FixedError
from nicos.device import Measurable
from nicos.commands.output import printwarning
from nicos.commands.measure import _count


INFO_CATEGORIES = [
    ('experiment', 'Experiment information'),
    ('sample', 'Sample and alignment'),
    ('instrument', 'Instrument setup'),
    ('offsets', 'Offsets'),
    ('limits', 'Limits'),
    ('status', 'Instrument status'),
    ('general', 'Instrument state at first scan point'),
]


class Scan(object):
    """
    Represents a general scan over some devices with a specified detector.
    """

    def __init__(self, devices, positions, firstmoves=None, multistep=None,
                 detlist=None, preset=None, scaninfo=None, scantype=None):
        if not detlist:
            detlist = session.instrument.detectors
        if multistep:
            nsteps = len(multistep[0][1])
            devices.extend(ms[0] for ms in multistep)
            positions = [dpos + [ms[1][i] for ms in multistep]
                         for dpos in positions for i in range(nsteps)]
        self.dataset = session.experiment.createDataset(scantype)
        self._movedevices = self.dataset.mdevices = devices
        self._readdevices = self.dataset.rdevices = []
        for dev in devices:
            self._readdevices.extend(dev.scanDevices())
        self._targets = self.dataset.positions = positions
        self._firstmoves = firstmoves
        self._detlist = self.dataset.detlist = detlist
        self._preset = self.dataset.preset = preset
        self.dataset.scaninfo = scaninfo
        self._sinks = self.dataset.sinks
        self._npoints = len(positions)

    def prepareScan(self):
        session.beginActionScope('Scan')
        session.action('Moving to start')
        can_measure = True
        # the move-before devices
        if self._firstmoves:
            can_measure = self.moveTo(self._firstmoves)
        # the scanned-over devices
        can_measure &= self.moveTo(zip(self._movedevices, self._targets[0]))
        return can_measure

    def beginScan(self):
        dataset = self.dataset
        dataset.points = []
        dataset.sinkinfo = []
        dataset.xnames, dataset.xunits = [], []
        for dev in self._readdevices:
            dataset.xnames.append(dev.name)
            dataset.xunits.append(dev.unit)
        dataset.ynames, dataset.yunits = [], []
        for det in dataset.detlist:
            names, units = det.valueInfo()
            dataset.ynames.extend(names)
            dataset.yunits.extend(units)
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

    def addPoint(self, xvalues, yvalues):
        self.dataset.points.append(xvalues + yvalues)
        for sink in self._sinks:
            sink.addPoint(self.dataset, xvalues, yvalues)

    def finishPoint(self):
        session.endActionScope()

    def endScan(self):
        for sink in self._sinks:
            sink.endDataset(self.dataset)
        session.endActionScope()

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

    def moveTo(self, where):
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

    def maybeMoveTo(self, where):
        """Like moveTo, but gets another tuple item that gives the last
        position.  If it equals the target position, do not move.
        """
        waitdevs = []
        for dev, val, prevval in where:
            if val != prevval:
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

    def run(self):
        # move all devices to starting position before starting scan
        can_measure = self.prepareScan()
        self.beginScan()
        prevpos = [None] * len(self._movedevices)
        try:
            for i, position in enumerate(self._targets):
                self.preparePoint(i+1, position)
                try:
                    session.action('Positioning')
                    if i > 0:
                        can_measure = self.maybeMoveTo(
                            zip(self._movedevices, position, prevpos))
                    if not can_measure:
                        continue
                    actualpos = [dev.read() for dev in self._readdevices]
                    session.action('Counting')
                    result = list(_count(self._detlist, self._preset))
                    self.addPoint(actualpos, result)
                    prevpos = position
                finally:
                    self.finishPoint()
        finally:
            self.endScan()
