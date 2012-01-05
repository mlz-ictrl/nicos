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

"""NICOS test suite utilities."""

__version__ = "$Revision$"

from nose.tools import assert_raises

from nicos.core import Moveable, HasLimits, status
from nicos.data import DataSink


def raises(exc, *args, **kwds):
    assert_raises(exc, *args, **kwds)
    return True


class TestDevice(HasLimits, Moveable):

    def doInit(self):
        self._value = 0
        self._start_exception = None
        self._read_exception = None
        self._status_exception = None

    def doRead(self):
        if self._read_exception:
            raise self._read_exception
        return self._value

    def doStart(self, target):
        if self._start_exception and target != 0:
            raise self._start_exception
        self._value = target

    def doWait(self):
        return self._value

    def doStatus(self):
        if self._status_exception:
            raise self._status_exception
        return status.OK, 'fine'


class TestSink(DataSink):

    def doInit(self):
        self.clear()

    def clear(self):
        self._calls = []
        self._info = []
        self._points = []

    def prepareDataset(self, dataset):
        self._calls.append('prepareDataset')

    def beginDataset(self, dataset):
        self._calls.append('beginDataset')

    def addInfo(self, dataset, category, valuelist):
        self._calls.append('addInfo')
        self._info.extend(valuelist)

    def addPoint(self, dataset, xvalues, yvalues):
        self._calls.append('addPoint')
        self._points.append(xvalues + yvalues)

    def addBreak(self, dataset):
        self._calls.append('addBreak')

    def endDataset(self, dataset):
        self._calls.append('endDataset')
