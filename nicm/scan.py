#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Scan classes for NICOS
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Scan classes for NICOS."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from nicm import nicos
from nicm.device import Measurable
from nicm.errors import NicmError, LimitError, FixedError
from nicm.commands.output import printwarning
from nicm.commands.measure import _count


class Scan(object):
    """
    Represents a general scan over some devices with a specified detector.
    """

    def __init__(self, devices, positions, detlist=None, preset=None,
                 scaninfo=None, scantype=None):
        if detlist is None:
            # XXX better default
            detlist = [nicos.getDevice('det', Measurable)]
        self.devices = devices
        self.positions = positions
        self.detlist = detlist
        self.preset = preset
        self.scaninfo = scaninfo
        self.sinks = nicos.system.storage.getSinks(scantype)

    def beginScan(self):
        nicos.beginActionScope('Scan')
        sinkinfo = []
        for sink in self.sinks:
            sinkinfo.extend(sink.prepareDataset())
        for sink in self.sinks:
            sink.beginDataset(self.devices, self.positions, self.detlist,
                              self.preset, self.scaninfo, sinkinfo)
        # XXX add category, sort by that
        category = ''
        for name, device in sorted(nicos.devices.iteritems()):
            values = device.info()
            for sink in self.sinks:
                sink.addInfo(category, name, values)

    def preparePoint(self, num, xvalues):
        nicos.action('Point %d' % num)

    def addPoint(self, num, xvalues, yvalues):
        for sink in self.sinks:
            sink.addPoint(num, xvalues, yvalues)

    def endScan(self):
        for sink in self.sinks:
            sink.endDataset()
        nicos.endActionScope()

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
            except NicmError, err:
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
