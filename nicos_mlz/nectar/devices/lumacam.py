# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Simon Sebold <simon.sebold@frm2.tum.de>
#
# *****************************************************************************

"""LumaCAM specific devices."""

import os

import numpy as np

from nicos import session
from nicos.core import MASTER, ArrayDesc, Attach, Device, Moveable, Override, \
    Param, oneof, pvname, status
from nicos.core.constants import POINT
from nicos.core.data import DataFile, DataSinkHandler
from nicos.devices.datasinks import FileSink
from nicos.devices.epics import EpicsStringReadable
from nicos.devices.epics.pyepics import EpicsDevice
from nicos.devices.generic import Detector, VirtualTimer
from nicos.devices.generic.detector import ActiveChannel, DummyDetector, \
    ImageChannelMixin
from nicos.devices.generic.manual import ManualSwitch

from nicos_sinq.devices.epics.detector import EpicsDetector


class LumaCamSinkHandler(DataSinkHandler):

    fileclass = DataFile

    def prepare(self):
        self.log.debug('LumaCamSinkHandler.prepare')
        # self.sink._attached_status_prepare.move('preparing')
        # TODO: try except is here because it throws an error when called from beginScan
        # I guess I need to figure out how to deactivate the datasink for scans?
        try:
            self.manager.assignCounter(self.dataset)
            # if not self.defer_file_creation:
            #     self._createFile()
            # session.log.info(self.dataset)
            filename, filepaths = self.manager.getFilenames(
                self.dataset,
                self.sink.filenametemplate,
                self.sink.subdir,
                fileclass=self.fileclass,
                filemode=self.sink.filemode,
                logger=self.sink.log
            )
            filepath = filepaths[0].removeprefix(session.experiment.dataroot).lstrip('/')
            filepath = os.path.split(filepath)[0]
            self.log.debug(f'Got filepaths {filepaths}')
            self.log.debug(f'Selecting filepath {filepath}')
            pointcount = filename
            self.log.debug(f'Setting pointcounterout to {pointcount}')
            self.sink._attached_pointcounterout.move(
                pointcount
            )
            self.log.debug(f'Setting foldernameout to {filepath}')
            self.sink._attached_foldernameout.move(
                filepath
            )
            while int(self.sink._attached_pointcounterout.read(0)) != int(pointcount):
                session.delay(0.1)
                self.log.debug(f'waiting for folder name ack {int(self.sink._attached_pointcounterout.read(0))} != {pointcount}')

        except Exception as e:
            self.log.debug(e)

    # def prepare(self):
    #     """Prepare writing this dataset.

    #     This is usually the place to assign the file counter with the data
    #     manager's `assignCounter()` and request a file with `createDataFile()`.
    #     If a file should only be created when actual data to save is present,
    #     you can defer this to `putResults` or `putMetainfo`.
    #     """

    def begin(self):
        """Begin writing this dataset.

        This is called immediately after `prepare`, but after *all* sink
        handlers have been prepared.  Therefore, the method can use the
        filenames requested from all sinks on ``self.dataset.filenames``.
        """
        self.sink._attached_status_prepare.move('ready')

    def putMetainfo(self, metainfo):
        """Called for point datasets when the dataset metainfo is updated.

        Argument *metainfo* contains the new metainfo.
        ``self.dataset.metainfo`` contains the full metainfo.

        The *metainfo* is a dictionary in this form:

        * key: ``(devname, paramname)``
        * value: ``(value, stringified value, unit, category)``

        where the category is one of the keys defined in
        `nicos.core.params.INFO_CATEGORIES`.
        """
        # self.log.debug(metainfo)

    def putValues(self, values):
        """Called for point datasets when device values are updated.

        The *values* parameter is a dictionary with device names as keys and
        ``(timestamp, value)`` as values.

        ``self.dataset.values`` contains all values collected so far.  You can
        also use ``self.dataset.valuestats`` which is a dictionary with more
        statistics of the values over the whole duration of the dataset in the
        form ``(average, stdev, minimum, maximum)``.
        """

    def putResults(self, quality, results):
        """Called for point datasets when measurement results are updated.

        The *quality* is one of the constants defined in `nicos.core`:

        * LIVE is for intermediate data that should not be written to files.
        * INTERMEDIATE is for intermediate data that should be written.
        * FINAL is for final data.
        * INTERRUPTED is for data that has been read after the counting was
          interrupted by an exception.

        Argument *results* contains the new results.  ``self.dataset.results``
        contains all results so far.

        The *results* parameter is a dictionary with device names as keys and
        ``(scalarvalues, arrays)`` as values.
        """

    def addSubset(self, subset):
        """Called when a new subset of the sink's dataset is finished.

        This is the usual place in a scan handler to react to points measured
        during the scan.
        """

    def end(self):
        """Finish up the dataset (close files etc).

        This method is called on all sinks participating in a dataset, even if
        an error occurred during data collection or even initialization.

        Therefore, the method cannot expect that even its own `prepare()` has
        been called successfully.
        """
        # self.sink._attached_status_prepare.move('ready')

    # def end(self):
    #     # DataSinkHandler.end()
    #     self.sink._attached_status_prepare.move('ready')


class LumaCamFileSinkStatus(ManualSwitch):
    parameter_overrides = {
        'states': Override(default=['preparing', 'ready'], mandatory=False)
    }

    def doStatus(self, maxage=0):
        if self.read(maxage) == 'preparing':
            return status.BUSY, 'preparing'
        return status.OK, ''


class LumaCamSink(FileSink):
    handlerclass = LumaCamSinkHandler

    attached_devices = {
        # This probably includes sample names?
        'foldernameout': Attach('Fname', Moveable),
        'pointcounterout': Attach('Nicos Point Number of the following count', Moveable),
        # 'pointcounterout': Attach('Nicos Point Number of the following count', EpicsStringMoveable),
        'status_prepare': Attach('', LumaCamFileSinkStatus),
    }

    parameter_overrides = {
        # 'subdir': Override(description='Filetype specific subdirectory name '
        #                    'for the image files'),
        # 'settypes': Override(default=[POINT, SCAN, SUBSCAN]),
        'settypes': Override(default=[POINT]),
    }


class FakeImage(ImageChannelMixin, ActiveChannel):

    arraydesc = ArrayDesc('fake', (2, 2), int)

    def doReadArray(self, quality):
        return np.zeros((2, 2))

    def valueInfo(self):
        return ()


class LumaCamStatus(EpicsStringReadable):
    # States names are compatible with EpicsAreaDetector
    busy_states = [
        'Acquire',
        'Readout',
    ]
    ready_states = [
        'Idle',
    ]

    def doStatus(self, maxage=0):
        severity, msg = EpicsStringReadable.doStatus(self, maxage)
        if severity == status.OK:
            luma_status = self.read(maxage)
            if luma_status in self.busy_states:
                return status.BUSY, luma_status
            if luma_status in self.ready_states:
                return status.OK, ''
            return status.OK, luma_status
        return severity, msg


class LumaCamTrigger(VirtualTimer):
    attached_devices = {
        'status_luma': Attach('', LumaCamStatus),
        'trigger_luma': Attach('Device triggered', Moveable),
    }

    parameters = {
        'runvalue': Param('Value of moveable while timer is running',
                          mandatory=True, type=str),
        'stopvalue': Param('Value of moveable while timer is stopped',
                           mandatory=True, type=str),
    }

    def doStart(self):
        self.curstatus = status.OK, 'started'
        self._attached_trigger_luma.move(self.runvalue)
        while self._attached_status_luma.status(0)[0] == status.OK:
            session.delay(0.1)
            self.log.debug('waiting for cam to run')
        self.log.debug(self._attached_status_luma.read(0))
        self.log.debug(self.preselection)
        self.log.debug(f'is controller: {self.iscontroller}')
        VirtualTimer.doStart(self)

    def doFinish(self):
        VirtualTimer.doFinish(self)
        self._attached_trigger_luma.move(self.stopvalue)


class ADLumaCam(EpicsDetector):

    attached_devices = {
        'status': Attach('Status via EPICS', LumaCamStatus),
        'prepare_status': Attach('Status of filename prepare', LumaCamFileSinkStatus),
        'pointcounter': Attach('Current acquition point counter. '
                               'Used to set the raw file name.', Moveable),
        'empir_path_to_add': Attach('Send next path to Empir.', Moveable),
    }

    parameters = {
        'pvprefix': Param('Base PV name withouth :,',
                          type=pvname, mandatory=True, userparam=False),

        'base_raw_file_path': Param('Base file path for the raw tpx3 files on '
                                    'the machine running serval.',
                                    type=str, settable=True, mandatory=True),
        'empir_path_prefix': Param('What to remove from the base_raw_file_path '
                                   'before sending to empir',
                                   type=str, settable=True, mandatory=True),

        # 'raw_file_template': Param('File name template for prefix of the raw '
        #                            'tpx3 file names on the machine running serval.',
        #                            type=str, mandatory=True, settable=True,
        #                            userparam=False),
        # 'num_images': Param('Temporary until TimerChannel is implemented. '
        #                     'Set to ridiculous value and stop acquistion '
        #                     'manually. After how many images (each 2s) '
        #                     'tpx3cam will stop acquisition.',
        #                     type=str, mandatory=True, settable=True,
        #                     userparam=False),
        'bad_pixel_config': Param('Filepath to the bad pixel mask config file '
                                  'on the serval PC.',
                                  type=str, settable=True, volatile=True),
        'dac_config': Param('Filepath to the digital to analog converter config '
                            'file on the serval PC.',
                            type=str, settable=True, volatile=True),
        # Maybe add option to load the parameter set for startup from a JSON file?
        # For now all data is in the default values fo the "Serval XXXX" parameters.
        # 'serval_config': Param('Filepath on the nicos PC containing the parameters '
        #                        'the luma cam autodevices are set to on init.',
        #                        type=str, mandatory=True, settable=True,
        #                        userparam=False),

        'tpx3writeraw': Param('Serval WriteRaw, needs to be one so serval '
                              'writes tpx files.',
                              type=int, default=1, settable=True,
                              volatile=True),
        'tpx3loglevel': Param('Serval LogLevel',
                              type=int, default=1, settable=True, volatile=True),
        'tpx3biasvoltage': Param('Serval BiasVoltage',
                                 type=int, default=40, settable=True,
                                 volatile=True),
        'tpx3biasenabled': Param('Serval BiasEnabled',
                                 type=bool, default=True, settable=True,
                                 volatile=True),
        'tpx3polarity': Param('Serval Polarity',
                              type=str, default='Positive', settable=True,
                              volatile=True),
        'tpx3periphclk80': Param('Serval PeriphClk80',
                                 type=bool, default=True, settable=True,
                                 volatile=True),
        'tpx3triggerin': Param('Serval TriggerIn',
                               type=int, default=0, settable=True, volatile=True),
        'tpx3triggerout': Param('Serval TriggerOut',
                                type=int, default=0, settable=True,
                                volatile=True),
        'tpx3triggerperiod': Param('Serval TriggerPeriod',
                                   type=float, default=2.0, settable=True,
                                   volatile=True),
        'tpx3exposuretime': Param('Serval ExposureTime',
                                  type=float, default=2.0, settable=True,
                                  unit='s', volatile=True),
        'tpx3triggerdelay': Param('Serval TriggerDelay',
                                  type=float, default=0.0, settable=True,
                                  volatile=True),
        'tpx3globaltimestampinterval': Param('Serval GlobalTimestampInterval',
                                             type=float, default=1.0,
                                             settable=True, volatile=True),
        'tpx3tdc0': Param('Serval Tdc0',
                          type=str, default="P0", settable=True, volatile=True),
        'tpx3tdc1': Param('Serval Tdc1',
                          type=str, default="P0", settable=True, volatile=True),
        'tpx3triggermode': Param('Serval TriggerMode',
                                 type=str, default="Continuous", settable=True,
                                 volatile=True),
        'tpx3rawsplitstg': Param('Serval RawSplitStg',
                                 type=str, default="frame", settable=True,
                                 volatile=True),
        'tpx3rawfilepath': Param('Directory for the raw .tpx files on the serval '
                                 'PC. This is communicated to serval/tpx3 and '
                                 'data reduction (empir) via the attached device '
                                 'empir_path_to_add.',
                                 type=str, settable=True, volatile=True),
        'tpx3rawfiletemplate': Param('File name template for the raw .tpx files '
                                     'on the serval PC.',
                                     type=str, settable=True, volatile=True),
        'tpx3numimages': Param('Number of "images" to take. That is, how many '
                               '.tpx files each filled with events of <exposuretime> '
                               'seconds. Usually a very large number and control '
                               'the acquisition time with Acquire 0/1.',
                               type=int, default=99999999, settable=True,
                               volatile=True),
    }

    parameter_overrides = {
        'startpv': Override(mandatory=False, userparam=False, settable=False)
    }

    # Handling of sub PVs --> this should be done in a base class. e.g. EpicsAreaDetector
    # that's also where I copied it from
    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the pvprefix parameter, if necessary.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        prefix = getattr(self, 'pvprefix')
        field = self._record_fields.get(pvparam)

        if field is not None:
            return ':'.join((prefix, field))

        return getattr(self, pvparam)

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in motor record.

        :returnTpx3: List of PV aliases.
        """
        pvs = set(self._record_fields)

        return pvs

    # set_XXXXX is for PVs that can't be read (??) just "activated" (??)
    _record_fields = {
        # Override from EpicsDetector
        # This should be overriden in an EpicsAreaDetector (I think the name is
        # standardized there to be Acquire and Acquire_RBV?)
        # nicos_sinq....EpicsAreaDetector does weird other stuff. basepv vs pvprefix,
        #               other PVs that need to be explicitly specified.
        # nicos_ess ....EpicsAreaDetector same
        # --> todo create EpicsAreadDetector base class
        'startpv': 'Acquire',

        # PVs used by bad_pixel_config and dac_config
        'write_bpcfilepath': 'BPCFilePath',
        'write_bpcfilename': 'BPCFileName',
        'read_bpcfilepath': 'BPCFilePath_RBV',
        'read_bpcfilename': 'BPCFileName_RBV',
        'set_writebpcfile': 'WriteBPCFile',
        'write_dacsfilepath': 'DACSFilePath',
        'write_dacsfilename': 'DACSFileName',
        'read_dacsfilepath': 'DACSFilePath_RBV',
        'read_dacsfilename': 'DACSFileName_RBV',
        'set_writedacsfile': 'WriteDACSFile',
        'read_writefilemessage': 'WriteFileMessage',
        'read_httpcode': 'HttpCode_RBV',

        # PVs used to initialize tpx3/serval
        'read_loglevel': 'LogLevel_RBV',
        'write_loglevel': 'LogLevel',
        'read_biasvoltage': 'BiasVolt_RBV',
        'write_biasvoltage': 'BiasVolt',
        'read_biasenabled': 'BiasEnbl_RBV',
        'write_biasenabled': 'BiasEnbl',
        'read_polarity': 'Polarity_RBV',
        'write_polarity': 'Polarity',
        'read_periphclk80': 'PeriphClk80_RBV',
        'write_periphclk80': 'PeriphClk80',
        'read_triggerin': 'TriggerIn_RBV',
        'write_triggerin': 'TriggerIn',
        'read_triggerout': 'TriggerOut_RBV',
        'write_triggerout': 'TriggerOut',
        'read_triggerperiod': 'AcquireTime_RBV',
        'write_triggerperiod': 'AcquireTime',
        'read_exposuretime': 'AcquirePeriod_RBV',
        'write_exposuretime': 'AcquirePeriod',
        'read_triggerdelay': 'TriggerDelay_RBV',
        'write_triggerdelay': 'TriggerDelay',
        'read_globaltimestampinterval': 'GlblTimestampIntvl_RBV',
        'write_globaltimestampinterval': 'GlblTimestampIntvl',
        'read_tdc0': 'Tdc0_RBV',
        'write_tdc0': 'Tdc0',
        'read_tdc1': 'Tdc1_RBV',
        'write_tdc1': 'Tdc1',
        'read_triggermode': 'TriggerMode_RBV',
        'write_triggermode': 'TriggerMode',
        'read_rawsplitstg': 'RawSplitStg_RBV',
        'write_rawsplitstg': 'RawSplitStg',

        # PVs to set the output of .tpx files (raw event lists of activated pixels directly from the chip)
        'read_rawfilepath': 'RawFilePath_RBV',
        'write_rawfilepath': 'RawFilePath',
        'read_rawfiletemplate': 'RawFileTemplate_RBV',
        'write_rawfiletemplate': 'RawFileTemplate',
        'read_writeraw': 'WriteRaw',
        'write_writeraw': 'WriteRaw',

        # PVs to set acquisition specific settings
        'read_numimages': 'NumImages_RBV',
        'write_numimages': 'NumImages',
        'set_writedata': 'WriteData',
    }

    # PARAMETERS MASKING MULTIPLE PVs

    def _check_file_upload(self):
        msg = self._get_pv('read_writefilemessage', as_string=True).strip('\n\0')
        if http_code := self._get_pv('read_httpcode') != 200:
            self.log.warning(f'Upload failed! {http_code}: {msg}')
        else:
            self.log.info('Upload successful')

    def doReadBad_Pixel_Config(self):
        """Get the current path set for the bad pixel config."""
        # Epics Waveform Char types terminate with \n\0
        raw_path = self._get_pv('read_bpcfilepath', as_string=True).strip('\n\0')
        raw_fname = self._get_pv('read_bpcfilename', as_string=True).strip('\n\0')
        return raw_path + raw_fname

    # Is it ok to write to hardware in doUpdate<Param>?
    # Nicos Documentation: "It may not access the hardware, set other parameters or do write operations on the filesystem."
    # may not == must not? or may not == doesn't need to but can?
    def doWriteBad_Pixel_Config(self, value):
        # self.bad_pixel_config = value
        # Epics waveform chars need to be terminated with \0, otherwise it only overwrites
        # as many chars as the value is long
        # if self._mode == MASTER:
        path, file = os.path.split(value)
        self._put_pv('write_bpcfilepath', path + '/\0', wait=True)
        self._put_pv('write_bpcfilename', file + '\0', wait=True)
        self._put_pv('set_writebpcfile', 1, wait=True)
        self.log.info(f'Uploading bad pixel config: {value}')
        self._check_file_upload()

    def doReadDac_Config(self):
        """Get the current path set for the DAC config."""
        # Epics Waveform Char types terminate with \n\0
        raw_path = self._get_pv('read_dacsfilepath', as_string=True).strip('\n\0')
        raw_fname = self._get_pv('read_dacsfilename', as_string=True).strip('\n\0')
        return raw_path + raw_fname

    def doWriteDac_Config(self, value):
        # Epics waveform chars need to be terminated with \0, otherwise it only overwrites
        # as many chars as the value is long
        if self._mode == MASTER:
            path, file = os.path.split(value)
            self._put_pv('write_dacsfilepath', path + '/\0', wait=True)
            self._put_pv('write_dacsfilename', file + '\0', wait=True)
            self._put_pv('set_writedacsfile', 1, wait=True)
            self.log.info(f'Uploading DAC config: {value}')
            self._check_file_upload()

    # SINGLE PV PARAMETER

    # Read
    def doReadTpx3Writeraw(self):
        return self._get_pv('read_writeraw')

    def doReadTpx3Loglevel(self):
        return self._get_pv('read_loglevel')

    def doReadTpx3Biasvoltage(self):
        return self._get_pv('read_biasvoltage')

    def doReadTpx3Biasenabled(self):
        return self._get_pv('read_biasenabled')

    def doReadTpx3Polarity(self):
        return self._get_pv('read_polarity', as_string=True)

    def doReadTpx3Periphclk80(self):
        return self._get_pv('read_periphclk80')

    def doReadTpx3Triggerin(self):
        return self._get_pv('read_triggerin')

    def doReadTpx3Triggerout(self):
        return self._get_pv('read_triggerout')

    def doReadTpx3Triggerperiod(self):
        return self._get_pv('read_triggerperiod')

    def doReadTpx3Exposuretime(self):
        return self._get_pv('read_exposuretime')

    def doReadTpx3Triggerdelay(self):
        return self._get_pv('read_triggerdelay')

    def doReadTpx3Globaltimestampinterval(self):
        return self._get_pv('read_globaltimestampinterval')

    def doReadTpx3Tdc0(self):
        return self._get_pv('read_tdc0', as_string=True)

    def doReadTpx3Tdc1(self):
        return self._get_pv('read_tdc1', as_string=True)

    def doReadTpx3Triggermode(self):
        return self._get_pv('read_triggermode', as_string=True)

    def doReadTpx3Rawsplitstg(self):
        return self._get_pv('read_rawsplitstg', as_string=True)

    # Write (Update because the default values should be set on Init)
    def doWriteTpx3Writeraw(self, value):
        if self._mode == MASTER:
            self._put_pv('write_writeraw', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Loglevel(self, value):
        if self._mode == MASTER:
            self._put_pv('write_loglevel', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Biasvoltage(self, value):
        if self._mode == MASTER:
            self._put_pv('write_biasvoltage', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Biasenabled(self, value):
        if self._mode == MASTER:
            self._put_pv('write_biasenabled', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Polarity(self, value):
        if self._mode == MASTER:
            self._put_pv('write_polarity', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Periphclk80(self, value):
        if self._mode == MASTER:
            self._put_pv('write_periphclk80', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Triggerin(self, value):
        if self._mode == MASTER:
            self._put_pv('write_triggerin', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Triggerout(self, value):
        if self._mode == MASTER:
            self._put_pv('write_triggerout', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Triggerperiod(self, value):
        if self._mode == MASTER:
            self._put_pv('write_triggerperiod', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Exposuretime(self, value):
        if self._mode == MASTER:
            self._put_pv('write_exposuretime', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Triggerdelay(self, value):
        if self._mode == MASTER:
            self._put_pv('write_triggerdelay', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Globaltimestampinterval(self, value):
        if self._mode == MASTER:
            self._put_pv('write_globaltimestampinterval', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Tdc0(self, value):
        if self._mode == MASTER:
            self._put_pv('write_tdc0', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Tdc1(self, value):
        if self._mode == MASTER:
            self._put_pv('write_tdc1', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Triggermode(self, value):
        if self._mode == MASTER:
            self._put_pv('write_triggermode', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doWriteTpx3Rawsplitstg(self, value):
        if self._mode == MASTER:
            self._put_pv('write_rawsplitstg', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doReadTpx3Rawfilepath(self):
        # more!!
        rawfilepath_value = self._get_pv('read_rawfilepath', as_string=True)
        self.log.debug(rawfilepath_value)
        rawfilepath_value = rawfilepath_value.strip('\n\0')
        self.log.debug(rawfilepath_value)
        # remove the fixed subfolder /tpx3Files_tmp
        rawfilepath_value = os.path.split(rawfilepath_value)[0]
        self.log.debug(f'removed tpx3Files_tmp subfolder: {rawfilepath_value}')
        return rawfilepath_value

    # here no doUpdate because this is set specifically at each doPrepare
    # doch: should also be set to the default/configured value at Init
    def doWriteTpx3Rawfilepath(self, value):
        if self._mode == MASTER:
            # This functionality might be better placed in a custom data sink
            # The goal is to set the output for the temporary raw (pixel activation event files) to something unique
            # which is then passed to the data reduction software (empir) via different PVs
            # the subfolder /tpx3Files_tmp is hard coded in empir
            rawfilepath_value = os.path.join(value, 'tpx3Files_tmp') + '\0'
            self.log.debug(rawfilepath_value)
            self._put_pv('write_rawfilepath', rawfilepath_value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doReadTpx3Rawfiletemplate(self):
        self._get_pv('read_rawfiletemplate', as_string=True)

    def doWriteTpx3Rawfiletemplate(self, value):
        if self._mode == MASTER:
            self._put_pv('write_rawfiletemplate', value + '\0')
            self._put_pv('set_writedata', 1, wait=True)

    def doReadTpx3Numimages(self):
        return self._get_pv('read_numimages')

    def doWriteTpx3Numimages(self, value):
        if self._mode == MASTER:
            self._put_pv('write_numimages', value, wait=True)
            self._put_pv('set_writedata', 1, wait=True)

    def doInit(self, mode):
        EpicsDetector.doInit(self, mode)
        self.tpx3writeraw = 1
        self.log.info('Initialization of LumaCam complete.')

    def doPrepare(self):
        self.log.debug('ADLumaCam::doPrepare')

        current_point = int(self._attached_pointcounter.read(0))

        recon_folder = os.path.join(self.base_raw_file_path, f'{current_point:08d}')
        self.tpx3rawfilepath = recon_folder
        # this is set when starting empir! TODO think about how to handle
        recon_folder = recon_folder.removeprefix(self.empir_path_prefix)
        self._attached_empir_path_to_add.start(recon_folder)
        self.tpx3writeraw = 1
        self.log.debug('Detector::doPrepare')
        EpicsDetector.doPrepare(self)

    def doStatus(self, maxage=0):
        return Detector.doStatus(self, maxage)

    def doFinish(self):
        EpicsDetector.doFinish(self)
        while self._attached_status.read(0) != 'Idle':
            session.delay(0.1)
            self.log.debug('waiting for LumaCamStatus to be "Idle".')

        self.log.debug('Setting attached Empir path to add to empty string.')
        self._attached_empir_path_to_add.start('')
        self.log.debug('ADLumaCam:doFinish done.')

    # def duringMeasureHook(self, elapsed):
    #     return LIVE


class ManualStringMoveable(Moveable):
    _value = ''

    def doStart(self, target):
        self._value = target

    def doRead(self, maxage=0):
        return self._value

    def doStatus(self, maxage=0):
        return status.OK, ''


# Idee: eine HasEpicsPvMixin für Devices die PVs haben aber kein EpicsDevice sind?
# und dann --> class EpicsDevice(HasEpicsPvMixin, Device)?
class Empir(EpicsDevice, Device):

    parameters = {
        'pvprefix': Param('pvprefix', pvname),
        'px2ph_dspace': Param('px2ph_dspace', float, settable=True, unit=''),
        'px2ph_dtime': Param('px2ph_dtime', float, settable=True, unit=''),
        'px2ph_npxmin': Param('px2ph_npxmin', float, settable=True, unit=''),
        'ph2ev_dspace': Param('ph2ev_dspace', float, settable=True, unit=''),
        'ph2ev_dtime': Param('ph2ev_dtime', float, settable=True, unit=''),
        'ph2ev_durmax': Param('ph2ev_durmax', float, settable=True, unit=''),
        'evfilt_phmin': Param('Minimum number of photons for accepting an event.', int, settable=True, unit=''),
        'evfilt_psdmin': Param('Pulse Shape Discrimination value threshold for accepting an event.', float, settable=True, unit=''),
        'ev2img_sizex': Param('ev2img_sizex', int, settable=True, volatile='px'),
        'ev2img_sizey': Param('ev2img_sizey', int, settable=True, volatile='px'),
        # TODO add oneof()
        'ph2ev_alg': Param('ph2ev_alg', str, settable=True),
        'ev2img_texttrig': Param('ev2img_texttrig', oneof('ignore', 'reference', 'frameSync'), settable=True, unit=''),
        'ev2img_tres': Param('ev2img_tres, empty means ignore other wise str(float in seconds).', str, settable=True, unit='s'),
        'ev2img_tlim': Param('ev2img_tlim, empty means ignore other wise str(int in seconds).', str, settable=True, unit='s'),
    }
    _record_fields = {
        'read_px2ph_dspace': 'px2ph:dSpace',
        'write_px2ph_dspace': 'px2ph:dSpace',
        'read_px2ph_dtime': 'px2ph:dTime',
        'write_px2ph_dtime': 'px2ph:dTime',
        'read_px2ph_npxmin': 'px2ph:nPxMin',
        'write_px2ph_npxmin': 'px2ph:nPxMin',
        'read_ph2ev_alg': 'ph2ev:alg',
        'write_ph2ev_alg': 'ph2ev:alg',
        'read_ph2ev_dspace': 'ph2ev:dSpace',
        'write_ph2ev_dspace': 'ph2ev:dSpace',
        'read_ph2ev_dtime': 'ph2ev:dTime',
        'write_ph2ev_dtime': 'ph2ev:dTime',
        'read_ph2ev_durmax': 'ph2ev:durMax',
        'write_ph2ev_durmax': 'ph2ev:durMax',
        'read_evfilt_phmin': 'evFilt:phMin',
        'write_evfilt_phmin': 'evFilt:phMin',
        'read_evfilt_psdmin': 'evFilt:psdMin',
        'write_evfilt_psdmin': 'evFilt:psdMin',
        'read_ev2img_sizex': 'ev2img:size_x',
        'write_ev2img_sizex': 'ev2img:size_x',
        'read_ev2img_sizey': 'ev2img:size_y',
        'write_ev2img_sizey': 'ev2img:size_y',
        'read_ev2img_texttrig': 'ev2img:t_extTrig',
        'write_ev2img_texttrig': 'ev2img:t_extTrig',
        'read_ev2img_tres': 'ev2img:t_res',
        'write_ev2img_tres': 'ev2img:t_res',
        'read_ev2img_tlim': 'ev2img:t_lim',
        'write_ev2img_tlim': 'ev2img:t_lim',
        # devs
        # 'nProcessing',int ro
        # 'lastDone_file_meas',str  ro
        # 'lastDone_file_name',str ro
        # 'lastDone_meas',str ro
        # 'path_toAdd',str rw
        # 'path_lastAdded',str ro
    }

    # Handling of sub PVs --> this should be done in a base class. e.g. EpicsAreaDetector
    # that's also where I copied it from
    def _get_pv_name(self, pvparam):
        """
        Implementation of inherited method that translates between PV aliases
        and actual PV names. Automatically adds a prefix to the PV name
        according to the pvprefix parameter, if necessary.

        :param pvparam: PV alias.
        :return: Actual PV name.
        """
        prefix = getattr(self, 'pvprefix')
        field = self._record_fields.get(pvparam)

        if field is not None:
            return ':'.join((prefix, field))

        return getattr(self, pvparam)

    def _get_pv_parameters(self):
        """
        Implementation of inherited method to automatically account for fields
        present in motor record.

        :returnTpx3: List of PV aliases.
        """
        pvs = set(self._record_fields)

        return pvs

    def doReadPx2Ph_Dspace(self):
        return self._get_pv('read_px2ph_dspace')

    def doReadPx2Ph_Dtime(self):
        return self._get_pv('read_px2ph_dtime')

    def doReadPx2Ph_Npxmin(self):
        return self._get_pv('read_px2ph_npxmin')

    def doReadPh2Ev_Dspace(self):
        return self._get_pv('read_ph2ev_dspace')

    def doReadPh2Ev_Dtime(self):
        return self._get_pv('read_ph2ev_dtime')

    def doReadPh2Ev_Durmax(self):
        return self._get_pv('read_ph2ev_durmax')

    def doReadEvfilt_Phmin(self):
        return self._get_pv('read_evfilt_phmin')

    def doReadEvfilt_Psdmin(self):
        return self._get_pv('read_evfilt_psdmin')

    def doReadEv2Img_Sizex(self):
        return self._get_pv('read_ev2img_sizex')

    def doReadEv2Img_Sizey(self):
        return self._get_pv('read_ev2img_sizey')

    def doReadPh2Ev_Alg(self):
        return self._get_pv('read_ph2ev_alg', as_string=True)

    def doReadEv2Img_Texttrig(self):
        return self._get_pv('read_ev2img_texttrig', as_string=True)

    def doReadEv2Img_Tres(self):
        return self._get_pv('read_ev2img_tres', as_string=True)

    def doReadEv2Img_Tlim(self):
        return self._get_pv('read_ev2img_tlim', as_string=True)

    def doWritePx2Ph_Dspace(self, value):
        if self._mode == MASTER:
            self._put_pv('write_px2ph_dspace', value)

    def doWritePx2Ph_Dtime(self, value):
        if self._mode == MASTER:
            self._put_pv('write_px2ph_dtime', value)

    def doWritePx2Ph_Npxmin(self, value):
        if self._mode == MASTER:
            self._put_pv('write_px2ph_npxmin', value)

    def doWritePh2Ev_Dspace(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ph2ev_dspace', value)

    def doWritePh2Ev_Dtime(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ph2ev_dtime', value)

    def doWritePh2Ev_Durmax(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ph2ev_durmax', value)

    def doWriteEvfilt_Phmin(self, value):
        if self._mode == MASTER:
            self._put_pv('write_evfilt_phmin', value)

    def doWriteEvfilt_Psdmin(self, value):
        if self._mode == MASTER:
            self._put_pv('write_evfilt_psdmin', value)

    def doWriteEv2Img_Sizex(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ev2img_sizex', value)

    def doWriteEv2Img_Sizey(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ev2img_sizey', value)

    def doWritePh2Ev_Alg(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ph2ev_alg', value)

    def doWriteEv2Img_Texttrig(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ev2img_texttrig', value)

    def doWriteEv2Img_Tres(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ev2img_tres', value)

    def doWriteEv2Img_Tlim(self, value):
        if self._mode == MASTER:
            self._put_pv('write_ev2img_tlim', value)


class DummyImageChannel(ImageChannelMixin, DummyDetector):

    arraydesc = ArrayDesc('dummy', shape=(100, 100), dtype=np.uint16)

    def doReadArray(self, quality):
        return np.zeros((100, 100), dtype=np.uint16)
