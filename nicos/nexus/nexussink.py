# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************

import numpy as np
from h5py import File as H5File
from h5py.version import hdf5_version

from nicos import session
from nicos.core.constants import LIVE, POINT, SCAN, INTERMEDIATE
from nicos.core.data import DataSinkHandler
from nicos.core.data.sink import DataFileBase
from nicos.core.errors import NicosError
from nicos.core.params import Param, dictof, nicosdev
from nicos.devices.datasinks import FileSink
from nicos.nexus.elements import NexusElementBase, NXAttribute, NXScanLink, \
    NXTime
from nicos.utils import importString


class NexusFile(DataFileBase):

    def __init__(self, shortpath, filepath):
        DataFileBase.__init__(self, shortpath, filepath)
        with H5File(filepath, 'w') as h5file:
            h5file.attrs['file_name'] = np.bytes_(filepath)
            h5file.attrs['HDF5_Version'] = np.bytes_(hdf5_version)
            tf = NXTime()
            h5file.attrs['file_time'] = np.bytes_(tf.formatTime())


class NexusTemplateProvider:
    """A base class which provides the NeXus template for the NexusSinkHandler.

    Subclasses **must** implement ``getTemplate()``.

    This abstraction allows the dynamic provisioning of a suitable NeXus
    template. Because the template may be dependent on the setup or other
    instrument conditions.
    """

    def init(self, **kwargs):
        """Initialize the provider.

        In some cases the provider can be used for different instrument with
        the same provider but different devices for the same NeXus elements.
        """

    def getTemplate(self):
        """Return a dictionary containing the desired NeXus structure."""
        raise NotImplementedError


def copy_nexus_template(template):
    """Implement a specialized version of copy.

    The dict structure is deep-copied while the placeholders are a shallow
    copy of the original.
    """
    if isinstance(template, dict):
        return {k: copy_nexus_template(v) for k, v in template.items()}
    if isinstance(template, list):
        return [copy_nexus_template(elem) for elem in template]
    return template


class NexusSinkHandler(DataSinkHandler):
    """
    For a scan NICOS sends first a scan dataset and then a point dataset
    for each scan point. This class has to make sure that all this ends up
    in one NeXus file. This requires keeping a copy of the start dataset
    around and some logic in begin() and end().
    """
    def __init__(self, sink, dataset, detector):
        self.startdataset = None
        self._filename = None
        self.filepath = None
        self.h5file = None
        self.template = {}
        DataSinkHandler.__init__(self, sink, dataset, detector)

    def prepare(self):
        if self.startdataset is None:
            self.startdataset = self.dataset
            # if self.startdataset.settype == POINT:
            #     self.startdataset.countertype = SCAN
            # Assign the counter
            self.manager.assignCounter(self.dataset)

            # Generate the file
            h5file = self.manager.createDataFile(
                self.dataset, self.sink.filenametemplate, self.sink.subdir,
                fileclass=NexusFile)
            self.filepath = h5file.filepath

    def begin(self):
        if self.dataset.settype == POINT and not self._filename:
            self.template = copy_nexus_template(self.sink.loadTemplate())
            if not isinstance(self.template, dict):
                raise NicosError('The template should be of type dict')

            self._filename = self.filepath
            # Update meta information of devices, only if not present
            if not self.dataset.metainfo:
                self.manager.updateMetainfo()
            # Open the hdf5 file
            try:
                self.h5file = H5File(self._filename, 'r+', driver='core')
            except Exception as e:
                self.log.error('Exception while opening NeXus file.',
                                exc_info=e)
                raise e
            self.createStructure()

    def createStructure(self):
        if self.h5file is not None:
            h5obj = self.h5file['/']
        else:
            self.log.warning('Failed to create hdf5 structure, no valid file.')
            return
        self.create(self.template, h5obj)

    def create(self, dictdata, h5obj):
        for key, val in dictdata.items():
            if isinstance(val, str):
                val = NXAttribute(val, 'string')
                val.create(key, h5obj, self)
            elif isinstance(val, dict):
                if ':' not in key:
                    self.log.warning(
                        'Cannot write group %r, no nxclass defined', key)
                    continue
                [nxname, nxclass] = key.rsplit(':', 1)
                nxgroup = h5obj.create_group(nxname)
                nxgroup.attrs['NX_class'] = np.bytes_(nxclass)
                self.create(val, nxgroup)
            elif isinstance(val, NexusElementBase):
                try:
                    val.create(key, h5obj, self)
                except Exception as e:
                    self.log.warning('Exception %r while creating NeXus entry '
                                     'for %r', str(e), key)
            else:
                self.log.warning('Cannot write %r of type %r', key, type(val))

    def updateValues(self, dictdata, h5obj, values):
        if self.dataset.settype == POINT:
            for key, val in dictdata.items():
                if isinstance(val, dict):
                    nxname = key.split(':')[0]
                    childh5obj = h5obj[nxname]
                    self.updateValues(val, childh5obj, values)
                elif isinstance(val, str):
                    # No need to update attributes
                    pass
                elif isinstance(val, NexusElementBase):
                    try:
                        val.update(key, h5obj, self, values)
                    except Exception as e:
                        self.log.warning('Exception %s while updating %s',
                                         str(e), key)
                else:
                    self.log.warning('Cannot identify and update %r', key)

    def append(self, dictdata, h5obj, subset):
        for key, val in dictdata.items():
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
                    self.log.warning('Exception %r while appending to key %r',
                                     err, key)
            else:
                self.log.warning('Cannot identify and append %r', key)

    def putValues(self, values):
        if self.dataset.settype != POINT:
            return
        if values:
            try:
                h5obj = self.h5file['/']
                self.updateValues(self.template, h5obj, values)
            except BlockingIOError:
                # This is not interesting to know
                pass

    def resultValues(self, dictdata, h5obj, results):
        for key, val in dictdata.items():
            if isinstance(val, dict):
                nxname = key.split(':')[0]
                childh5obj = h5obj[nxname]
                self.resultValues(val, childh5obj, results)
            elif isinstance(val, str):
                # No need to update attributes
                pass
            elif isinstance(val, NexusElementBase):
                try:
                    val.results(key, h5obj, self, results)
                except Exception as e:
                    self.log.warning('Exception %s while writing results '
                                     'to %s', str(e), key)
            else:
                self.log.warning('Cannot add results to %r', key)

    def putResults(self, quality, results):
        # Suppress updating data files when updating live data
        if quality == LIVE:
            return
        try:
            h5obj = self.h5file['/']
            self.resultValues(self.template, h5obj, results)
        except BlockingIOError:
            session.log.warning('Other process is accessing NeXus file '
                                'while saving results')
            return
        if quality == INTERMEDIATE:
            self.h5file.flush()
            session.log.debug('Flushed hdf5 file: %s', self._filename)

    def addSubset(self, subset):
        if self.startdataset.settype == SCAN:
            self.begin()
            if self._filename is None:
                self.log.info('skipping: %s', self.dataset.settype)
                return
            try:
                h5obj = self.h5file['/']
                self.append(self.template, h5obj, subset)
            except BlockingIOError:
                session.log.warning('Other process is accessing NeXus file '
                                    'while updating, possibly loosing '
                                    'scan point')

    def find_scan_link(self, h5obj, template):
        for key, val in template.items():
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
        for key, val in template.items():
            if isinstance(val, dict):
                nxname = key.split(':')[0]
                childobj = h5obj[nxname]
                self.make_scan_links(childobj, val, linkpath)
            elif isinstance(val, NexusElementBase):
                val.scanlink(key, self, h5obj, linkpath)

    def test_external_links(self, h5obj, template):
        for key, val in template.items():
            if isinstance(val, dict):
                nxname = key.split(':')[0]
                childobj = h5obj[nxname]
                self.test_external_links(childobj, val)
            else:
                if isinstance(val, NexusElementBase):
                    val.test_written(key, h5obj)

    def end(self):
        """
            There is a trick here: The NexusSink sets the dataset only on
            initialisation.  And NICOS tries to make a new SinkHandler for the
            ScanDataset and then for each PointDataset.  The result is that I
            get the NexusSinkHandler.end() doubly called with the last
            PointDataset.  However, I keep the startdataset.  And the NICOS
            engine sets the startdataset.finished from None to a timestamp
            when it is done.  I use this to detect the end. If the NICOS
            engine in some stage change on this one, this code will break.
        """
        if self.startdataset.finished is not None:
            # if self.startdataset.settype == SCAN:
            # Take the first entry found in the list to make it as
            # default to plot
            self.h5file.attrs['default'] = np.bytes_(list(self.h5file.keys())[0])
            h5obj = self.h5file['/']
            linkpath = self.find_scan_link(h5obj, self.template)
            if linkpath is not None:
                self.make_scan_links(h5obj, self.template, linkpath)
            self.test_external_links(h5obj, self.template)
            # Close file at end of scan
            self.h5file.close()
            self.h5file = None
            self._filename = None
            self.sink.end()
            self.startdataset = None
        else:
            self.dataset = self.manager._current
        self.log.debug('%s: # datasets %d', self, len(self.manager._stack))


class NexusSink(FileSink):
    """This is a sink for writing NeXus HDF5 files from a template.

    The template is a dictionary representing the structure of the NeXus file.
    Special elements in this dictionary are responsible for writing the various
    NeXus elements. The actual writing work is done in the NexusSinkHandler.
    This class just initializes the handler properly.
    """
    parameters = {
        'templateclass': Param('Python class implementing '
                               'NexusTemplateProvider',
                               type=str, mandatory=True),
        'device_mapping': Param('Mapping the template devices to real NICOS '
                                'devices',
                                type=dictof(nicosdev, nicosdev), default={}),
    }

    handlerclass = NexusSinkHandler
    _handlerObj = None

    # The default implementation creates gazillions of SinkHandlers.
    # For NeXus we do not want this, we want one keeping track of the whole
    # process.  However, we want a handler object per file.

    def createHandlers(self, dataset):
        if self._handlerObj is None:
            self._handlerObj = self.handlerclass(self, dataset, None)
        else:
            self._handlerObj.dataset = dataset
        return [self._handlerObj]

    def end(self):
        if self._handlerObj.dataset == self._handlerObj.startdataset:
            self._handlerObj = None

    def loadTemplate(self):
        tp = importString(self.templateclass)()
        tp.init(**self.device_mapping)
        return tp.getTemplate()
