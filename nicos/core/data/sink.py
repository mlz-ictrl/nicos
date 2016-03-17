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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Base classes for NICOS data sinks."""

from nicos import session
from nicos.core.constants import SIMULATION
from nicos.core.device import Device
from nicos.core.params import Param, listof, setof
from nicos.core.data.dataset import SETTYPES


class DataSinkHandler(object):
    """Handles sink operations for a single dataset."""

    def __init__(self, sink, dataset, detector):
        """Prepare `DataSinkHandler` for writing this `dataset`."""
        self.log = sink.log
        self.sink = sink
        self.dataset = dataset
        self.detector = detector

    #
    # DataSinkHandler API
    #

    def start(self):
        """Start writing this dataset."""

    def begin(self):
        """Run after sinks are all started."""
        # filenames are set when this is called

    def putMetainfo(self, metainfo):
        """Called when the dataset metainfo is updated.

        Argument *metainfo* contains the new metainfo.  ``dataset.metainfo``
        contains the full metainfo.

        The metainfo is a dictionary in this form:

        * key: (devname, paramname)
        * value: (value, stringified value, unit, category)

        where the category is one of the keys defined in
        `nicos.core.params.INFO_CATEGORIES`.
        """

    def putValues(self, values):
        """Called when device values are updated.

        The *values* parameter is a dictionary with device names as keys and
        ``(timestamp, value)`` as values.
        """

    def putResults(self, quality, results):
        """Called when the point dataset main results are updated.

        The *quality* is one of the constants defined in the module:

        * LIVE is for intermediate data that should not be written to files.
        * INTERMEDIATE is for intermediate data that should be written.
        * FINAL is for final data.
        * INTERRUPTED is for data that has been read after the counting was
          interrupted by an exception.

        Argument *results* contains the new results.  ``dataset.results``
        contains all results so far.

        The *results* parameter is a dictionary with device names as keys and
        ``(scalarvalues, arrays)`` as values.
        """

    def addSubset(self, subset):
        """Called when a new subset of the sink's dataset is finished.
        """

    def finish(self):
        """Finish up writing this dataset."""

    def end(self):
        """Run after sinks are all finished."""

    def addAnalysis(self):
        """Add an after-measure analysis to the dataset.

        XXX: discuss if this is in the right place here.
        """


class DataSink(Device):
    """Class that represents one way of processing incoming data.

    This is a device to be instantiated once per setup so that it can be
    configured easily through NICOS setups.  Actual processing is done by a
    `DataSinkHandler` class, of which one instance is created per dataset.
    """

    parameters = {
        'detectors': Param('List of detector names to activate this sink '
                           '(default is always activated)', type=listof(str)),
        'settypes':  Param('List of dataset types to activate this sink '
                           '(default is for all settypes the sink supports)',
                           type=setof(*SETTYPES)),
    }

    # Set to true in subclasses that are safe for simulation.
    activeInSimulation = False

    # Set this to the corresponding Handler class.
    handlerclass = None

    def isActive(self, dataset):
        """Return True if the sink can and should process this dataset."""
        if session.mode == SIMULATION and not self.activeInSimulation:
            return False
        if self.settypes and dataset.settype not in self.settypes:
            return False
        if self.detectors and \
           not (set(d.name for d in dataset.detectors) & set(self.detectors)):
            return False
        return True

    def createHandlers(self, dataset):
        """Start processing the given dataset (a BaseDataset).

        Creates the corresponding DataSinkHandler instances to use for this
        dataset determined via `handlerclass` and returns them.
        """
        if self.handlerclass is None:
            raise NotImplementedError('Must set an "handlerclass" attribute '
                                      'on %s' % self.__class__)
        if dataset.settype == 'point':
            dets = set(d.name for d in dataset.detectors)
            if self.detectors:
                dets &= set(self.detectors)
            # pylint: disable=not-callable
            return [self.handlerclass(self, dataset, session.getDevice(det))
                    for det in dets]
        else:
            # pylint: disable=not-callable
            return [self.handlerclass(self, dataset, None)]
