#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import time

from nicos import session
from nicos.core import DataSinkHandler, NicosError, Override, Param, listof
from nicos.core.constants import POINT
from nicos.devices.datasinks import FileSink
from nicos.utils import AutoDefaultODict

# if these labels apear as part of a key, they are "known"
element_part = [
    'cooling_memograph',
    'FAK40_Cap',
    'FAK40_Press',
    'flow_memograph_in',
    'flow_memograph_out',
    'leak_memograph',
    'NL2b', 'Space', 'timer', 'Sample', 'mon1', 'mon2'
    'optic',
    'p_memograph_in',
    'p_memograph_out',
    'REFSANS', 'Crane', 'det', 'Sixfold', 'ReactorPower', 'Exp', 'image',
    'sds',
    # 'shutter',
    # 'shutter_gamma',
    't_memograph_in',
    't_memograph_out',
    'triangle',
    'triangle_phi',
    'triangle_theta',
    'vacuum_CB',
    'vacuum_SFK',
    'vacuum_SR',
    'wegbox_A_1ref',
    'wegbox_A_2ref',
    'wegbox_B_1ref',
    'wegbox_B_2ref',
    'wegbox_C_1ref',
    'wegbox_C_2ref',
]
chopper = [
    'chopper2/pos',
    'chopper',
    'chopper/mode',
    'chopper/resolution',
    'chopper/speed',
    'chopper/wlmin',
    'chopper/wlmax',
    'chopper/gap',
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
    'height',
    'autocollimator_phi',
    'autocollimator_theta',
    'last_slit',
    'samplechanger',
    'Sample/length',
    'Sample/width',
]
NOKs = [
    'nok1', 'nok2', 'nok3', 'nok4',
    'nok5a', 'nok5b', 'nok6', 'nok7', 'nok8', 'nok9',
]
NOKs_label = ['', '_mode']

Slits = ['b1', 'zb0', 'zb1', 'zb2', 'zb3', 'bs1', 'b2', 'h2', 'b3']
Slits_label = ['', '_mode']
simple_slit = ['sc2', 'disc3', 'disc4']

lateral = ['h2']
lateral_label = ['', '_width', '_center']
simple_lateral = ['h3']
simple_lateral_label = ['', '_mode']

det_pos = [
    'det_pivot',
    'det_table',
    'det_yoke',
    'beamstop_height',
    'beamstop_center',
    'beamstop_asym',
]

optic = ['optic']
optic_label = ['', '_mode']

monitor = ['prim_monitor']
monitor_label = ['_typ', '_x', '_z']

Miscellaneous = [
    'shutter',
    'shutter_gamma',
    'pressure_SR',
    'pressure_SFK',
    'pressure_CB',
]

VSD = [
    'ChopperEnable2',
    'ChopperEnable1',
    'ControllerStatus',
    'Air1Pressure',
    'Air2Pressure',
    'AkkuPower',
    'Media_DigitalOutput1',
    'Media_DigitalOutput2',
    'Media_DigitalOutput3',
    'Media_DigitalOutput4',
    'Media1Current',
    'Media1Voltage',
    'Media2Current',
    'Media2Voltage',
    'Media3Current',
    'Media3Voltage',
    'Media4Current',
    'Media4Voltage',
    'Merker128',
    'Merker129',
    'Merker253',
    'Merker254',
    'PowerBreakdown',
    'PowerSupplyNormal',
    'PowerSupplyUSV',
    'SolenoidValve',
    'Temperature1',
    'Temperature2',
    'Temperature3',
    'Temperature4',
    'Temperature5',
    'Temperature6',
    'Temperature7',
    'Temperature8',
    'TempVibration',
    'User1Current',
    'User1Voltage',
    'User2Current',
    'User2Voltage',
    'VSD_User1DigitalInput',
    'VSD_User1DigitalOutput1',
    'VSD_User1DigitalOutput2',
    'VSD_User2DigitalInput',
    'VSD_User2DigitalOutput1',
    'VSD_User2DigitalOutput2',
    'VSD_User3DigitalInput1',
    'VSD_User3DigitalInput2',
    'VSD_User3DigitalInput3',
    'VSD_User3DigitalOutput1',
    'VSD_User3DigitalOutput2',
    'VSD_User3DigitalOutput3',
    'VSD_User4DigitalInput1',
    'VSD_User4DigitalInput2',
    'VSD_User4DigitalInput3',
    'VSD_User4DigitalOutput1',
    'VSD_User4DigitalOutput2',
    'VSD_User4DigitalOutput3',
    'Water1Flow',
    'Water1Pressure',
    'Water1Temp',
    'Water2Flow',
    'Water2Pressure',
    'Water2Temp',
    'Water3Flow',
    'Water3Temp',
    'Water4Flow',
    'Water4Temp',
    'Water5Flow',
    'Water5Temp',
]

cpt = ['cpt', 6]

analog_encoder = '_acc'

element_part += chopper
element_part += simple_slit
element_part += Gonio
element_part += VSD
element_part += det_pos
element_part += monitor
element_part += Miscellaneous

for l in optic:
    for label in optic_label:
        element_part.append(l + label)
for l in NOKs:
    for label in NOKs_label:
        element_part.append(l + label)
for l in monitor:
    for label in monitor_label:
        element_part.append(l + label)

for l in lateral:
    for label in lateral_label:
        element_part.append(l + label)
for l in simple_lateral:
    for label in simple_lateral_label:
        element_part.append(l + label)

for l in Slits:
    for label in Slits_label:
        element_part.append(l + label)
for i in range(cpt[1]):
    element_part.append(cpt[0] + '%d' % (i + 1))

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
            # TODO: Check the need of dictionaries
            self._data['Detector Parameters'] = self._dict()
            self._data['Chopper'] = self._dict()
            self._data['NOKs'] = self._dict()
            self._data['Slits'] = self._dict()
            self._data['Lateral'] = self._dict()
            self._data['Sample'] = self._dict()
            self._data['Detector'] = self._dict()
            self._data['Monitor'] = self._dict()
            self._data['Miscellaneous'] = self._dict()
            self._data['vsd'] = self._dict()
            self._data['optic'] = self._dict()
            self._data['cpt'] = self._dict()
            self._data['analog_encoder'] = self._dict()

    def begin(self):
        ds = self.dataset
        scaninfo = ds.info.split('-')[-1].strip()
        if self._data:
            self._data['Measurement Comment'] = scaninfo

    def _write_meas_comment(self, metainfo):
        # TODO: Check which of the 'Measurement Comment' is the right one
        self._data['Measurement Comment'] = metainfo['Exp', 'remark'][0]
        self._data['instrument'] = metainfo['REFSANS', 'instrument'][0]
        try:
            self._data['usercomment'] = metainfo['det', 'usercomment'][0]
        except (KeyError, IndexError):
            self._data['usercomment'] = 'None'
        self._data['Sample Name'] = '%s' % metainfo['Sample',
                                                    'samplename'][0]
        self._data['Proposal'] = '%s' % metainfo['Exp', 'proposal'][0]

    def _write_meas_info(self, metainfo):
        pass

    def _write_noks(self, metainfo):
        self._write_label_ext(metainfo, 'NOKs', NOKs, NOKs_label)

    def _write_slits(self, metainfo):
        self._write_label_ext(metainfo, 'Slits', Slits, Slits_label)
        self._write_label_ext(metainfo, 'Slits', simple_slit, [''])

    def _write_label_ext(self, metainfo, key, liste, ext):
        for ele in liste:
            for label in ext:
                s = ele + label
                if (s, 'value') in metainfo:
                    self._data[key][s] = (metainfo[s, 'value'][0])

    def _write_lateral(self, metainfo):
        self._write_label_ext(metainfo, 'Lateral', lateral, lateral_label)
        self._write_label_ext(metainfo, 'Lateral', simple_lateral,
                              simple_lateral_label)

    def _write_misc(self, metainfo):
        for dev in Miscellaneous:
            if (dev, 'value') in metainfo:
                self._data['Miscellaneous'][dev] = metainfo[dev, 'value'][0]

    def _write_vsd(self, metainfo):
        for dev in VSD:
            if (dev, 'value') in metainfo:
                self._data['vsd'][dev] = metainfo[dev, 'value'][0]

    def _write_optic(self, metainfo):
        self._write_label_ext(metainfo, 'optic', optic, optic_label)

    def _write_cpt(self, metainfo):
        for i in range(cpt[1]):
            dev = cpt[0] + '%d' % (i + 1)
            try:  # SB hack for setup cpt not loaded
                self._data['cpt'][dev] = metainfo[dev, 'value'][0]
            except KeyError:
                pass

    def _write_analog_encoder(self, metainfo):
        keys = list(metainfo.keys())
        for tup in keys:
            if tup[1] == 'value' and analog_encoder in tup[0]:
                element_part.append(tup[0])
                self._data['analog_encoder'][tup[0]] = metainfo[tup[0],
                                                                'value'][0]

    def _write_detector_params(self, metainfo):
        detparams = self._data['Detector Parameters']

        det = self._dict()
        detparams['detector'] = det

    def _write_detector(self, metainfo):
        for dev in det_pos:
            if (dev, 'value') in metainfo:
                self._data['Detector'][dev] = metainfo[dev, 'value'][0]

    def _write_monitor(self, metainfo):
        self._write_label_ext(metainfo, 'Monitor', monitor, monitor_label)

    def _write_chopper(self, metainfo):
        for devname in chopper:
            if (devname, 'value') in metainfo:
                self._data['Chopper'][devname] = metainfo[devname, 'value'][0]
            else:
                dev, key = devname.split('/')
                if (dev, key) in metainfo:
                    self._data['Chopper']['%s' % devname.replace('/', '_')] = \
                        metainfo[dev, key][0]
                else:
                    self.log.warning('missing %s', devname)
        self.log.debug('chopper_mode %s',
                       metainfo['chopper', 'mode'][0])

    def _write_sample(self, metainfo):
        sample = self._dict()
        for dev in Gonio:
            if (dev, 'value') in metainfo:
                sample[dev] = metainfo[dev, 'value'][0]
        self._data['Sample'] = sample

    def _write_extra(self, metainfo, elements):
        extra = self._dict()
        for dev in elements:
            if (dev, 'value') in metainfo:
                extra[dev] = metainfo[dev, 'value'][0]
        self._data['Extra'] = extra

    def putMetainfo(self, metainfo):
        self.log.debug('ADD META INFO %r', metainfo)
        keys = list(metainfo.keys())
        tmp = keys[0]
        self.log.debug('tmp type %s, value %s', type(tmp), tmp)

        if self._data:
            self._write_meas_info(metainfo)
            self._write_meas_comment(metainfo)
            self._write_chopper(metainfo)
            # self._write_detector_params(metainfo)
            self._write_detector(metainfo)
            self._write_monitor(metainfo)
            self._write_optic(metainfo)
            self._write_noks(metainfo)
            self._write_slits(metainfo)
            self._write_lateral(metainfo)
            self._write_sample(metainfo)
            self._write_misc(metainfo)
            self._write_vsd(metainfo)
            self._write_cpt(metainfo)
            self._write_analog_encoder(metainfo)

        elements = []
        for tup in keys:
            if tup[0] not in elements and \
               tup[0] not in element_part:
                elements.append(tup[0])
        if elements:
            self.log.debug('EXTRA %s', str(elements))

        if self._data:
            # should be empty
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
        'commentchar': Override(default='#'),
    }
