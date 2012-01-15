#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI data handler class."""

__version__ = "$Revision$"

import copy
import uuid

from PyQt4.QtCore import QObject, SIGNAL
from PyQt4.QtGui import QApplication, QProgressDialog

from nicos.gui.utils import unzip


class DataError(Exception):
    pass


class Curve(object):
    description = ''
    yaxis = 1
    yindex = -1
    dyindex = -1
    timeindex = -1
    monindices = []
    disabled = False
    function = False

    def __init__(self):
        self.datax, self.datay, self.datady, self.datatime, self.datamon = \
                    [], [], [], [], []

    def copy(self):
        return copy.copy(self)

    def tolist(self):
        # XXX doesn't handle time/mon
        if self.dyindex != -1:
            return zip(self.datax, self.datay, self.datady)
        return zip(self.datax, self.datay)

    def setdata(self, data):
        # XXX doesn't handle time/mon
        lists = unzip(data)
        self.datax = lists[0]
        self.datay = lists[1]
        if len(lists) == 3:
            self.datady = lists[2]


class DataHandler(QObject):
    def __init__(self, client):
        QObject.__init__(self)
        self.client = client
        self.sets = []
        self.uid2set = {}
        self.dependent = []
        self.currentset = None
        self.bulk_adding = False

        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)
        self.connect(self.client, SIGNAL('dataset'), self.on_client_dataset)
        self.connect(self.client, SIGNAL('datapoint'), self.on_client_datapoint)

    def on_client_connected(self):
        # retrieve datasets and put them into the scans window
        pd = QProgressDialog()
        pd.setLabelText('Transferring datasets, please wait...')
        pd.setRange(0, 1)
        pd.setCancelButton(None)
        pd.show()
        QApplication.processEvents()
        datasets = self.client.ask('getdataset', '*')
        self.bulk_adding = True
        if datasets:
            for dataset in datasets:
                try:
                    self.on_client_dataset(dataset)
                except Exception, err:
                    print 'Error adding dataset:', err
        self.bulk_adding = False
        pd.setValue(1)
        pd.close()

    def on_client_dataset(self, set):
        self.sets.append(set)
        self.uid2set[set.uid] = set
        self.currentset = set
        self.dependent = []
        # add some custom attributes of the dataset
        set.invisible = False
        set.name = str(set.sinkinfo.get('number', set.scaninfo)) # XXX
        set.curves = self._init_curves(set)
        for xvalues, yvalues in zip(set.xresults, set.yresults):
            self._update_curves(xvalues, yvalues)
        self.emit(SIGNAL('datasetAdded'), set)

    def add_existing_dataset(self, set, origins=()):
        set.uid = str(uuid.uuid1())
        self.sets.append(set)
        self.uid2set[set.uid] = set
        self.emit(SIGNAL('datasetAdded'), set)
        if self.currentset.uid in origins:
            self.dependent.append(set)

    def on_client_datapoint(self, (xvalues, yvalues)):
        if not self.currentset:
            raise DataError('No current set, trying to add a point')
        self.currentset.xresults.append(xvalues)
        self.currentset.yresults.append(yvalues)
        self._update_curves(xvalues, yvalues)
        self.emit(SIGNAL('pointsAdded'), self.currentset)
        for depset in self.dependent:
            self.emit(SIGNAL('pointsAdded'), depset)

    def _init_curves(self, set):
        curves = []
        timeindex = -1
        monindices = []
        for i, (name, info) in enumerate(zip(set.ynames, set.yvalueinfo)):
            if info.type in ('info', 'error'):
                continue
            curve = Curve()
            curve.description = '%s (%s)' % (name, info.unit)
            curve.yindex = i
            if info.type == 'other':
                curve.yaxis = 2
            elif info.type == 'time':
                timeindex = i
                curve.disabled = True
            elif info.type == 'monitor':
                monindices.append(i)
                curve.disabled = True
            elif info.type == 'calc':
                curve.function = True
            if info.errors == 'sqrt':
                curve.dyindex = -2
            elif info.errors == 'next':
                curve.dyindex = i+1
            curves.append(curve)
        for curve in curves:
            curve.timeindex = timeindex
            curve.monindices = monindices
        return curves

    def _update_curves(self, xvalues, yvalues):
        for curve in self.currentset.curves:
            try:
                curve.datax.append(xvalues[self.currentset.xindex])
            except IndexError:
                curve.datax.append(len(curve.datax))
            curve.datay.append(yvalues[curve.yindex])
            if curve.dyindex != -1:
                curve.datady.append(yvalues[curve.dyindex])
            if curve.timeindex != -1:
                curve.datatime.append(yvalues[curve.timeindex])
            for i in curve.monindices:
                if yvalues[i] != 0:
                    curve.datamon.append(yvalues[i])
                    break
            else:
                curve.datamon.append(0)
