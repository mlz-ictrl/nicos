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
        self.dataset = session.experiment.createDataset(scantype)
        self._devices = self.dataset.devices = devices
        self._targets = self.dataset.positions = positions
        self._multistep = self.dataset.multistep = multistep
        self._firstmoves = firstmoves
        self._detlist = self.dataset.detlist = detlist
        self._preset = self.dataset.preset = preset
        self.dataset.scaninfo = scaninfo
        self._sinks = self.dataset.sinks
        self._npoints = len(positions)

    def beginScan(self):
        session.beginActionScope('Scan')
        dataset = self.dataset
        dataset.points = []
        dataset.sinkinfo = []
        dataset.devunits = [dev.unit for dev in dataset.devices]
        dataset.devnames = [dev.name for dev in dataset.devices]
        dataset.valueinfo = [det.valueInfo() for det in self._detlist]
        dataset.detnames = []
        dataset.detunits = []
        for names, units in dataset.valueinfo:
            dataset.detnames.extend(names)
            dataset.detunits.extend(units)
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
        if isinstance(err, LimitError):
            printwarning('Skipping data point', exc=1)
            return False
        elif isinstance(err, FixedError):
            raise
        else:
            # consider all other errors to be fatal
            raise

    def moveTo(self, where):
        for dev, val in where:
            try:
                dev.start(val)
                dev.wait()
            except NicosError, err:
                # handleError can reraise for fatal error, return False to
                # skip this point and True to measure anyway
                return self.handleError(dev, val, err)
        return True

    def run(self):
        # move to first position before starting scan
        session.action('Moving to start')
        can_measure = True
        if self._firstmoves:
            can_measure = self.moveTo(self._firstmoves)
        can_measure &= self.moveTo(zip(self._devices, self._targets[0]))
        self.beginScan()
        try:
            for i, position in enumerate(self._targets):
                self.preparePoint(i+1, position)
                try:
                    session.action('Positioning')
                    if i > 0:
                        can_measure = self.moveTo(zip(self._devices, position))
                    if not can_measure:
                        continue
                    session.action('Counting')
                    # XXX add multistep action
                    result = _count(self._detlist, self._preset)
                    self.addPoint(position, result)
                finally:
                    self.finishPoint()
        finally:
            self.endScan()
