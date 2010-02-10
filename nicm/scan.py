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
from nicm.errors import NicmError, LimitError, FixedError
from nicm.commands.output import printwarning


class Scan(object):
    """
    Represents a scan over some devices.
    """
    def __init__(self, devices, positions, detector, preset=None,
                 scantype=None):
        self.devices = devices
        self.positions = positions
        self.detector = detector
        self.preset = preset
        self.sinks = nicos.get_system_device().getStorage().getSinks(scantype)

    def beginScan(self):
        for sink in self.sinks:
            sink.beginDataset(self.devices, self.detector, self.preset)

    def addPoint(self, position, counts):
        for sink in self.sinks:
            sink.addPoint(position, counts)

    def endScan(self):
        for sink in self.sinks:
            sink.endDataset()

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
        self.beginScan()
        try:
            for position in self.positions:
                if self.moveTo(self.devices, position):
                    self.detector.start(self.preset)
                    self.detector.wait()
                    self.addPoint(position, self.detector.read())
        finally:
            self.endScan()
