#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

from os import path
from time import time as currenttime

from nicos import session
from nicos.core import DataSink, DataSinkHandler, Override
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos.core.data import ScanData
from nicos.devices.datasinks.image import ImageSink
from nicos.pycompat import cPickle as pickle, memory_buffer


class DaemonSinkHandler(DataSinkHandler):

    def begin(self):
        self._dataset_emitted = False

    def _emitDataset(self):
        session.emitfunc('dataset', ScanData(self.dataset))

    def addSubset(self, point):
        if point.settype != POINT:
            return
        if not self._dataset_emitted:
            self._emitDataset()
            self._dataset_emitted = True
        else:
            xvalues = point.devvaluelist + point.envvaluelist
            yvalues = point.detvaluelist
            session.emitfunc('datapoint',
                             (str(self.dataset.uid), xvalues, yvalues))


class DaemonSink(DataSink):
    """A DataSink that sends scan datasets to connected GUI clients.

    The data will be send for live plotting.  The sink is only active for
    daemon sessions.
    """

    activeInSimulation = False

    handlerclass = DaemonSinkHandler

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
    }

    def isActive(self, dataset):
        from nicos.services.daemon.session import DaemonSession
        if not isinstance(session, DaemonSession):
            return False
        return DataSink.isActive(self, dataset)


class LiveViewSinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        if len(self.detector.arrayInfo()) > 1:
            self.log.warning('image sink only supports one array per detector')

    def putResults(self, quality, results):
        if self.detector.name in results:
            result = results[self.detector.name]
            if result is None:
                return
            buffers = []
            filenames = []
            nx, ny, nz = [], [], []
            for i, data in enumerate(result[1]):
                if data is not None:
                    if len(data.shape) == 1:
                        resX, resY, resZ = data.shape, 1, 1
                    elif len(data.shape) == 2:
                        (resX, resY), resZ = data.shape, 1
                    else:
                        resX, resY, resZ = data.shape
                    if self.dataset.filenames and \
                            i < len(self.dataset.filenames) and \
                            self.dataset.filenames[i]:
                        filename = self.dataset.filenames[i]
                    else:
                        filename = self.sink.filenametemplate[
                                       0] % self.dataset.counter
                    nx += [resX]
                    ny += [resY]
                    nz += [resZ]
                    filenames += [filename]
                    buffers += [memory_buffer(data.astype('<u4'))]
            if buffers:
                session.updateLiveData('Live', self.dataset.uid,
                                       self.detector.name, filenames,
                                       '<u4', nx, ny, nz,
                                       currenttime() - self.dataset.started,
                                       buffers)


class LiveViewSink(ImageSink):
    """A DataSink that sends images to attached clients for live preview."""

    parameter_overrides = {
        # this is fixed string for labeling cached live data
        'filenametemplate': Override(mandatory=False, userparam=False,
                                     default=['<Live>@%d']),
    }

    handlerclass = LiveViewSinkHandler


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
    """A DataSink that writes serialized datasets to a single file.

    Can be used to retrieve and redisplay past datasets.
    """

    activeInSimulation = False

    handlerclass = SerializedSinkHandler

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
    }
