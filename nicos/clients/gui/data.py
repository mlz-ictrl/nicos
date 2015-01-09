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

"""NICOS GUI data handler class."""

import copy
import uuid
from itertools import chain

import numpy as np

# Wrong number of positional args -> wrong positive on emit
# pylint: disable=E1121
from PyQt4.QtGui import QApplication, QProgressDialog
from PyQt4.QtCore import QObject, SIGNAL


class DataError(Exception):
    pass


class DataProxy(object):
    def __init__(self, lists):
        self.lists = list(lists)

    def __array__(self, *typ):
        return np.array(tuple(chain(*self.lists)), *typ)

    def __len__(self):
        return len(tuple(chain(*self.lists)))


class Curve(object):
    description = ''
    source = ''  # source dataset if curves from different sets are combined
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

    @property
    def full_description(self):
        if self.source:
            return '%s [%s]' % (self.description, self.source)
        return self.description

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)


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
        self.connect(self.client, SIGNAL('datacurve'), self.on_client_datacurve)
        self.connect(self.client, SIGNAL('experiment'), self.on_client_experiment)

    def on_client_connected(self):
        # retrieve datasets and put them into the scans window
        pd = QProgressDialog(labelText='Transferring datasets, please wait...')
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
                except Exception:
                    from nicos.clients.gui.main import log
                    log.error('Error adding dataset', exc=1)
        self.bulk_adding = False
        pd.setValue(1)
        pd.close()

    def on_client_dataset(self, dataset):
        self.sets.append(dataset)
        self.uid2set[dataset.uid] = dataset
        self.currentset = dataset
        self.dependent = []
        # add some custom attributes of the dataset
        dataset.invisible = False
        dataset.name = str(dataset.sinkinfo.get('number', dataset.scaninfo))
        dataset.curves = self._init_curves(dataset)
        for xvalues, yvalues in zip(dataset.xresults, dataset.yresults):
            self._update_curves(xvalues, yvalues)
        self.emit(SIGNAL('datasetAdded'), dataset)

    def add_existing_dataset(self, dataset, origins=()):
        dataset.uid = str(uuid.uuid1())
        self.sets.append(dataset)
        self.uid2set[dataset.uid] = dataset
        self.emit(SIGNAL('datasetAdded'), dataset)
        if self.currentset.uid in origins:
            self.dependent.append(dataset)

    def on_client_datapoint(self, data):
        (xvalues, yvalues) = data
        if not self.currentset:
            raise DataError('No current set, trying to add a point')
        self.currentset.xresults.append(xvalues)
        self.currentset.yresults.append(yvalues)
        self._update_curves(xvalues, yvalues)
        self.emit(SIGNAL('pointsAdded'), self.currentset)
        for depset in self.dependent:
            self.emit(SIGNAL('pointsAdded'), depset)

    def on_client_datacurve(self, data):
        (title, xvalues, yvalues) = data
        if not self.currentset:
            raise DataError('No current set, trying to add a curve')
        newc = Curve()
        newc.description = title
        newc.datax = xvalues
        newc.datay = yvalues
        newc.function = True
        self.currentset.curves.append(newc)
        self.emit(SIGNAL('curveAdded'), self.currentset)

    def on_client_experiment(self, proposal):
        # clear data
        self.sets = []
        self.uid2set = {}
        self.dependent = []


    def _init_curves(self, dataset):
        curves = []
        timeindex = -1
        monindices = []
        for i, (name, info) in enumerate(zip(dataset.ynames, dataset.yvalueinfo)):
            if info.type in ('info', 'error'):
                continue
            curve = Curve()
            if info.unit != 'cts':
                curve.description = '%s (%s)' % (name, info.unit)
            else:
                curve.description = name
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
            if curve.dyindex >= 0:
                curve.datady.append(yvalues[curve.dyindex])
            elif curve.dyindex == -2:
                curve.datady.append(np.sqrt(yvalues[curve.yindex]))
            else:
                curve.datady.append(0)
            if curve.timeindex != -1:
                curve.datatime.append(yvalues[curve.timeindex])
            else:
                curve.datatime.append(0)
            for i in curve.monindices:
                if yvalues[i] != 0:
                    curve.datamon.append(yvalues[i])
                    break
            else:
                curve.datamon.append(0)
