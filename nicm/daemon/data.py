#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICOS daemon data handling
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

"""
Data handling interface between nicm and client.
"""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

COL_DESCS = set(('x', 'dx', 'y', 'dy', 'z', 'norm', ''))
PLOT_MODES = set(('default', 'lines', 'points', 'map', 'y2', 'disabled'))


class Curve(object):
    def __init__(self, name, coldesc, plotmode):
        for col in coldesc:
            if col.split(':', 1)[0].lower() not in COL_DESCS:
                raise ValueError('invalid coldesc: %r' % col)
        if plotmode == '':
            plotmode = 'default'
        for mode in plotmode.split(','):
            if mode.lower() not in PLOT_MODES:
                raise ValueError('invalid plotmode: %r' % mode)
        self.name = name
        self.coldesc = coldesc
        self.plotmode = plotmode
        self.values = []

    def append(self, values):
        self.values.append(values)

    def extend(self, values):
        self.values.extend(values)

    def tolist(self):
        return [self.name, self.coldesc, self.plotmode, self.values]


class DataSet(object):
    def __init__(self, num, title, subtitle='',
                 name='', filename='', comments='',
                 xaxisname='', yaxisname='', y2axisname='',
                 xscale=(0, 0), yscale=(0, 0), y2scale=(0, 0)):
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
        self.last_curve = -1

    def tolist(self):
        return [[self.num, self.title, self.subtitle, self.name, self.filename,
                 self.comments, self.xaxisname, self.yaxisname, self.y2axisname,
                 self.xscale, self.yscale, self.y2scale]] + \
               [curve.tolist() for curve in self.curves]


class DataHandler(object):
    def __init__(self, daemon):
        self._log = daemon._log
        self._emit_event = daemon.emit_event
        self._datasets = []
        self._dataset_number = 0
        self.active_dataset = None

    def purge(self):
        self._datasets = []
        self._dataset_number = 0
        self.active_dataset = None

    def update_dataset(self, title, subtitle='', name='', filename='', comments='',
                       xaxisname='', yaxisname='', y2axisname='',
                       xscale=(0, 0), yscale=(0, 0), y2scale=(0, 0)):
        self.active_dataset.title = title
        self.active_dataset.subtitle = subtitle
        self.active_dataset.name = name
        self.active_dataset.filename = filename
        self.active_dataset.comments = comments
        self.active_dataset.xaxisname = xaxisname
        self.active_dataset.yaxisname = yaxisname
        self.active_dataset.y2axisname = y2axisname
        self.active_dataset.xscale = xscale
        self.active_dataset.yscale = yscale
        self.active_dataset.y2scale = y2scale

        if title:
            self._emit_event('new_dataset', self.active_dataset.tolist())

    def new_dataset(self, title, subtitle='', name='', filename='', comments='',
                    xaxisname='', yaxisname='', y2axisname='',
                    xscale=(0, 0), yscale=(0, 0), y2scale=(0, 0)):
        self._dataset_number += 1
        self.active_dataset = dataset = DataSet(
            self._dataset_number, title, subtitle, name, filename, comments,
            xaxisname, yaxisname, y2axisname, xscale, yscale, y2scale)
        self._datasets.append(dataset)
        self._emit_event('new_dataset', dataset.tolist())

    def add_curve(self, name, coldesc, plotmode=''):
        curve = Curve(name, coldesc, plotmode)
        self._emit_event('new_curve', curve.tolist())
        self.active_dataset.curves.append(curve)
        self.active_dataset.last_curve += 1
        return self.active_dataset.last_curve

    def add_point(self, index, point):
        if index == -1:
            index = self.active_dataset.last_curve
        if not 0 <= index <= self.active_dataset.last_curve:
            self._log.warning('[dataset] discarding add_point(), '
                              'index %s neither -1 nor between 0 and %d',
                              index, self.active_dataset.last_curve)
            return
        # add required dummy column at the end
        point = list(point) + [0]
        self._emit_event('new_point', (index, point))
        self.active_dataset.curves[index].append(point)

    def add_points(self, index, points):
        if index == -1:
            index = self.active_dataset.last_curve
        if not 0 <= index <= self.active_dataset.last_curve:
            self._log.warning('[dataset] discarding add_points(), '
                              'index %s neither -1 nor between 0 and %d',
                              index, self.active_dataset.last_curve)
            return
        # add required dummy column at the end
        points = [list(point) + [0] for point in points]
        self._emit_event('new_points', (index, points))
        self.active_dataset.curves[index].extend(points)

    def tolist(self):
        return [dataset.tolist() for dataset in self._datasets]
