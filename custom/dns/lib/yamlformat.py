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
#   Stefanie Keuler <s.keuler@fz-juelich.de>
#   Lydia Fleischhauer-Fuss <l.fleischhauer-fuss@fz-juelich.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""DNS file format saver for the new YAML based format."""

import quickyaml

from nicos import session
from nicos.core import Override
from nicos.devices.datasinks.image import ImageSink
from nicos.frm2.yamlbase import YAMLBaseFileSinkHandler


class YAMLFileSinkHandler(YAMLBaseFileSinkHandler):

    filetype = 'MLZ.DNS.2.0-beta3'
    yaml_array_handling = quickyaml.ARRAY_AS_MAP

    def _write_instr_data(self, meas, image):
        expdev = session.experiment

        hist = meas['history']
        hist['duration_counted'] = self._readdev('timer')[0]
        hist['duration_scheduled'] = self._devpar('timer', 'preselection')
        hist['termination_reason'] = self._devpar('timer', 'name')

        # TODO: one we have a better sample object
        # sample = meas['sample']['description']
        # sample['kind'] = 'Vanadium' etc.
        # sample['unit_cell'] = from_maybe_utf8(expdev.sample.description)
        # sample['spacegroup'] = 'not looked up'

        temp = meas['sample']['temperature']
        temp['environment'] = self._devpar('T', 'description')
        # TODO: replace by true mean once we keep track with the new data API
        temp['setpoint']['mean'] = self._devpar('T', 'setpoint')
        temp['T1']['mean'] = self._readdev('T_jlc3_tube')
        temp['T2']['mean'] = self._readdev('Ts')

        orient = meas['sample']['orientation']
        orient['rotation_angle'] = self._readdev('sample_rot')
        orient['lower_cradle_angle'] = self._readdev('cradle_lo')
        orient['upper_cradle_angle'] = self._readdev('cradle_up')

        settings = meas['setup']['settings_for']
        lam = self._readdev('mon_lambda')
        if lam is not None:
            energy = 81.804165 / lam**2
        else:
            energy = None
        settings['incident_wavelength'] = lam
        settings['incident_energy'] = energy

        mono = meas['setup']['monochromator']
        mono['crystal'] = 'PG-002'
        mono['angle'] = self._readdev('mon_rot')

        selector = meas['setup']['velocity_selector']
        if 'selector_speed' in session.devices:
            selector['is_in_place'] = self._readdev('selector_inbeam') == 'in'
            if selector['is_in_place']:
                selector['frequency'] = self._readdev('selector_speed')

        polarizer = meas['setup']['polarizer']
        polarizer['is_in_place'] = self._readdev('pol_inbeam') == 'in'
        if polarizer['is_in_place']:
            polarizer['displacement'] = self._readdev('pol_trans')
            polarizer['rotation_angle'] = self._readdev('pol_rot')

        flipper = meas['setup']['flipper']
        flipper['is_in_place'] = self._readdev('flipper_inbeam') == 'in'
        if flipper['is_in_place']:
            flipper['setting'] = self._readdev('flipper')
            flipper['precession_current'] = self._readdev('Co')
            flipper['z_compensation_current'] = self._readdev('Fi')

        slit = meas['setup']['slit_i']
        slit['upper_clearance'] = self._readdev('ap_sam_y_upper')
        slit['lower_clearance'] = self._readdev('ap_sam_y_lower')
        slit['left_clearance'] = self._readdev('ap_sam_x_left')
        slit['right_clearance'] = self._readdev('ap_sam_x_right')

        coil = meas['setup']['xyz_coil']
        if 'field' in session.devices:
            coil['is_in_place'] = self._readdev('xyzcoil_inbeam') == 'in'
            if coil['is_in_place']:
                coil['coil_a_current'] = self._readdev('A')
                coil['coil_b_current'] = self._readdev('B')
                coil['coil_c_current'] = self._readdev('C')
                coil['coil_zb_current'] = self._readdev('ZB')
                coil['coil_zt_current'] = self._readdev('ZT')

        meas['setup']['polarization'] = self._readdev('field')

        monitor = meas['monitor']
        if 'mon1' in session.devices:
            monitor['is_in_place'] = True
            monitor['counts'] = self._readdev('mon1')[0]
        else:
            monitor['is_in_place'] = False

        timechannels = 1
        chanwidth = 0
        tofdelay = 0
        uses_chopper = False
        meas['detectors'] = []
        det1 = self._dict()
        det1['type'] = 'polarization_analyser_detector_bank'
        if 'det' in expdev.detlist:
            tofchan = session.getDevice('dettof')
            uses_chopper = tofchan.timechannels > 1
            det1['is_in_place'] = True
            if tofchan.timechannels > 1:
                timechannels = tofchan.timechannels
                chanwidth = tofchan.divisor / 1000000.
                tofdelay = tofchan.delay / 1000000.
                det1['axes'] = self._flowlist(['tube', 'time'])
            else:
                det1['axes'] = self._flowlist(['tube'])
            start, end = tofchan.readchannels
            det1['angle_tube0'] = self._readdev('det_rot') - 5*start
            det1['angle_step'] = -5
            det1['number_of_tubes'] = end - start + 1
            total = 0
            for j in range(start, end + 1):
                det_counts = [int(v) for v in image[:, j]]
                if len(det_counts) > 1:
                    det1['counts'][j] = self._flowlist(det_counts)
                else:
                    det1['counts'][j] = det_counts[0]
                total += image[:, j].sum()
            det1['total_counts'] = int(total)
        else:
            det1['is_in_place'] = False
        meas['setup']['time_of_flight']['number_of_channels'] = timechannels
        meas['setup']['time_of_flight']['delay_duration'] = tofdelay
        meas['setup']['time_of_flight']['channel_duration'] = chanwidth
        meas['setup']['settings_for']['uses_chopper'] = uses_chopper
        meas['detectors'].append(det1)

        det2 = self._dict()
        det2['type'] = 'position_sensitive_detector_bank'
        det2['is_in_place'] = False  # 'qm_det' in expdev.detlist
        meas['detectors'].append(det2)


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
