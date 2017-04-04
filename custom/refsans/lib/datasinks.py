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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""ConfigObj data sink classes for REFSANS."""

import time

from nicos import session
from nicos.core import DataSinkHandler, Override, Param, listof
from nicos.core.constants import POINT
from nicos.devices.datasinks import FileSink

from nicos.utils import AutoDefaultODict

try:
    import configobj
except ImportError:
    configobj = None

TIMEFMT = '%a %b %d %H:%M:%S %Y'


class ConfigObjDatafileSinkHandler(DataSinkHandler):
    """Write the REFSANS specific configobj-formatted scan data file."""

    # def _readdev(self, devname, mapper=lambda x: x):
    #     try:
    #         return mapper(session.getDevice(devname).read())
    #     except NicosError:
    #         return None

    # def _devpar(self, devname, parname, mapper=lambda x: x):
    #     try:
    #         return mapper(getattr(session.getDevice(devname), parname))
    #     except NicosError:
    #         return None

    def _dict(self):
        return AutoDefaultODict()

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._template = sink.filenametemplate
        self._data = None

    def prepare(self):
        self.log.debug('prepare: %r', self.dataset.settype)
        if configobj:
            if self._data is None:
                self._data = configobj.ConfigObj()
            self._number = session.data.assignCounter(self.dataset)
            fp = session.data.createDataFile(self.dataset, self._template[0])
            self._data.filename = fp.filepath
            self._data.initial_comment = ['Start Time %.2f' % time.time(), '',
                                          '']

            self._data['File Name'] = self._data.filename
            self._data['Start Time'] = time.strftime(TIMEFMT)
            self._data['Measurement Comment'] = ''
            self._data['Detector Parameters'] = self._dict()
            self._data['Chopper'] = self._dict()
            self._data['NOKs'] = self._dict()
            self._data['Slits'] = self._dict()
            self._data['Sample'] = self._dict()
            self._data['Detector'] = self._dict()
            self._data['Miscelaneous'] = self._dict()

    def begin(self):
        ds = self.dataset
        scaninfo = ds.info.split('-')[-1].strip()
        if self._data:
            self._data['Measurement Comment'] = scaninfo

    # def _float(self, value):
    #     return float(eval(value))

    # def _integer(self, value):
    #     return int(eval(value))

    def _write_noks(self, metainfo):
        for dev in ['nok1', 'nok2', 'nok3', 'nok4', 'nok5a', 'nok5b', 'nok6',
                    'nok7', 'nok8', 'nok9']:
            if (dev, 'value') in metainfo:
                self._data['NOKs'][dev] = metainfo[(dev, 'value')][0]

    def _write_slits(self, metainfo):
        for dev in ['b1', 'zb0', 'zb1', 'zb2', 'zb3', 'bs1', 'b2', 'h2']:
            if (dev, 'value') in metainfo:
                self._data['Slits'][dev] = metainfo[(dev, 'value')][0]
            if (dev, 'mask') in metainfo:
                self._data['Slits'][dev + '.mask'] = '%s' % \
                    metainfo[(dev, 'mask')][1]
        if ('h2', 'value') not in metainfo and \
           ('h2_center', 'value') in metainfo and \
           ('h2_width', 'value') in metainfo:
            self._data['Slits']['h2'] = (metainfo['h2_width', 'value'][0],
                                         metainfo['h2_center', 'value'][0])

    def _write_misc(self, metainfo):
        vacuum = []
        for dev in ['vacuum_CB', 'vacuum_SFK', 'vacuum_SR']:
            if (dev, 'value') in metainfo:
                vacuum.append(metainfo[(dev, 'value')][0])
        self._data['Miscelaneous']['vakuum'] = vacuum
        for dev in ['shutter']:
            if (dev, 'value') in metainfo:
                self._data['Miscelaneous'][dev] = metainfo[(dev, 'value')][0]

    def _write_detector_params(self, metainfo):
        detparams = self._data['Detector Parameters']
        detparams['filetime_counter.inf'] = 1379678099.0
        detparams['use_counter'] = ['fast']
        detparams['parts'] = ['fast', 'mdll']

        det = self._dict()
        det['physical_size'] = [200, 200]
        det['type'] = 'DENEX_123456789'
        det['borders'] = [150, 400]
        det['offset_search_time_anode'] = 400
        det['pixel_size'] = [1.378, 1.378]
        detparams['detector'] = det

        _help = self._dict()
        _help['connections'] = "the way cards are connected can be accessed " \
                               "with counter.doGetPar('connection')"
        detparams['help'] = _help

        connection = self._dict()
        fast = connection['fast'] = self._dict()
        fast['monitor'] = ['B', 3]
        fast['anode_chan'] = [['A', 0, True], ['A', 1, True]]
        fast['swap_AB'] = False
        fast['card_type'] = 'Fast'
        fast['cathY0_chan'] = ['A', 1, True]
        fast['cathX1_chan'] = ['B', 1, True]
        fast['cathX0_chan'] = ['A', 3, True]
        detparams['connection'] = connection

        mdll = self._dict()
        mdll['card_type'] = 'MesyTec'
        mdll['monitor'] = 'D1'
        detparams['mdll'] = mdll

    def _write_detector(self, metainfo):
        for dev in ['table', 'pivot', 'tube']:
            if (dev, 'value') in metainfo:
                if dev == 'pivot':
                    self._data['Detector']['table.pivot'] = metainfo[
                        (dev, 'value')][0]
                else:
                    self._data['Detector'][dev] = metainfo[(dev, 'value')][0]

    def _write_chopper(self, metainfo):
        chopper = self._dict()
        chopper['intern'] = 'RUN'
        chopper['disk2_pos_6'] = False
        _set = self._dict()

        axis1 = self._dict()
        axis1['speed'] = 895
        _set['axis1'] = axis1

        axis2 = self._dict()
        axis2['phase'] = -94.05
        axis2['gear'] = 1
        _set['axis2'] = axis2

        axis3 = 'Inactive'
        _set['axis3'] = axis3

        axis4 = self._dict()
        axis4['phase'] = -139.78
        axis4['gear'] = 1
        _set['axis4'] = axis4

        axis5 = 'Inactive'
        _set['axis5'] = axis5

        axis6 = self._dict()
        axis6['phase'] = 53.17
        axis6['gear'] = 1
        _set['axis6'] = axis6

        cn = self._dict()
        cn['w1_max'] = 11
        cn['D'] = 22.8
        cn['w1_min'] = 2
        cn['disk2_Pos'] = 4

        target_file = self._dict()
        target_file['SC2_phase'] = 28.82858
        target_file['SC1_phase'] = 4.86024
        target_file['angles'] = [0] * 6
        target_file['freq'] = axis1['speed'] / 60.
        target_file['rpm'] = axis1['speed']
        target_file['D'] = cn['D']
        target_file['d_SC2'] = 10.61
        target_file['SC2_mode'] = 'smart'
        target_file['delay_angle'] = 0
        target_file['disk2_Pos'] = cn['disk2_Pos']
        target_file['SC1_open_angle'] = 27.8231
        target_file['SC2_open_angle'] = 120
        target_file['SC1_Pos'] = 6
        target_file['w1_min'] = cn['w1_min']
        target_file['w1_max'] = cn['w1_max']
        target_file['delay_time'] = 0
        target_file['frame_offsets'] = [((0., 0.), (0, 0)), (0., 0)]
        chopper['set'] = _set
        chopper['cn'] = cn
        chopper['target_file'] = target_file
        self._data['Chopper']['chopper'] = chopper

    def _write_sample(self, metainfo):
        sample = self._dict()
        for dev in ['top_phi', 'top_theta', 'top_z', 'monitor', 'bg', 'z', 'y',
                    'chi', 'phi', 'theta', 'probenwechsler']:
            if (dev, 'value') in metainfo:
                sample[dev] = metainfo[(dev, 'value')][0]
        self._data['Sample']['sample'] = sample

    def putMetainfo(self, metainfo):
        self.log.debug('ADD META INFO %r', metainfo)
        if self._data:
            self._write_detector_params(metainfo)
            self._write_detector(metainfo)
            self._write_noks(metainfo)
            self._write_slits(metainfo)
            self._write_misc(metainfo)
            self._write_chopper(metainfo)
            self._write_sample(metainfo)

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
        """
        self.log.debug('%s', quality)

    def _dump(self):
        if self._data:
            self._data.write()

    def end(self):
        self._dump()
        self._data = None


class ConfigObjDatafileSink(FileSink):
    """A data sink that writes to a YAML compatible data file.

    The `lastpoint` parameter is managed automatically.

    The current file counter as well as the name of the most recently written
    scanfile is managed by the experiment device.
    """

    handlerclass = ConfigObjDatafileSinkHandler

    parameters = {
        'filenametemplate': Param('Name template for the files written',
                                  type=listof(str), userparam=False,
                                  settable=False,
                                  default=['%(proposal)s_'
                                           '%(pointcounter)08d.cfg'],
                                  ),
    }

    parameter_overrides = {
        'settypes': Override(default=[POINT]),
        'semicolon': Override(default=''),
        'commentchar': Override(default='#',)
    }
