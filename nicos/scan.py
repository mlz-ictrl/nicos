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

    def __init__(self, devices, positions, detlist=None, preset=None,
                 scaninfo=None, scantype=None):
        if detlist is None:
            detlist = session.system.instrument.detectors
        self.devices = devices
        self.positions = positions
        self.detlist = detlist
        self.preset = preset
        self.scaninfo = scaninfo
        self.sinks = session.system.getSinks(scantype)
        self._npoints = len(self.positions)

    def beginScan(self):
        session.beginActionScope('Scan')
        sinkinfo = []
        for sink in self.sinks:
            sinkinfo.extend(sink.prepareDataset())
        for sink in self.sinks:
            sink.beginDataset(self.devices, self.positions, self.detlist,
                              self.preset, self.scaninfo, sinkinfo)
        bycategory = {}
        for name, device in sorted(session.devices.iteritems()):
            if device.lowlevel:
                continue
            for category, key, value in device.info():
                bycategory.setdefault(category, []).append((device, key, value))
        for catname, catinfo in INFO_CATEGORIES:
            if catname not in bycategory:
                continue
            for sink in self.sinks:
                sink.addInfo(catinfo, bycategory[catname])

    def preparePoint(self, num, xvalues):
        session.action('Point %d/%d' % (num, self._npoints))

    def addPoint(self, num, xvalues, yvalues):
        for sink in self.sinks:
            sink.addPoint(num, xvalues, yvalues)

    def endScan(self):
        for sink in self.sinks:
            sink.endDataset()
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

    def moveTo(self, devices, values):
        for dev, val in zip(devices, values):
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
        can_measure = self.moveTo(self.devices, self.positions[0])
        self.beginScan()
        try:
            for i, position in enumerate(self.positions):
                self.preparePoint(i+1, position)
                if i > 0:
                    can_measure = self.moveTo(self.devices, position)
                if not can_measure:
                    continue
                result = _count(self.detlist, self.preset)
                self.addPoint(i+1, position, result)
        finally:
            self.endScan()
