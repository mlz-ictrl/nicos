# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
from nicos.core import status as ncstatus
from nicos.core.constants import FINAL, POINT
from nicos.devices.datasinks import FileSink
from nicos.utils import AutoDefaultODict

# if these labels apear as part of a key, they are "known"
element_part = [
    'FAK40_Cap',
    'FAK40_Press',
    'Space',
    'timer',
    'mon1',
    'mon2',
    'REFSANS',
    'det',
    'Sixfold',
    'Exp',
    'image',
    'rate',
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
aperture_keys = ['value', 'alias']

Slits = ['b1', 'zb0', 'zb1', 'zb2', 'zb3', 'bs1', 'b2', 'b3']
Slits_label = ['', '_mode']
Slits_PlanB_label = ['r_motor', 's_motor', 'r_analog', 's_analog', '_analog',
                     '_motor', 'r_motor', 's_motor']

simple_slit = ['sc2', 'disc3', 'disc4']

lateral = ['h2', 'h3']
lateral_label = ['width', 'center']

det_pos = [
    'det_drift',
    'det_pivot',
    'det_pix_height',
    'det_pix_width',
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
    'hv_anode',
    'hv_drift1',
    'hv_drift2',
    'hv_mon',
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
    'safedetectorsystem',
    'shutter',
    'shutter_gamma',
    'pressure_SR',
    'pressure_SFK',
    'pressure_CB',
    'chamber_CB',
    'chamber_SFK',
    'chamber_SR',
    'NL2b',
    'ReactorPower',
    'Crane',
]

safetysystem = [
    'doors',
    'place',
    'PO_save',
    'shutter_permission',
    'service',
    'SR_save',
    'supervisor',
    'personalkey',
    'Freigabe_Taster',
    'techOK',
    'Safedetectorsystem',
    'user_safetysystem_interface',
]

VSD = [
    'ChopperEnable2',
    'ChopperEnable1',
    'chopper_expertvibro',
    'chopper_no_Warning',
    'chopper_vibration_ok',
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
    'julabo_ext', 'julabo_int', 'julabo_temp', 'julabo_flow', 'julabo_flow_avg',
    'active_regulator',
    'pump0_diameter', 'pump0_rate', 'pump0_run',
    'pump1_diameter', 'pump1_rate', 'pump1_run',
    'nima_area', 'nima_pressure', 'nima_speed', 'nima_z',
]

# element_part += simple_slit
# element_part += Gonio
# element_part += VSD
# element_part += safetysystem
# element_part += det_pos
# element_part += aperture
# element_part += monitor
# element_part += Miscellaneous
# element_part += environment
# element_part += ['shutter_gamma_motor']
#
# for ll in optic:
#     for label in optic_label:
#         element_part.append(ll + label)
#
# for ll in NOKs:
#     for label in NOKs_label + NOKs_PlanB_label:
#         element_part.append(ll + label)
#
# for ll in PlanB:
#     for label in PlanB_label:
#         element_part.append(ll + label)
#
# for ll in ana4gpio:
#     for label in ana4gpio_label:
#         element_part.append(ll + label)
#
# for ll in monitor:
#     for label in monitor_label:
#         element_part.append(ll + label)
#
# for ll in lateral:
#     for label in lateral_label:
#         element_part.append(ll + label)
#
# for ll in Slits:
#     for label in Slits_label + Slits_PlanB_label:
#         element_part.append(ll + label)
# element_part.append('b3h3_frame')
#
# for i in range(cpt0[1]):
#     element_part.append('%s%d' % (cpt0[0], i))
#
# for i in range(cpt[1]):
#     element_part.append('%s%d' % (cpt[0], i))
#
# for i in range(cptoptic[1]):
#     element_part.append('%s%d' % (cptoptic[0], i + 1))

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
        self._processed = []

    def prepare(self):
        if configobj:
            if self._data is None:
                self._data = configobj.ConfigObj(encoding='utf-8')
                self._processed = element_part.copy()
            self._number = self.manager.assignCounter(self.dataset)
            fp = self.manager.createDataFile(self.dataset, self._template[0])
            self._data.filename = fp.filepath
            fp.close()
            self._data.initial_comment = ['Start Time %.2f' % time.time(), '',
                                          '']

            self._data['measurement'] = self._dict()
            self._data['Chopper'] = self._dict()
            self._data['NOKs'] = self._dict()
            self._data['NOKs_mode'] = self._dict()
            # self._data['motor'] = self._dict()
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
            self._data['sample environment'] = self._dict()

    def _write_meas_comment(self, metainfo):
        self._data['measurement'] = self._dict()
        self._data['measurement']['File Name'] = self._data.filename
        self._data['measurement']['Start Time'] = time.strftime(TIMEFMT)
        # self._data['measurement']['Measurement Comment'] = metainfo[
        #     'Exp', 'remark'][0]
        self.dataAllocation('measurement', 'Measurement Comment',
                            ('Exp', 'remark'), metainfo)
        ds = self.dataset
        self.log.debug('self.dataset: %s', type(self.dataset))
        self.log.debug('self.dataset: %s', self.dataset)
        scaninfo = ds.info.split('-')[-1].strip()
        if self._data:
            self._data['measurement']['scaninfo'] = scaninfo
        # self._data['measurement']['usercomment'] = metainfo.get(
        #     ('det', 'usercomment'), ['None'])[0]
        self.dataAllocation('measurement', 'usercomment',
                            ('det', 'usercomment'), metainfo)
        for dev in REFSANS:
            # self._data['measurement'][dev] = metainfo[
            #     'REFSANS', dev][0]
            self.dataAllocation('measurement', dev, ('REFSANS', dev), metainfo)
        # self._data['measurement']['Sample Name'] = '%s' % metainfo[
        #     'Sample', 'samplename'][0]
        self.dataAllocation('measurement', 'Sample Name', ('Sample', 'samplename'), metainfo)
        for dev in EXP:
            # self._data['measurement'][dev] = '%s' % metainfo['Exp', dev][0]
            self.dataAllocation('measurement', dev, ('Exp', dev), metainfo)

    def _write_noks(self, metainfo):
        self._write_label_ext(metainfo, 'NOKs', NOKs, 'value', [''], ['reactor', 'sample'])
        self._write_label_ext(metainfo, 'NOKs_mode', NOKs, 'mode', [''])

    def _write_AbsPos(self, metainfo):
        for dev, _key in metainfo:
            if _key == 'value':
                sp = dev.split('_')
                if sp[-1] == 'motor':
                    self.dataAllocation('Absolute_Positions', dev,
                                        (dev, 'value'), metainfo)

    def _write_slits(self, metainfo):
        for dev in ['b3h3_frame']:
            if (dev, 'value') in metainfo:
                self.dataAllocation('Slits', dev, (dev, 'value'), metainfo)
        self._write_label_ext(metainfo, 'Slits', Slits, 'value', [''], ['center', 'height'])
        self._write_label_ext(metainfo, 'Slits_mode', Slits, 'mode', [''])
        self._write_label_ext(metainfo, 'Slits', simple_slit, 'value', [''])

    def _write_label_ext(self, metainfo, key, liste, content, ext, tags=None):
        for ele in liste:
            for label in ext:
                sub = ele + label
                if (sub, content) in metainfo:
                    try:
                        if sub not in self._processed:
                            self._processed.append(sub)
                        vals = (metainfo[sub, content][0])
                        if tags is None or isinstance(vals, float):
                            self._data[key][sub] = vals
                        else:
                            # self._data[key][sub] = vals
                            for tag, val in zip(tags, vals):
                                self._data[key][sub + '_' + tag] = val
                    except Exception:
                        self._data[key][ele + label] = 'except: FAIL'

    def _write_lateral(self, metainfo):
        self._write_label_ext(metainfo, 'Lateral', lateral, 'value', [''],
                              lateral_label)

    def _write_misc(self, metainfo):
        for dev in Miscellaneous:
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['Miscellaneous'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('Miscellaneous', dev, (dev, 'value'),
                                    metainfo)

    def _write_vsd(self, metainfo):
        for dev in VSD:
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['vsd'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('vsd', dev, (dev, 'value'), metainfo)

    def _write_safetysystem(self, metainfo):
        for dev in safetysystem:
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['safetysystem'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('safetysystem', dev, (dev, 'value'), metainfo)

    def _write_environment(self, metainfo):
        for dev in environment:
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['sample environment'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('sample environment', dev, (dev, 'value'),
                                    metainfo)

    def _write_optic(self, metainfo):
        self._write_label_ext(metainfo, 'optic', optic, 'value', optic_label)
        self._write_label_ext(metainfo, 'optic_mode', optic, 'mode',
                              optic_label)

    def _write_cpt(self, metainfo):
        for i in range(cpt0[1]):
            dev = '%s%d' % (cpt0[0], i)
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['cpt'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('cpt', dev, (dev, 'value'), metainfo)
        for i in range(cpt[1]):
            dev = '%s%d' % (cpt[0], i)
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['cpt'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('cpt', dev, (dev, 'value'), metainfo)
        for i in range(cptoptic[1]):
            dev = '%s%d' % (cptoptic[0], (i + 1))
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['cpt'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('cpt', dev, (dev, 'value'), metainfo)

    def _write_attenuators(self, metainfo):
        keys = list(metainfo.keys())
        for tup in keys:
            if tup[1] == 'value' and attenuator in tup[0]:
                # element_part.append(tup[0])
                # self._processed.append(tup[0])
                # self._data['Attenuators'][tup[0]] = metainfo[tup[0],
                #                                              'value'][0]
                self.dataAllocation('Attenuators', tup[0], (tup[0], 'value'),
                                    metainfo)

    def _write_analog_encoder(self, metainfo):
        keys = list(metainfo.keys())
        for tup in keys:
            if tup[1] == 'value' and analog_encoder in tup[0]:
                # element_part.append(tup[0])
                # self._processed.append(tup[0])
                # self._data['analog_encoder'][tup[0]] = metainfo[tup[0],
                #                                                 'value'][0]
                self.dataAllocation('analog_encoder', tup[0], (tup[0], 'value'),
                                    metainfo)

    def _write_detector(self, metainfo):
        for dev in det_pos:
            if (dev, 'value') in metainfo:
                # self._processed.append(dev)
                # self._data['Detector'][dev] = metainfo[dev, 'value'][0]
                self.dataAllocation('Detector', dev, (dev, 'value'), metainfo)

    def _write_aperture(self, metainfo):
        for dev in aperture:
            if dev not in element_part:
                self._processed.append(dev)
            for key in aperture_keys:
                if (dev, key) in metainfo:
                    self.dataAllocation('aperture', f'{dev}_{key}',
                                        (dev, key), metainfo)
                else:
                    self.log.warning('missing %s %s', dev, key)

    def _write_monitor(self, metainfo):
        self._write_label_ext(metainfo, 'Monitor', monitor, 'value',
                              monitor_label)

    def dataAllocation(self, keys, name, metatag, metainfo):
        target = self._data
        if isinstance(keys, str):
            if keys not in target:
                target[keys] = self._dict()
            target = target[keys]
        elif len(keys) == 1:
            if keys[0] not in target:
                target[keys[0]] = self._dict()
            target = target[keys[0]]
        else:
            for key in keys:
                if key not in target:
                    target[key] = {}
                target = target[key]
        if metatag in metainfo:
            target[name] = metainfo[metatag][0]
            if False:   # manual Test only
                if type(target[name]) in [
                    int,
                    float,
                    str,
                    bool,
                    None,
                   ]:
                    pass
                else:
                    # line = 'typerror:'
                    self.log.debug('typerror: %s %s %s', name, type(target[name]), target[name])
                    self.log.info('typerror: %s %s %s', name, type(target[name]), target[name])
                    self.log.error('typerror: %s %s %s', name, type(target[name]), target[name])
                    # self.log.error(name)
                    # self.log.error(target[name])
                    # self.log.error(type(target[name]))
            # if metatag[0] not in element_part:
            #     element_part.append(metatag[0])
            if metatag[0] not in self._processed:
                self._processed.append(metatag[0])
            if metatag[1] == 'value':
                target[name + '_unit'] = metainfo[metatag][2]

                st = metainfo[(metatag[0], 'status')]
                if st[0][0] != ncstatus.OK:
                    target[name + '_status'] = st[0][1]
        else:
            self.log.warning('missing %s', metatag)
            target[name] = 'missing'

    def _write_chopper(self, metainfo):

        for devname in [
            (['Chopper', 'chopper_config_args'], 'wlmin', ('chopper', 'wlmin')),
            (['Chopper', 'chopper_config_args'], 'wlmax', ('chopper', 'wlmax')),
            (['Chopper', 'chopper_config_args'], 'D_disk1_detector_m', ('chopper', 'dist')),
            (['Chopper', 'chopper_config_args'], 'duty_cycle', ('chopper', 'duty_cycle')),
            (['Chopper', 'chopper_config_args'], 'disc2_pos', ('chopper', 'disc2_pos')),
            (['Chopper', 'chopper_config_args'], 'suppress_overlap', ('chopper', 'suppress_overlap')),

            (['Chopper', 'chopper_actual'], 'chopper_wlmin', ('chopper', 'chopper_wlmin')),
            (['Chopper', 'chopper_actual'], 'chopper_wlmax', ('chopper', 'chopper_wlmax')),
            (['Chopper', 'chopper_actual'], 'resolution_pct', ('resolution', 'value')),
            (['Chopper', 'chopper_actual'], 'flightpath_m', ('real_flight_path', 'value')),
            (['Chopper', 'chopper_actual'], 'disk2_mode', ('chopper', 'mode')),
            (['Chopper', 'chopper_actual'], 'disc2_pos', ('disc2_pos', 'value')),
            (['Chopper', 'chopper_actual'], 'chopper_rpm_setpoint', ('chopper', 'chopper_rpm_setpoint')),
            (['Chopper', 'chopper_actual'], 'chopper_rpm', ('chopper_speed', 'value')),
           ]:
            self.dataAllocation(devname[0], devname[1], devname[2], metainfo)

    def _write_sample(self, metainfo):
        sample = self._dict()
        for devname in Gonio:
            if (devname, 'value') in metainfo:
                self._processed.append(devname)
                sample[devname] = metainfo[devname, 'value'][0]
            else:
                key = tuple(devname.split('/'))
                if key in metainfo:
                    self._processed.append(key[1])
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
            # self._write_motor(metainfo)
            self._write_AbsPos(metainfo)
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

        # self.log.debug('metainfo: %s' + type(metainfo))
        self.log.debug('metainfo: %s', metainfo)
        self.log.debug('metainfo: %s', list(metainfo.keys()))
        # elements = []
        # for key in metainfo:
        #     self.log.debug('%35s: %s', key, metainfo[key])

        # for dev, _key in metainfo:
        #     if dev not in elements + element_part:
        #         elements.append(dev)
        #     if elements:
        #         self.log.debug('EXTRA ele %d %s', len(elements), elements)

        # self.log.debug('metainfo: %s', type(metainfo))
        self.log.debug('metainfo: %s', metainfo)
        self.log.debug('metainfo: %s', list(metainfo.keys()))
        # for key in metainfo.keys():
        #     self.log.debug('%35s: %s', key, metainfo[key])
        self.log.debug('work on element_part self._processed')
        extra = []
        for dev, _key in metainfo:
            if dev not in self._processed and dev not in extra:
                extra.append(dev)
        if len(extra) > 0:
            self.log.debug('EXTRA ext %d %s', len(extra), extra)
            self._write_extra(metainfo, extra)

        # elements = []
        # for dev, _key in metainfo:
        #     if dev not in elements + element_part:
        #         elements.append(dev)
        #     if elements:
        #         self.log.debug('EXTRA ele %d %s', len(elements), elements)

        self.log.debug('work on element_part self._processed')
        extra = []
        for dev, _key in metainfo:
            if dev not in self._processed and dev not in extra:
                extra.append(dev)
        if len(extra) > 0:
            self.log.debug('EXTRA ext %d %s', len(extra), extra)
            self._write_extra(metainfo, extra)

        # if self._data:
        #     # should be empty
        #     self._write_extra(metainfo, elements)
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
