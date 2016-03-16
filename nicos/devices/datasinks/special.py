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

"""Data sink classes (new API) for NICOS."""

import time
from os import path

from nicos import session
from nicos.core import Override, DataSink, DataSinkHandler
from nicos.pycompat import iteritems, cPickle as pickle
from nicos.utils import lazy_property


class SimpleDataset(object):
    """Simplified dataset for transfer to the GUI."""
    # unique id
    uid = ''
    # start time
    started = 0
    # scan info
    scaninfo = ''
    # assigned number
    counter = 0
    # resulting x values
    xresults = []
    # resulting y values
    yresults = []
    # index of the x value to use for plotting
    xindex = 0
    # continuation info
    continuation = None
    cont_direction = 0
    # value info
    xvalueinfo = []
    yvalueinfo = []
    # storage for header info
    headerinfo = {}

    def __init__(self):
        self.xresults = []
        self.yresults = []
        self.xvalueinfo = []
        self.yvalueinfo = []
        self.headerinfo = {}

    # info derived from valueinfo
    @lazy_property
    def xnames(self):
        return [v.name for v in self.xvalueinfo]

    @lazy_property
    def xunits(self):
        return [v.unit for v in self.xvalueinfo]

    @lazy_property
    def ynames(self):
        return [v.name for v in self.yvalueinfo]

    @lazy_property
    def yunits(self):
        return [v.unit for v in self.yvalueinfo]


class DaemonSinkHandler(DataSinkHandler):

    def begin(self):
        self._dataset_emitted = False

    def _emitDataset(self):
        dataset = SimpleDataset()
        dataset.uid = self.dataset.uid
        dataset.started = time.localtime(self.dataset.started)
        dataset.scaninfo = self.dataset.info
        dataset.counter = self.dataset.counter
        dataset.xindex = self.dataset.xindex
        dataset.continuation = self.dataset.continuation
        dataset.cont_direction = self.dataset.cont_direction
        dataset.xvalueinfo = self.dataset.devvalueinfo
        dataset.yvalueinfo = self.dataset.detvalueinfo
        for (devname, key), (_, val, unit, category) in \
                iteritems(self.dataset.metainfo):
            catlist = dataset.headerinfo.setdefault(category, [])
            catlist.append((devname, key, (val + ' ' + unit).strip()))
        session.emitfunc('dataset', dataset)

    def addSubset(self, point):
        if not self._dataset_emitted:
            self._emitDataset()
            self._dataset_emitted = True
        xvalues = point.devvaluelist
        yvalues = point.detvaluelist
        session.emitfunc('datapoint', (xvalues, yvalues))

    # XXX
    # def addFitCurve(self, dataset, result):
    #     session.emitfunc('datacurve', (result,))


class DaemonSink(DataSink):
    """A DataSink that sends datasets to connected GUI clients for live
    plotting.  Only active for daemon sessions.
    """

    activeInSimulation = False

    handlerclass = DaemonSinkHandler

    parameter_overrides = {
        'settypes':  Override(default=['scan', 'subscan']),
    }

    def isActive(self, dataset):
        from nicos.services.daemon.session import DaemonSession
        if not isinstance(session, DaemonSession):
            return False
        return DataSink.isActive(self, dataset)


class SerializedSinkHandler(DataSinkHandler):

    def end(self):
        serial_file = path.join(session.experiment.datapath, '.all_datasets')
        if path.isfile(serial_file):
            try:
                with open(serial_file, 'rb') as fp:
                    datasets = pickle.load(fp)
            except Exception:
                self.log.warning('could not load serialized datasets', exc=1)
                datasets = {}
        else:
            datasets = {}
        datasets[self.dataset.counter] = self.dataset
        try:
            with open(serial_file, 'wb') as fp:
                pickle.dump(datasets, fp, pickle.HIGHEST_PROTOCOL)
        except Exception:
            self.log.warning('could not save serialized datasets', exc=1)


class SerializedSink(DataSink):
    """A data sink that writes serialized datasets to a single file.

    Can be used to retrieve and redisplay past datasets.
    """

    activeInSimulation = False

    handlerclass = SerializedSinkHandler

    parameter_overrides = {
        'settypes':  Override(default=['scan', 'subscan']),
    }
