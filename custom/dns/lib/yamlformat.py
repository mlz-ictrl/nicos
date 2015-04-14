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
#   Stefanie Keuler <s.keuler@fz-juelich.de>
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""DNS file format saver for the new YAML based format."""

from time import time as currenttime
from datetime import datetime
from collections import OrderedDict

import yaml

from nicos import session
from nicos.core import Override, NicosError
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.pycompat import from_maybe_utf8


# Subclass to support creation of nested dicts easily
class AutoDefaultODict(OrderedDict):
    def __missing__(self, key):
        val = self[key] = self.__class__()
        return val


# Subclass to support flowed (inline) lists
class FlowSeq(list):
    pass


# The improved YAML dumper
class ImprovedDumper(yaml.Dumper):
    pass


def odict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())


def flowseq_representer(dumper, data):
    return dumper.represent_sequence(
        yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG,
        data, flow_style=True)

ImprovedDumper.add_representer(AutoDefaultODict, odict_representer)
ImprovedDumper.add_representer(FlowSeq, flowseq_representer)
ImprovedDumper.add_representer(
    str, yaml.representer.SafeRepresenter.represent_str)
ImprovedDumper.add_representer(
    unicode, yaml.representer.SafeRepresenter.represent_unicode)


def improved_dump(data, stream=None, **kwds):
    return yaml.dump(data, stream, ImprovedDumper, allow_unicode=True,
                     encoding='utf-8', default_flow_style=False, indent=4,
                     width=70, **kwds)


def nice_datetime(dt):
    if isinstance(dt, float):
        dt = datetime.fromtimestamp(dt)
    rounded = dt.replace(microsecond=0)
    return rounded.isoformat()


class YAMLFileSinkHandler(SingleFileSinkHandler):

    filetype = 'DNS-YAML'
    accept_final_images_only = True

    def writeData(self, fp, image):
        """Save in YAML format."""

        fp.seek(0)

        expdev = session.experiment
        instrdev = session.instrument

        def readdev(devname):
            try:
                return session.getDevice(devname).read()
            except NicosError:
                return None

        def devpar(devname, parname):
            try:
                return getattr(session.getDevice(devname), parname)
            except NicosError:
                return None

        o = AutoDefaultODict()
        instr = o['instrument']
        instr['name'] = instrdev.instrument
        instr['facility'] = instrdev.facility
        # TODO: add instrument params for these two, once this migrates from DNS
        instr['operator'] = u'Jülich Centre for Neutron Science (JCNS)'
        instr['website'] = 'http://www.mlz-garching.de/dns'
        instr['references'] = [AutoDefaultODict({'doi': instrdev.doi})]

        objects = ['angle', 'clearance', 'current', 'displacement', 'duration',
                   'energy', 'frequency', 'temperature', 'wavelength']
        units = ['deg', 'mm', 'A', 'mm', 's', 'eV', 'hertz', 'K', 'A']

        o['format']['identifier'] = 'MLZ.DNS.2.0-beta3'
        for obj, unit in zip(objects, units):
            o['format']['units'][obj] = unit

        exp = o['experiment']
        # TODO: use experiment number when we have it in NICOS
        exp['number'] = expdev.proposal
        exp['proposal'] = expdev.proposal
        exp['title'] = from_maybe_utf8(expdev.title)
        exp['authors'] = []
        authors = [
            {'name': from_maybe_utf8(expdev.users),
             'roles': ['principal_investigator']},
            {'name':  from_maybe_utf8(expdev.localcontact),
             'roles': ['local_contact']},
        ]
        for author in authors:
            a = AutoDefaultODict()
            a['name'] = author['name']
            a['roles'] = FlowSeq(author['roles'])
            exp['authors'].append(a)

        meas = o['measurement']
        meas['number'] = self.dataset.number
        meas['unique_identifier'] = '%s/%s/%s' % (
            expdev.proposal, self.dataset.counter, self.dataset.number)

        hist = meas['history']
        hist['started'] = nice_datetime(self.dataset.started)
        hist['stopped'] = nice_datetime(currenttime())
        hist['duration_counted'] = readdev('timer')[0]
        hist['duration_scheduled'] = devpar('timer', 'preselection')
        hist['termination_reason'] = devpar('timer', 'name')

        sample = meas['sample']['description']
        sample['name'] = from_maybe_utf8(expdev.sample.samplename)
        # TODO: one we have a better sample object
        # sample['kind'] = 'Vanadium' etc.
        # sample['unit_cell'] = from_maybe_utf8(expdev.sample.description)
        # sample['spacegroup'] = 'not looked up'

        temp = meas['sample']['temperature']
        temp['environment'] = devpar('T', 'description')
        # TODO: replace by true mean once we keep track with the new data API
        temp['setpoint']['mean'] = devpar('T', 'setpoint')
        temp['T1']['mean'] = readdev('T_jlc3_tube')
        temp['T2']['mean'] = readdev('Ts')

        orient = meas['sample']['orientation']
        orient['rotation_angle'] = readdev('sample_rot')
        orient['lower_cradle_angle'] = readdev('cradle_lo')
        orient['upper_cradle_angle'] = readdev('cradle_up')

        settings = meas['setup']['settings_for']
        lam = readdev('mon_lambda')
        energy = 81.804165 / lam**2
        settings['incident_wavelength'] = lam
        settings['incident_energy'] = energy

        mono = meas['setup']['monochromator']
        mono['crystal'] = 'PG-002'
        mono['angle'] = readdev('mon_rot')

        selector = meas['setup']['velocity_selector']
        if 'selector_speed' in session.devices:
            selector['is_in_place'] = readdev('selector_inbeam') == 'in'
            if selector['is_in_place']:
                selector['frequency'] = readdev('selector_speed')

        polarizer = meas['setup']['polarizer']
        polarizer['is_in_place'] = readdev('pol_inbeam') == 'in'
        if polarizer['is_in_place']:
            polarizer['displacement'] = readdev('pol_trans')
            polarizer['rotation_angle'] = readdev('pol_rot')

        flipper = meas['setup']['flipper']
        flipper['is_in_place'] = readdev('flipper_inbeam') == 'in'
        if flipper['is_in_place']:
            flipper['setting'] = readdev('flipper')
            flipper['precession_current'] = readdev('Co')
            flipper['z_compensation_current'] = readdev('Fi')

        slit = meas['setup']['slit_i']
        slit['upper_clearance'] = readdev('ap_sam_y_upper')
        slit['lower_clearance'] = readdev('ap_sam_y_lower')
        slit['left_clearance'] = readdev('ap_sam_x_left')
        slit['right_clearance'] = readdev('ap_sam_x_right')

        coil = meas['setup']['xyz_coil']
        if 'field' in session.devices:
            coil['is_in_place'] = readdev('xyzcoil_inbeam') == 'in'
            if coil['is_in_place']:
                coil['coil_a_current'] = readdev('A')
                coil['coil_b_current'] = readdev('B')
                coil['coil_c_current'] = readdev('C')
                coil['coil_zb_current'] = readdev('ZB')
                coil['coil_zt_current'] = readdev('ZT')

        meas['setup']['polarization'] = readdev('field')

        monitor = meas['monitor']
        if 'mon0' in session.devices:
            monitor['is_in_place'] = True
            monitor['counts'] = readdev('mon0')[0]
        else:
            monitor['is_in_place'] = False

        nrtimechan = 1
        chanwidth = 0
        tofdelay = 0
        uses_chopper = False
        meas['detectors'] = []
        det1 = AutoDefaultODict()
        det1['type'] = 'polarization_analyser_detector_bank'
        if 'det' in expdev.detlist:
            tofchan = session.getDevice('dettof')
            uses_chopper = tofchan.tofmode == 'tof'
            det1['is_in_place'] = True
            if tofchan.tofmode == 'tof':
                nrtimechan = tofchan.nrtimechan
                chanwidth = tofchan.divisor / 1000000.
                tofdelay = tofchan.offsetdelay / 1000000.
                det1['axes'] = FlowSeq(['tube', 'time'])
            else:
                det1['axes'] = FlowSeq(['tube'])
            start, end = tofchan.readchannels
            det1['angle_tube0'] = readdev('det_rot') - 5*start
            det1['angle_step'] = -5
            det1['number_of_tubes'] = end - start + 1
            total = 0
            for j in range(start, end + 1):
                det_counts = [int(v) for v in image[:, j]]
                if len(det_counts) > 1:
                    det1['counts'][j] = FlowSeq(det_counts)
                else:
                    det1['counts'][j] = det_counts[0]
                total += image[:, j].sum()
            det1['total_counts'] = int(total)
        else:
            det1['is_in_place'] = False
        meas['setup']['time_of_flight']['number_of_channels'] = nrtimechan
        meas['setup']['time_of_flight']['delay_duration'] = tofdelay
        meas['setup']['time_of_flight']['channel_duration'] = chanwidth
        meas['setup']['settings_for']['uses_chopper'] = uses_chopper
        meas['detectors'].append(det1)

        det2 = AutoDefaultODict()
        det2['type'] = 'position_sensitive_detector_bank'
        det2['is_in_place'] = False  # 'qm_det' in expdev.detlist
        meas['detectors'].append(det2)

        improved_dump(o, fp)
        fp.flush()


class YAMLFileSink(ImageSink):
    """Saves DNS image data and header in yaml format"""

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(proposal)s_'
                                              '%(pointcounter)010d.yaml'],
                                     ),
    }

    handlerclass = YAMLFileSinkHandler
