#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

from PyQt4.QtGui import QApplication, QProgressDialog
from PyQt4.QtCore import QObject, pyqtSignal

from nicos.utils.fitting import FitResult


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
    yindex = -1
    dyindex = -1
    disabled = False
    hidden = False
    function = False
    default_xname = None

    def __init__(self):
        self.datax = {}
        self.datanorm = {}
        self.datay = []
        self.datady = []

    @property
    def full_description(self):
        if self.source:
            return '%s [%s]' % (self.description, self.source)
        return self.description

    def copy(self):
        return copy.copy(self)

    def deepcopy(self):
        return copy.deepcopy(self)


def name_unit(name, unit):
    if unit:
        return '%s (%s)' % (name, unit)
    return name


def try_index(seq, index):
    try:
        return seq[index]
    except IndexError:
        return 0.


class DataHandler(QObject):
    datasetAdded = pyqtSignal(object)
    pointsAdded = pyqtSignal(object)
    fitAdded = pyqtSignal(object, object)

    def __init__(self, client):
        QObject.__init__(self)
        self.client = client
        self.sets = []
        self.uid2set = {}
        self.dependent = []
        self.currentset = None
        self.bulk_adding = False

        self.client.connected.connect(self.on_client_connected)
        self.client.dataset.connect(self.on_client_dataset)
        self.client.datapoint.connect(self.on_client_datapoint)
        self.client.datacurve.connect(self.on_client_datacurve)
        self.client.experiment.connect(self.on_client_experiment)

    def on_client_connected(self):
        # retrieve datasets and put them into the scans window
        pd = QProgressDialog(labelText='Transferring datasets, please wait...')
        pd.setRange(0, 1)
        pd.setCancelButton(None)
        pd.show()
        QApplication.processEvents()
        datasets = self.client.ask('getdataset', '*', default=[])
        self.bulk_adding = True
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
        dataset.name = str(dataset.counter)
        dataset.default_xname = name_unit(dataset.xnames[dataset.xindex],
                                          dataset.xunits[dataset.xindex])
        dataset.curves = self._init_curves(dataset)
        for xvalues, yvalues in zip(dataset.xresults, dataset.yresults):
            try:
                self._update_curves(dataset, xvalues, yvalues)
            except Exception:
                from nicos.clients.gui.main import log
                log.error('Error adding datapoint', exc=1)
        self.datasetAdded.emit(dataset)

    def add_existing_dataset(self, dataset, origins=()):
        dataset.uid = str(uuid.uuid1())
        self.sets.append(dataset)
        self.uid2set[dataset.uid] = dataset
        self.datasetAdded.emit(dataset)
        if self.currentset.uid in origins:
            self.dependent.append(dataset)

    def on_client_datapoint(self, data):
        uid, xvalues, yvalues = data
        currentset = self.uid2set.get(uid)
        if not currentset:
            # happens when we didn't catch the beginning of the dataset
            return
        currentset.xresults.append(xvalues)
        currentset.yresults.append(yvalues)
        self._update_curves(currentset, xvalues, yvalues)
        self.pointsAdded.emit(currentset)
        for depset in self.dependent:
            self.pointsAdded.emit(depset)

    def on_client_datacurve(self, data):
        if not self.currentset:
            raise DataError('No current set, trying to add a curve')
        if len(data) == 3:
            # for compatibility with older daemons
            title, dx, dy = data
            res = FitResult(_failed=False, _message='', _title=title,
                            curve_x=dx, curve_y=dy, chi2=0,
                            label_x=0, label_y=0, label_contents=[])
        else:
            res = data[0]
        self.fitAdded.emit(self.currentset, res)

    def on_client_experiment(self, data):
        # clear data
        self.sets = []
        self.uid2set = {}
        self.dependent = []

    def _init_curves(self, dataset):
        curves = []
        normindices = []
        dataset.datanorm = {}
        xnameunits = [name_unit(name, unit) for name, unit
                      in zip(dataset.xnames, dataset.xunits)]
        dataset.datax = dict((key, []) for key in xnameunits)
        for i, (name, info) in enumerate(zip(dataset.xnames, dataset.xvalueinfo)):
            if info.type != 'other':
                continue
            curve = Curve()
            curve.datax = dataset.datax
            curve.datanorm = dataset.datanorm
            curve.default_xname = name_unit(dataset.xnames[dataset.xindex],
                                            dataset.xunits[dataset.xindex])
            if info.unit:
                curve.description = '%s (%s)' % (name, info.unit)
            else:
                curve.description = name
            curve.yindex = -i-1
            curve.dyindex = -1
            curve.hidden = True
            curves.append(curve)

        for i, (name, info) in enumerate(zip(dataset.ynames, dataset.yvalueinfo)):
            if info.type in ('info', 'error', 'filename'):
                continue
            curve = Curve()
            # share data for X and normalization
            curve.datax = dataset.datax
            curve.datanorm = dataset.datanorm
            curve.default_xname = name_unit(dataset.xnames[dataset.xindex],
                                            dataset.xunits[dataset.xindex])
            if info.unit not in ('', 'cts'):
                curve.description = '%s (%s)' % (name, info.unit)
            else:
                curve.description = name
            curve.yindex = i
            if info.type in ('time', 'monitor'):
                normindices.append((i, name))
                curve.disabled = True
            elif info.type == 'calc':
                curve.function = True
            if info.errors == 'sqrt':
                curve.dyindex = -2
            elif info.errors == 'next':
                curve.dyindex = i + 1
            curves.append(curve)
        dataset.xnameunits = xnameunits
        dataset.normindices = normindices
        dataset.datanorm.update((name, []) for (i, name) in normindices)
        return curves

    def _update_curves(self, currentset, xvalues, yvalues):
        done = set()
        for key, val in zip(currentset.xnameunits, xvalues):
            # avoid adding values twice
            if key not in done:
                currentset.datax[key].append(val)
                done.add(key)
        for index, name in currentset.normindices:
            currentset.datanorm[name].append(try_index(yvalues, index))
        for curve in currentset.curves:
            if curve.yindex < 0:
                curve.datay.append(try_index(xvalues, -curve.yindex-1))
                curve.datady.append(0)
            else:
                curve.datay.append(try_index(yvalues, curve.yindex))
                if curve.dyindex >= 0:
                    curve.datady.append(try_index(yvalues, curve.dyindex))
                elif curve.dyindex == -2:
                    curve.datady.append(np.sqrt(try_index(yvalues, curve.yindex)))
                else:
                    curve.datady.append(0)
