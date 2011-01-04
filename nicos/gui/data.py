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

"""NICOS GUI data handler class."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import copy

from PyQt4.QtCore import *

import numpy as np

X = 0
Y = 1
Z = 2
DX = 3
DY = 4
FIRST_NORM = 5


class DataError(Exception):
    pass


class Curve(list):
    def __init__(self, name, coldesc, plotmode, data=None):
        self.name = name
        self.coldesc = coldesc
        self.plotmode = plotmode

        self.has_dx = False
        self.has_dy = False
        self.n_norm = 0
        self.colnames = []
        self.modes = set()

        # default to #columns, which is the dummy entry at the end of each point
        xindex = yindex = dxindex = dyindex = zindex = len(coldesc)
        normindices = []
        otherindices = []
        colnames = []
        for n, column in enumerate(coldesc):
            try:
                usage, name = column.split(':', 1)
            except ValueError:
                usage = column
                name = ''
            usage = usage.lower()
            if usage == 'x':
                xindex = n
            elif usage == 'y':
                yindex = n
            elif usage == 'z':
                zindex = n
            elif usage == 'dx':
                dxindex = n
                self.has_dx = True
            elif usage == 'dy':
                dyindex = n
                self.has_dy = True
            elif usage == 'norm':
                normindices.append(n)
                self.n_norm += 1
            else:
                otherindices.append(n)
            colnames.append(name)

        self.modes.update(mode.lower() for mode in plotmode.split(','))

        self.choicearr = np.array([xindex, yindex, zindex, dxindex, dyindex]
                                  + normindices + otherindices)
        self.colnames = self.choicearr.choose(colnames + [''])
        self.nvalues = len(self.choicearr)

        if data is not None:
            self.data = np.zeros((len(data), self.nvalues))
            for j, values in enumerate(data):
                self.data[j] = self.choicearr.choose(values)
        else:
            self.data = np.zeros((0, self.nvalues))

    def add_point(self, values):
        assert len(values) == len(self.coldesc) + 1
        # bring them in the right order
        values = self.choicearr.choose(values)
        self.data = np.resize(self.data, (len(self.data)+1, self.nvalues))
        self.data[-1] = values

    def copy(self):
        return copy.copy(self)


class DataSet(QObject):
    def __init__(self, num, title, subtitle='',
                 name='', filename='', comments='',
                 xaxisname='', yaxisname='', y2axisname='',
                 xscale=(0, 0), yscale=(0, 0), y2scale=(0, 0)):
        QObject.__init__(self)

        self.num = num
        self.title = title
        self.subtitle = subtitle
        self.name = name
        self.filename = filename
        self.comments = comments
        self.xaxisname = xaxisname
        self.yaxisname = yaxisname
        self.y2axisname = y2axisname
        self.xscale = xscale
        self.yscale = yscale
        self.y2scale = y2scale

        self.curves = []
        self.invisible = False


class DataHandler(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.sets = []
        self.num2set = {}
        self.currentset = None
        self.exnum = -1

    def new_dataset(self, dataset):
        try:
            (num, title, subtitle, name, filename, comments, xaxisname,
             yaxisname, y2axisname, xscale, yscale, y2scale) = dataset
        except ValueError:
            raise DataError('Got invalid dataset: %s' % dataset)
        set = DataSet(num, title, subtitle, name, filename, comments,
                      xaxisname, yaxisname, y2axisname, xscale, yscale, y2scale)
        self.sets.append(set)
        self.num2set[set.num] = set
        self.currentset = set
        self.emit(SIGNAL('datasetAdded'), set)

    def add_existing_dataset(self, set):
        set.num = self.exnum
        self.exnum -= 1
        self.sets.append(set)
        self.num2set[set.num] = set
        self.emit(SIGNAL('datasetAdded'), set)

    def add_curve(self, curve):
        try:
            name, coldesc, plotmode, data = curve
            coldesc = [(x or '') for x in coldesc]
        except ValueError:
            raise DataError('Got invalid curve: %s' % curve)
        if not self.currentset:
            raise DataError('No current set, trying to add a curve')
        try:
            self.currentset.curves.append(Curve(name, coldesc, plotmode, data))
        except Exception, err:
            raise DataError(str(err))
        self.currentset.emit(SIGNAL('curveAdded'), self.currentset.curves[-1])

    def add_point(self, index, point):
        if not self.currentset:
            raise DataError('No current set, trying to add a point')
        if not 0 <= index <= len(self.currentset.curves)-1:
            raise DataError('No such curve %d, trying to add points' % index)
        self.currentset.curves[index].add_point(point)
        self.currentset.emit(SIGNAL('pointsAdded'), index)

    def add_points(self, index, points):
        if not self.currentset:
            raise DataError('No current set, trying to add points')
        if not 0 <= index <= len(self.currentset.curves)-1:
            raise DataError('No such curve %d, trying to add points' % index)
        for point in points:
            self.currentset.curves[index].add_point(point)
        self.currentset.emit(SIGNAL('pointsAdded'), index)
