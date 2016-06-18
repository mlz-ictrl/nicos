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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""KWS-1 file format saver with YAML."""

from nicos import session
from nicos.core import Override
from nicos.devices.datasinks.image import ImageSink
from nicos.frm2.yamlbase import YAMLBaseFileSinkHandler


class YAMLFileSinkHandler(YAMLBaseFileSinkHandler):

    filetype = 'MLZ.KWS1.2.0-beta1'

    def _write_instr_data(self, meas, image):
        expdev = session.experiment

        hist = meas['history']
        hist['duration_counted'] = self._readdev('timer')[0]
        hist['duration_scheduled'] = self._devpar('timer', 'preselection')
        hist['termination_reason'] = self._devpar('timer', 'name')

        sample = meas['sample']['description']
        sample['time_factor'] = expdev.sample.timefactor
        sample['length'] = expdev.sample.thickness
        sample['detector_offset'] = expdev.sample.detoffset
        sample['comment'] = expdev.sample.comment

        orient = meas['sample']['orientation']
        orient['rotation_angle'] = self._readdev('sam_rot')
        orient['x_displacement'] = self._readdev('sam_trans_x')
        orient['y_displacement'] = self._readdev('sam_trans_y')

        if 'hexapod' in session.loaded_setups:
            hexapod = orient['hexapod']
            hexapod['table_angle'] = self._readdev('hexapod_dt')
            hexapod['x_angle'] = self._readdev('hexapod_rx')
            hexapod['y_angle'] = self._readdev('hexapod_ry')
            hexapod['z_angle'] = self._readdev('hexapod_rz')
            hexapod['x_displacement'] = self._readdev('hexapod_tx')
            hexapod['y_displacement'] = self._readdev('hexapod_ty')
            hexapod['z_displacement'] = self._readdev('hexapod_tz')

        setup = meas['setup']
        selector = setup['velocity_selector']
        selector['preset'] = self._readdev('selector')
        selector['wavelength'] = self._readdev('selector_lambda')
        selector['frequency'] = self._readdev('selector_speed',
                                              lambda x: x / 60.)

        chopper = setup['chopper']
        chopper['preset'] = self._readdev('chopper')
        if chopper['preset'] != 'off':
            chopper['frequency'] = self._readdev('chopper_params',
                                                 lambda x: x[0])
            chopper['opening_angle'] = self._readdev('chopper_params',
                                                     lambda x: x[1])

        _collslit = 'aperture_%02d' % self._readdev('coll_guides')
        coll = setup['collimation']
        coll['preset'] = self._readdev('collimation')
        coll['length'] = self._readdev('coll_guides')
        coll['aperture']['width'] = self._readdev(_collslit, lambda x: x[0])
        coll['aperture']['height'] = self._readdev(_collslit, lambda x: x[1])

        pol = setup['polarizer']
        pol_state = self._readdev('polarizer')
        pol['is_in_place'] = pol_state not in (None, 'out')

        if pol['is_in_place']:
            flipper = setup['flipper']
            flipper['is_in_place'] = True
            flipper['setting'] = pol_state

        det = setup['detector']
        det['preset'] = self._readdev('detector')
        det['z_displacement'] = self._readdev('det_z') * 1000
        det['x_displacement'] = self._readdev('det_x')
        det['y_displacement'] = self._readdev('det_y')

        slit = setup['sample_aperture']
        slit['upper_clearance'] = self._readdev('ap_sam_y1')
        slit['lower_clearance'] = self._readdev('ap_sam_y0')
        slit['left_clearance'] = self._readdev('ap_sam_x0')
        slit['right_clearance'] = self._readdev('ap_sam_x1')

        meas['monitors'] = self._flowlist([
            self._readdev('mon1', lambda x: x[0]),
            self._readdev('mon2', lambda x: x[0]),
            self._readdev('mon3', lambda x: x[0]),
        ])

        det1 = self._dict()
        det1['type'] = 'position_sensitive_detector'
        det1['is_in_place'] = True
        detimg = session.getDevice('det_img')
        uses_tof = detimg.mode == 'tof'
        if uses_tof:
            tof = meas['setup']['time_of_flight']
            tof['number_of_channels'] = image.shape[2]
            tof['channel_duration'] = self._flowlist(
                [d / 1000000. for d in detimg.slices])
            det1['axes'] = self._flowlist(['x', 'y', 'tof'])
        else:
            det1['axes'] = self._flowlist(['x', 'y'])
        det1['pixel_width'] = 5.3
        det1['pixel_height'] = 5.3
        counts = det1['counts']
        for i in range(image.shape[0]):
            if len(image.shape) == 2:
                counts[i] = self._flowlist(map(int, image[i]))
            else:
                for j in range(image.shape[1]):
                    counts[i][j] = self._flowlist(map(int, image[i][j]))
        det1['total_counts'] = int(image.sum())
        meas['detectors'] = [det1]


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

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
