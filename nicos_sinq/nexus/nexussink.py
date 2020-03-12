#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <Mark.Koennecke@psi.ch>
#
# *****************************************************************************
import importlib

import h5py
import numpy

from nicos import session
from nicos.core import SLAVE
from nicos.core.constants import POINT
from nicos.core.data import DataSinkHandler
from nicos.core.data.dataset import PointDataset, ScanDataset
from nicos.core.errors import NicosError
from nicos.core.params import Param
from nicos.devices.datasinks import FileSink
from nicos.pycompat import iteritems

from nicos_sinq.nexus.elements import NexusElementBase, NXAttribute, \
    NXScanLink, NXTime


class NexusTemplateProvider(object):
    """
        A base class which provides the NeXus template for the
        NexusSinkHandler.
        Subclasses must implement getTemplate(). This function is supposed to
        return a
        dictionary containg the desired NeXus structure of the file. This
        abstraction allows
        the dynamic provisioning of a suitable NeXus template. Because the
        template may be dependent
        on the setup or other instrument conditions.
    """

    def getTemplate(self):
        raise NotImplementedError


def copy_nexus_template(template):
    """ Implement a specialized version of copy. The dict structure is deep
    copied while the placeholders are a shallow copy of the original """
    if isinstance(template, dict):
        return {k: copy_nexus_template(v) for k, v in template.items()}
    elif isinstance(template, list):
        return [copy_nexus_template(elem) for elem in template]
    else:
        return template


class NexusSinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        self.startdataset = None
        DataSinkHandler.__init__(self, sink, dataset, detector)

    def prepare(self):
        if self.startdataset is None:
            self.startdataset = self.dataset
            if isinstance(self.startdataset, PointDataset):
                self.dataset.countertype = 'scan'
            # Assign the counter
            self.manager.assignCounter(self.dataset)

            # Generate the filenames, only if not set
            if not self.dataset.filepaths:
                self.manager.getFilenames(self.dataset,
                                          self.sink.filenametemplate,
                                          self.sink.subdir)

    def begin(self):
        if self.dataset.settype == POINT and self.dataset.number <= 1:
            self.template = copy_nexus_template(self.sink.loadTemplate())

            self.h5file = h5py.File(self.startdataset.filepaths[0], 'w')
            self.h5file.attrs['file_name'] = numpy.string_(
                self.startdataset.filepaths[0])
            tf = NXTime()
            self.h5file.attrs['file_time'] = numpy.string_(tf.formatTime())

            if not isinstance(self.template, dict):
                raise NicosError('The template should be of type dict')

            # Update meta information of devices, only if not present
            if not self.dataset.metainfo:
                self.manager.updateMetainfo()

            self.createStructure()

    def createStructure(self):
        h5obj = self.h5file['/']
        self.create(self.template, h5obj)
        self.h5file.flush()

    def create(self, dictdata, h5obj):
        for key, val in iteritems(dictdata):
            if isinstance(val, str):
                val = NXAttribute(val, 'string')
                val.create(key, h5obj, self)
            elif isinstance(val, dict):
                if ':' not in key:
                    session.log.warning(
                        'Cannot write group %s, no nxclass defined', key)
                    continue
                [nxname, nxclass] = key.rsplit(':', 1)
                nxgroup = h5obj.create_group(nxname)
                nxgroup.attrs['NX_class'] = numpy.string_(nxclass)
                self.create(val, nxgroup)
            elif isinstance(val, NexusElementBase):
                val.create(key, h5obj, self)
            else:
                session.log.warning('Cannot write %s of type %s', key,
                                    type(val))

    def updateValues(self, dictdata, h5obj, values):
        if isinstance(self.dataset, PointDataset):
            for key, val in iteritems(dictdata):
                if isinstance(val, dict):
                    nxname = key.split(':')[0]
                    childh5obj = h5obj[nxname]
                    self.updateValues(val, childh5obj, values)
                elif isinstance(val, str):
                    # No need to update attributes
                    pass
                elif isinstance(val, NexusElementBase):
                    val.update(key, h5obj, self, values)
                else:
                    session.log.warning('Cannot identify and  update %s', key)

    def append(self, dictdata, h5obj, subset):
        for key, val in iteritems(dictdata):
            if isinstance(val, dict):
                nxname = key.split(':', 1)[0]
                childh5obj = h5obj[nxname]
                self.append(val, childh5obj, subset)
            elif isinstance(val, str):
                # No need to update attributes
                pass
            elif isinstance(val, NexusElementBase):
                try:
                    val.append(key, h5obj, self, subset)
                except Exception as err:
                    session.log.warning('Exception %s on key %s', err, key)
            else:
                session.log.warning('Cannot identify and  append %s', key)

    def putValues(self, values):
        h5obj = self.h5file['/']
        self.updateValues(self.template, h5obj, values)
        self.h5file.flush()

    def resultValues(self, dictdata, h5obj, results):
        for key, val in iteritems(dictdata):
            if isinstance(val, dict):
                nxname = key.split(':')[0]
                childh5obj = h5obj[nxname]
                self.resultValues(val, childh5obj, results)
            elif isinstance(val, str):
                # No need to update attributes
                pass
            elif isinstance(val, NexusElementBase):
                val.results(key, h5obj, self, results)
            else:
                session.log.warning('Cannot add results to %s', key)

    def putResults(self, quality, results):
        h5obj = self.h5file['/']
        self.resultValues(self.template, h5obj, results)
        self.h5file.flush()

    def addSubset(self, subset):
        if isinstance(self.startdataset, ScanDataset):
            h5obj = self.h5file['/']
            self.append(self.template, h5obj, subset)
            self.h5file.flush()

    def find_scan_link(self, h5obj, template):
        for key, val in iteritems(template):
            if isinstance(val, dict):
                nxname = key.split(':', 1)[0]
                childobj = h5obj[nxname]
                link = self.find_scan_link(childobj, val)
                if link is not None:
                    return link
            if isinstance(val, NXScanLink):
                return h5obj.name
        return None

    def make_scan_links(self, h5obj, template, linkpath):
        for key, val in iteritems(template):
            if isinstance(val, dict):
                nxname = key.split(':')[0]
                childobj = h5obj[nxname]
                self.make_scan_links(childobj, val, linkpath)
            else:
                if isinstance(val, NexusElementBase):
                    val.scanlink(key, self, h5obj, linkpath)

    def end(self):
        """
            There is a trick here: The NexusSink sets the dataset only on
            initialisation. And NICOS
            tries to make a new SinkHandler for the ScanDataset and then for
            each PointDaset. The result is that
            I get the NexusSinkHandler.end() doubly called with  last
            PointDataset. However, I keep the startdatset.
            And the NICOS engine sets the startdaset.finished from None to a
            timestamp when it is done. I use this
            to detect the end. If the NICOS engine in some stage changes on
            this one, this code will break
        """
        if self.startdataset.finished is not None:
            if isinstance(self.startdataset, ScanDataset):
                h5obj = self.h5file['/']
                linkpath = self.find_scan_link(h5obj, self.template)
                if linkpath is not None:
                    self.make_scan_links(h5obj, self.template, linkpath)
            try:
                self.h5file.close()
            except Exception:
                # This can happen, especially with missing devices. But the
                # resulting
                # NeXus file is complete and sane.
                pass
            self.sink.end()


class NexusSink(FileSink):
    """
        This is a sink for writing NeXus HDF5 files from a template. The
        template is a dictionary
        representing the structure of the NeXus file. Special elements in
        this dictionary are
        responsible for writing the various NeXus elements. The actual
        writing work is done in the
        NexusSinkHandler. This class just initializes the handler properly.
    """
    parameters = {'templatesmodule': Param(
        'Python module containing NeXus the NexusTemplateProvider subclass',
        type=str, mandatory=True), 'templateclass': Param(
        'Python class implementing NexusTemplateProvider', type=str,
        mandatory=True), }

    handlerclass = NexusSinkHandler
    _handlerObj = None

    def doInit(self, mode):
        if mode == SLAVE:
            return

    #        The default implementation creates gazillions of SinkHandlers.
    #        For NeXus we do
    #        not want this, we want one keeping track of the whole process.
    #        However, we want a
    #        handler object per file.

    def createHandlers(self, dataset):
        if self._handlerObj is None:
            self._handlerObj = self.handlerclass(self, dataset, None)
        else:
            self._handlerObj.dataset = dataset
        return [self._handlerObj]

    def end(self):
        self._handlerObj = None

    def loadTemplate(self):
        mod = importlib.import_module(self.templatesmodule)
        class_ = getattr(mod, self.templateclass)
        inst = class_()
        return inst.getTemplate()
