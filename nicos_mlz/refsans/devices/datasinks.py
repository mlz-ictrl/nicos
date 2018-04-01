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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""ConfigObj data sink classes for REFSANS."""

import time

from nicos import session
from nicos.core import DataSinkHandler, NicosError, Override, Param, listof
from nicos.core.constants import POINT
from nicos.devices.datasinks import FileSink

from nicos.utils import AutoDefaultODict

# if these labels apear as part of a key, they are "known"
element_part = [
    'chopper',
    'chopper2_phase',
    'chopper_mode',
    'chopper1',
    'chopper2_pos',
    'chopper3_phase',
    'chopper4_phase',
    'chopper5_phase',
    'chopper6_phase',
    'cooling_memograph',
    'wegbox_A_1ref',
    'wegbox_A_2ref',
    'wegbox_B_1ref',
    'shutter',
    'FAK40_Cap',
    'FAK40_Press',
    'flow_memograph_in',
    'flow_memograph_out',
    'leak_memograph',
    'p_memograph_in',
    'p_memograph_out',
    't_memograph_in',
    'sds',
    'optic',
    't_memograph_out',
    'shutter_gamma',
    'wegbox_B_2ref',
    'wegbox_C_1ref',
    'wegbox_C_2ref',
    'vacuum_CB',
    'vacuum_SFK',
    'triangle',
    'triangle_phi',
    'triangle_theta',
    'shutter',
    'shutter_gamma',
    'vacuum_SR',
    'REFSANS', 'Crane', 'det', 'Sixfold', 'ReactorPower', 'Exp', 'image',
    'NL2b', 'Space', 'timer', 'Sample', 'mon1', 'mon2'
]
Gonio = [
    'gonio_omega',
    'gonio_phi',
    'gonio_theta',
    'gonio_z',
    'gonio_y',
    'gonio_top_phi',
    'gonio_top_theta',
    'gonio_top_z',
    'd_last_slit_sample',
    'last_slit',
    'samplechanger',
    'length',
    'width',
]
NOKs = [
    'nok1', 'nok2', 'nok3', 'nok4',
    'nok5a', 'nok5b', 'nok6', 'nok7', 'nok8', 'nok9'
]
Slits = ['b1', 'zb0', 'zb1', 'zb2', 'zb3', 'bs1', 'b2', 'h2', 'b3']
Slits_label = ['', '_mode']
simple_slit = ['sc2', 'disc3', 'disc4']

lateral = ['h2', 'h3']
lateral_label = ['_width', '_center']

det_pos = ['det_pivot', 'det_table', 'det_yoke']

monitor = ['prim_monitor']
monitor_label = ['_typ', '_x', '_z']

element_part += NOKs
element_part += Slits
element_part += simple_slit
element_part += Gonio
element_part += det_pos
element_part += monitor
for l in monitor:
    for label in monitor_label:
        element_part.append(l + label)
for l in lateral:
    for label in lateral_label:
        element_part.append(l + label)
for l in Slits:
    for label in Slits_label[1:]:
        element_part.append(l + label)

try:
    import configobj
except ImportError:
    configobj = None

TIMEFMT = '%a %b %d %H:%M:%S %Y'


class ConfigObjDatafileSinkHandler(DataSinkHandler):
    """Write the REFSANS specific configobj-formatted scan data file."""

    def _readdev(self, devname, mapper=lambda x: x):
        try:
            return mapper(session.getDevice(devname).read())
        except NicosError:
            return None

    def _devpar(self, devname, parname, mapper=lambda x: x):
        try:
            return mapper(getattr(session.getDevice(devname), parname))
        except NicosError:
            return None

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
            fp.close()
            self._data.initial_comment = ['Start Time %.2f' % time.time(), '',
                                          '']

            self._data['File Name'] = self._data.filename
            self._data['Start Time'] = time.strftime(TIMEFMT)
            self._data['Measurement Comment'] = 'FIXME READ COMMENT FROM GUI!!!!!'
            self._data['Sample Name'] = self._dict()
            self._data['Detector Parameters'] = self._dict()
            # self._data['Chopper'] = self._dict()
            self._data['NOKs'] = self._dict()
            self._data['Slits'] = self._dict()
            self._data['Lateral'] = self._dict()
            self._data['Sample'] = self._dict()
            self._data['Detector'] = self._dict()
            self._data['Monitor'] = self._dict()
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

    def _write_meas_comment(self, metainfo):
        self._data['Measurement Comment'] = metainfo[('Exp', 'remark')][0]
        self._data['Sample Name'] = '%s' % metainfo[('Sample',
                                                     'samplename')][0]
        self._data['Proposal'] = '%s' % metainfo[('Exp', 'proposal')][0]

    def _write_meas_info(self, metainfo):
        # self._data[''] =
        pass

    def _write_meas_comment(self, metainfo):
        self._data['Measurement Comment'] = metainfo[('Exp', 'remark')][0]
        self._data['Sample Name'] = '%s' % metainfo[('Sample',
                                                     'samplename')][0]
        self._data['Proposal'] = '%s' % metainfo[('Exp', 'proposal')][0]

    def _write_noks(self, metainfo):
        for dev in NOKs:
            if (dev, 'value') in metainfo:
                self._data['NOKs'][dev] = metainfo[(dev, 'value')][0]

    def _write_slits(self, metainfo):
        self._write_label_ext(metainfo, 'Slits', Slits, Slits_label)
        self._write_label_ext(metainfo, 'Slits', simple_slit, [])
        if ('h2', 'value') not in metainfo and \
           ('h2_center', 'value') in metainfo and \
           ('h2_width', 'value') in metainfo:
            self._data['Slits']['h2'] = (metainfo['h2_width', 'value'][0],
                                         metainfo['h2_center', 'value'][0])

    def _write_label_ext(self, metainfo, key, liste, ext):
        for ele in liste:
            for label in ext:
                s = ele + label
                if (s, 'value') in metainfo:
                    self._data[key][s] = (metainfo[s, 'value'][0])

    def _write_lateral(self, metainfo):
        self._write_label_ext(metainfo, 'Lateral', lateral, lateral_label)

    def _write_misc(self, metainfo):
        vacuum = []
        for dev in ['vacuum_CB', 'vacuum_SFK', 'vacuum_SR']:
            if (dev, 'value') in metainfo:
                vacuum.append(metainfo[(dev, 'value')][0])
        self._data['Miscelaneous']['vakuum'] = vacuum
        for dev in ['shutter', 'shutter_gamma']:
            if (dev, 'value') in metainfo:
                self._data['Miscelaneous'][dev] = metainfo[(dev, 'value')][0]

    def _write_detector_params(self, metainfo):
        detparams = self._data['Detector Parameters']

        det = self._dict()
        detparams['detector'] = det

        # detparams['help'] = _help

        # mdll = self._dict()
        # mdll['card_type'] = 'MesyTec'
        # mdll['monitor'] = 'D1'
        # detparams['mdll'] = mdll

    def _write_detector(self, metainfo):
        for dev in det_pos:
            if (dev, 'value') in metainfo:
                self._data['Detector'][dev] = metainfo[(dev, 'value')][0]

    def _write_monitor(self, metainfo):
        self._write_label_ext(metainfo, 'Monitor', monitor, monitor_label)

    def _write_chopper(self, metainfo):
        # chopper = self._dict()
        # chopper['chopper'] = metainfo[('chopper', 'value')][0]
        self._data['chopper'] = metainfo[('chopper', 'value')][0]

    def _write_sample(self, metainfo):
        sample = self._dict()
        for dev in Gonio:
            if (dev, 'value') in metainfo:
                sample[dev] = metainfo[(dev, 'value')][0]
        self._data['Sample'] = sample

    def _write_extra(self, metainfo, elements):
        extra = self._dict()
        for dev in elements:
            if (dev, 'value') in metainfo:
                extra[dev] = metainfo[(dev, 'value')][0]
        self._data['Extra'] = extra

    def putMetainfo(self, metainfo):
        self.log.debug('ADD META INFO %r', metainfo)
        keys = list(metainfo.keys())
        tmp = keys[0]
        self.log.debug('tmp type %s, value %s', type(tmp), tmp)

        elements = []
        # labels = ['value', 'status']
        for tup in keys:
            if tup[0] not in elements and \
               tup[0] not in element_part:
                elements.append(tup[0])
            # if tup[1] not in labels:
            #    labels.append(tup[1])
        if elements:
            self.log.info('EXTRA %s', str(elements))
        # self.log.info('labels %s', str(labels))
        if self._data:
            self._write_meas_info(metainfo)
            self._write_meas_comment(metainfo)
            self._write_chopper(metainfo)
            # self._write_detector_params(metainfo)
            self._write_detector(metainfo)
            self._write_monitor(metainfo)
            self._write_noks(metainfo)
            self._write_slits(metainfo)
            self._write_lateral(metainfo)
            self._write_sample(metainfo)
            self._write_misc(metainfo)
            self._write_extra(metainfo, elements)
        self._dump()

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
