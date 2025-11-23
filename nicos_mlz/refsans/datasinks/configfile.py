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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************
"""ConfigObj data sink classes for REFSANS."""

import time

from nicos import session
from nicos.core import DataSinkHandler, NicosError, Override, Param, listof
from nicos.core.constants import FINAL, POINT
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
    'NL2b', 'Space', 'timer', 'Sample', 'mon1', 'mon2',
    # 'optic',
    'p_memograph_in',
    'p_memograph_out',
    'REFSANS', 'Crane', 'det', 'Sixfold', 'ReactorPower', 'Exp', 'image',
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
    'chopper2_pos',
    'chopper',
    'resolution',
    'chopper/mode',
    # 'chopper/resolution',
    'chopper_speed',
    'chopper/wlmin',
    'chopper/wlmax',
    'chopper/gap',
    'chopper/manner',
]

EXP = [
    'localcontact',
    'proposal',
    'remark',
    'title',
    'users',
]

REFSANS = [
    'doi',
    'facility',
    'instrument',
    'operators',
    'responsible',
    'website',
]

Gonio = [
    'gonio_omega',
    'gonio_phi',
    'gonio_theta',
    'gonio_z',
    'gonio_x',
    'sample_x_manual',
    'gonio_y',
    'gonio_top_phi',
    'gonio_top_theta',
    'gonio_top_z',
    'd_last_slit_sample',
    'height',
    'autocollimator_phi',
    'autocollimator_theta',
    'backguard',
    'backguard1',
    'backguard1_motor',
    'backguard2',
    'backguard2_motor',
    'samplechanger',
    'Sample/length',
    'Sample/width',
]

NOKs = [
    'nok2', 'nok3', 'nok4',
    'nok5a', 'nok5b', 'nok6', 'nok7', 'nok8', 'nok9',
]

NOKs_label = ['', '_mode']
NOKs_PlanB_label = ['r_motor', 's_motor', 'r_analog', 's_analog']

aperture = [
    'primary_aperture',
    'last_aperture',
]

Slits = ['b1', 'zb0', 'zb1', 'zb2', 'zb3', 'bs1', 'b2', 'b3']
Slits_label = ['', '_mode']
Slits_PlanB_label = ['r_motor', 's_motor', 'r_analog', 's_analog', '_analog',
                     '_motor', 'r_motor', 's_motor']

simple_slit = ['sc2', 'disc3', 'disc4']

lateral = ['h2']
lateral_label = ['', '_width', '_center']
simple_lateral = ['h3']
simple_lateral_label = ['', '_mode']

det_pos = [
    'det_drift',
    'det_pivot',
    'det_pixsize',
    'det_table',
    'det_table_cab_temp',
    'det_table_motor',
    'det_table_motor_temp',
    'det_table_poti',
    'det_table_raw',
    'det_type',
    'det_yoke',
    'det_yoke_enc',
    'primary_beam',
    'tube_angle',
    'primary_beam',
    'beamstop_height',
    'beamstop_center',
    'beamstop_asym',
]

PlanB = [
    'det_table',
]

PlanB_label = [
    '_motor',
]

ana4gpio = [
    'humidity',
    'ana4gpio02',
]

ana4gpio_label = [
    '_ch1',
    '_ch2',
    '_ch3',
    '_ch4',
]

optic = ['optic']
optic_label = ['', '.mode']

monitor = ['prim_monitor']
monitor_label = ['_typ', '_x', '_z']

Miscellaneous = [
    'sds',
    'shutter',
    'shutter_gamma',
    'pressure_SR',
    'pressure_SFK',
    'pressure_CB',
    'real_flight_path',  # as bad label
    'chamber_CB',
    'chamber_SFK',
    'chamber_SR',
    'hv_anode',
    'hv_drift1',
    'hv_drift2',
    'hv_mon',
]

safetysystem = [
    'doors',
    'place',
    'PO_save',
    'basis',
    'service',
    'SR_save',
    'supervisor',
    'personalkey',
    'Freigabe_Taster',
    'techOK',
    'Safedetectorsystem',
    'user',
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
    'X16Voltage1',
    'X16Voltage2',
    'X16Voltage3',
    'X16Voltage4',
]

cpt = ['cpt', 6 + 1]
cpt0 = ['cpt0', 1 + 1]
cptoptic = ['cptoptic', 4]

analog_encoder = '_acc'

attenuator = 'attenuator'

environment = [
    'julabo_ext', 'julabo_int', 'julabo_temp',
    'active_regulator',
    'pump0_diameter', 'pump0_rate', 'pump0_run',
    'pump1_diameter', 'pump1_rate', 'pump1_run',
    'nima_area', 'nima_pressure', 'nima_speed', 'nima_z',
]

element_part += chopper
element_part += simple_slit
element_part += Gonio
element_part += VSD
element_part += safetysystem
element_part += det_pos
element_part += aperture
element_part += monitor
element_part += Miscellaneous
element_part += environment
element_part += ['shutter_gamma_motor']

for ll in optic:
    for label in optic_label:
        element_part.append(ll + label)

for ll in NOKs:
    for label in NOKs_label + NOKs_PlanB_label:
        element_part.append(ll + label)

for ll in PlanB:
    for label in PlanB_label:
        element_part.append(ll + label)

for ll in ana4gpio:
    for label in ana4gpio_label:
        element_part.append(ll + label)

for ll in monitor:
    for label in monitor_label:
        element_part.append(ll + label)

for ll in lateral:
    for label in lateral_label:
        element_part.append(ll + label)

for ll in simple_lateral:
    for label in simple_lateral_label:
        element_part.append(ll + label)

for ll in Slits:
    for label in Slits_label + Slits_PlanB_label:
        element_part.append(ll + label)
element_part.append('b3h3_frame')

for i in range(cpt0[1]):
    element_part.append('%s%d' % (cpt0[0], i))

for i in range(cpt[1]):
    element_part.append('%s%d' % (cpt[0], i))

for i in range(cptoptic[1]):
    element_part.append('%s%d' % (cptoptic[0], i + 1))

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
        if configobj:
            if self._data is None:
                self._data = configobj.ConfigObj(encoding='utf-8')
            self._number = self.manager.assignCounter(self.dataset)
            fp = self.manager.createDataFile(self.dataset, self._template[0])
            self._data.filename = fp.filepath
            fp.close()
            self._data.initial_comment = ['Start Time %.2f' % time.time(), '',
                                          '']

            self._data['measurement'] = self._dict()
            self._data['Chopper'] = self._dict()
            self._data['chopper_config'] = self._dict()
            self._data['NOKs'] = self._dict()
            self._data['NOKs_mode'] = self._dict()
            self._data['Absolute_Positions'] = self._dict()
            self._data['Slits'] = self._dict()
            self._data['Slits_mode'] = self._dict()
            self._data['Lateral'] = self._dict()
            self._data['Sample'] = self._dict()
            self._data['Detector'] = self._dict()
            self._data['aperture'] = self._dict()
            self._data['Monitor'] = self._dict()
            self._data['Miscellaneous'] = self._dict()
            self._data['vsd'] = self._dict()
            self._data['safetysystem'] = self._dict()
            self._data['optic'] = self._dict()
            self._data['optic_mode'] = self._dict()
            self._data['cpt'] = self._dict()
            self._data['analog_encoder'] = self._dict()
            self._data['Attenuators'] = self._dict()
            self._data['environment'] = self._dict()

    def _write_meas_comment(self, metainfo):
        self._data['measurement'] = self._dict()
        self._data['measurement']['File Name'] = self._data.filename
        self._data['measurement']['Start Time'] = time.strftime(TIMEFMT)
        self._data['measurement']['Measurement Comment'] = metainfo[
            'Exp', 'remark'][0]
        ds = self.dataset
        scaninfo = ds.info.split('-')[-1].strip()
        if self._data:
            self._data['measurement']['scaninfo'] = scaninfo
        self._data['measurement']['usercomment'] = metainfo.get(
                ('det', 'usercomment'), ['None'])[0]
        for dev in REFSANS:
            self._data['measurement'][dev] = metainfo[
                'REFSANS', dev][0]
        self._data['measurement']['Sample Name'] = '%s' % metainfo[
            'Sample', 'samplename'][0]
        for dev in EXP:
            self._data['measurement'][dev] = '%s' % metainfo['Exp', dev][0]

    def _write_noks(self, metainfo):
        self._write_label_ext(metainfo, 'NOKs', NOKs, 'value', NOKs_label)
        self._write_label_ext(metainfo, 'NOKs_mode', NOKs, 'mode', NOKs_label)

    def _write_PlanB(self, metainfo):
        self._write_label_ext(metainfo, 'Absolute_Positions',
                              NOKs + ['shutter_gamma'], 'value',
                              NOKs_PlanB_label)
        self._write_label_ext(metainfo, 'Absolute_Positions', Slits, 'value',
                              Slits_PlanB_label)
        self._write_label_ext(metainfo, 'Absolute_Positions', PlanB, 'value',
                              PlanB_label)
        self._write_label_ext(metainfo, 'Absolute_Positions',
                              ana4gpio, 'value',
                              ana4gpio_label)
        if not self._data['Absolute_Positions']:
            self.log.warning('Absolute_Positions has no content!')

    def _write_slits(self, metainfo):
        for dev in ['b3h3_frame']:
            if (dev, 'value') in metainfo:
                self._data['Slits'][dev] = metainfo[dev, 'value'][0]
        self._write_label_ext(metainfo, 'Slits', Slits, 'value', Slits_label)
        self._write_label_ext(metainfo, 'Slits_mode', Slits, 'mode',
                              Slits_label)
        self._write_label_ext(metainfo, 'Slits', simple_slit, 'value', [''])

    def _write_label_ext(self, metainfo, key, liste, content, ext):
        for ele, label in zip(liste, ext):
            if (ele, 'value') in metainfo:
                self._data[key][ele + label] = (metainfo[ele, content][0])

    def _write_lateral(self, metainfo):
        self._write_label_ext(metainfo, 'Lateral', lateral, 'value',
                              lateral_label)
        self._write_label_ext(metainfo, 'Lateral', simple_lateral, 'value',
                              simple_lateral_label)

    def _write_misc(self, metainfo):
        for dev in Miscellaneous:
            if (dev, 'value') in metainfo:
                self._data['Miscellaneous'][dev] = metainfo[dev, 'value'][0]

    def _write_vsd(self, metainfo):
        for dev in VSD:
            if (dev, 'value') in metainfo:
                self._data['vsd'][dev] = metainfo[dev, 'value'][0]

    def _write_safetysystem(self, metainfo):
        for dev in safetysystem:
            if (dev, 'value') in metainfo:
                self._data['safetysystem'][dev] = metainfo[dev, 'value'][0]

    def _write_environment(self, metainfo):
        for dev in environment:
            if (dev, 'value') in metainfo:
                self._data['environment'][dev] = metainfo[dev, 'value'][0]

    def _write_optic(self, metainfo):
        self._write_label_ext(metainfo, 'optic', optic, 'value', optic_label)
        self._write_label_ext(metainfo, 'optic_mode', optic, 'mode',
                              optic_label)

    def _write_cpt(self, metainfo):
        for i in range(cpt0[1]):
            dev = '%s%d' % (cpt0[0], i)
            if (dev, 'value') in metainfo:
                self._data['cpt'][dev] = metainfo[dev, 'value'][0]
        for i in range(cpt[1]):
            dev = '%s%d' % (cpt[0], i)
            if (dev, 'value') in metainfo:
                self._data['cpt'][dev] = metainfo[dev, 'value'][0]
        for i in range(cptoptic[1]):
            dev = '%s%d' % (cptoptic[0], (i + 1))
            if (dev, 'value') in metainfo:
                self._data['cpt'][dev] = metainfo[dev, 'value'][0]

    def _write_attenuators(self, metainfo):
        keys = list(metainfo.keys())
        for tup in keys:
            if tup[1] == 'value' and attenuator in tup[0]:
                element_part.append(tup[0])
                self._data['Attenuators'][tup[0]] = metainfo[tup[0],
                                                             'value'][0]

    def _write_analog_encoder(self, metainfo):
        keys = list(metainfo.keys())
        for tup in keys:
            if tup[1] == 'value' and analog_encoder in tup[0]:
                element_part.append(tup[0])
                self._data['analog_encoder'][tup[0]] = metainfo[tup[0],
                                                                'value'][0]

    def _write_detector(self, metainfo):
        for dev in det_pos:
            if (dev, 'value') in metainfo:
                self._data['Detector'][dev] = metainfo[dev, 'value'][0]

    def _write_aperture(self, metainfo):
        for dev in aperture:
            for key in ['value', 'alias']:  # 'status' as well ?
                if (dev, key) in metainfo:
                    self._data['aperture']['%s_%s' % (dev, key)] = \
                        metainfo[dev, key][0]
                val = metainfo[dev, 'status'][0]
                self._data['aperture']['%s_%s_dyn' % (dev, 'status')] = val
                # 'b3.height' => (200,'slit=b3') 2020-04-06 06:42:08 JFM
                val = (metainfo[dev, 'status'][0][0],
                       'slit=' + metainfo[dev, 'alias'][0].split('.')[0])
                self._data['aperture']['%s_%s' % (dev, 'status')] = val

    def _write_monitor(self, metainfo):
        self._write_label_ext(metainfo, 'Monitor', monitor, 'value',
                              monitor_label)

    def _write_chopper(self, metainfo):
        # label = 'chopper_resolution'
        # self._data['Chopper'][label] = metainfo['chopper2_pos', 'value'][0]
        self._data['Chopper'] = self._dict()
        self._data['chopper_config'] = self._dict()
        self._data['Chopper']['chopper_rpm'] = metainfo['chopper_speed',
                                                        'value'][0]
        for devname in chopper:
            if (devname, 'value') in metainfo:
                self.log.debug('1. %s %s', devname, metainfo[devname,
                                                             'value'][0])
                if devname == 'chopper':
                    self.log.debug('%s', type(metainfo[devname, 'value'][0]))
                    for key in metainfo[devname, 'value'][0].keys():
                        self._data['chopper_config'][key] = \
                            metainfo[devname, 'value'][0][key]
                else:
                    self._data['Chopper'][devname] = metainfo[devname,
                                                              'value'][0]
            else:
                key = tuple(devname.split('/'))
                if key in metainfo:
                    self.log.debug('2. %s %s', key, metainfo[key][0])
                    self._data['Chopper']['%s_%s' % key] = metainfo[key][0]
                else:
                    self.log.warning('missing %s', devname)
        # self.log.debug('chopper_mode %s', metainfo['chopper', 'mode'][0])

    def _write_sample(self, metainfo):
        sample = self._dict()
        for devname in Gonio:
            if (devname, 'value') in metainfo:
                sample[devname] = metainfo[devname, 'value'][0]
            else:
                key = tuple(devname.split('/'))
                if key in metainfo:
                    sample[key[1]] = metainfo[key][0]
                elif devname == 'height':
                    self.log.debug('missing %s', devname)
                else:
                    self.log.warning('missing %s', devname)
        self._data['Sample'] = sample

    def _write_extra(self, metainfo, elements):
        extra = self._dict()
        for dev in elements:
            if (dev, 'value') in metainfo:
                extra[dev] = metainfo[dev, 'value'][0]
        self._data['Extra'] = extra

    def putMetainfo(self, metainfo):
        if self._data:
            self._write_meas_comment(metainfo)
            self._write_chopper(metainfo)
            self._write_detector(metainfo)
            self._write_monitor(metainfo)
            self._write_optic(metainfo)
            self._write_noks(metainfo)
            self._write_PlanB(metainfo)
            self._write_aperture(metainfo)
            self._write_slits(metainfo)
            self._write_lateral(metainfo)
            self._write_sample(metainfo)
            self._write_misc(metainfo)
            self._write_vsd(metainfo)
            self._write_safetysystem(metainfo)
            self._write_cpt(metainfo)
            self._write_analog_encoder(metainfo)
            self._write_attenuators(metainfo)
            self._write_environment(metainfo)
        else:
            self.log.debug('no self._data')
        elements = []
        for dev, _key in metainfo:
            if dev not in elements + element_part:
                elements.append(dev)
        if elements:
            self.log.debug('EXTRA %d %s', len(elements), elements)

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
        if quality == FINAL:
            dic = {}
            self._final_dic(self.dataset.detectors[0]._attached_images,
                            '.sum', dic)
            self._final_dic(self.dataset.detectors[0]._attached_monitors,
                            '', dic)
            self._final_dic(self.dataset.detectors[0]._attached_timers,
                            '', dic)
            self._final_dic(self.dataset.detectors[0]._attached_counters,
                            '', dic)
            if self._data:
                try:
                    self._data['final'] = dic
                    self._data.write()
                except Exception:
                    self.log.warning("'final' not written")

    def _final_dic(self, att, tag, dic):
        for data in att:
            for info, val in zip(self.dataset.detvalueinfo,
                                 self.dataset.detvaluelist):
                if data.name + tag == info.name:
                    dic[info.name] = val

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
    }
