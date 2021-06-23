#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
from nicos.core import Override, status
from nicos.core.data.dataset import ScanDataset
from nicos.core.data.sink import GzipFile
from nicos.core.utils import formatStatus
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.utils import byteBuffer

from nicos_mlz.devices.yamlbase import YAMLBaseFileSinkHandler


class YAMLFileSinkHandler(YAMLBaseFileSinkHandler):

    filetype = 'MLZ.KWS1.2.0-gamma1'

    objects = []
    units = []

    def _set_detector_resolution(self, det1):
        det_img = session.getDevice('det_img')
        det1['pixel_width'] = 8.0
        if getattr(det_img, 'rebin8x8', False):
            det1['pixel_height'] = 8.0
        else:
            det1['pixel_height'] = 4.0

    def _write_instr_data(self, meas, image):
        manager = session.experiment.data  # get datamanager
        # get corresponding scan dataset with scan info if available
        stack = manager._stack
        if len(stack) >= 2 and isinstance(stack[-2], ScanDataset):
            scands = stack[-2]
            meas['info'] = scands.info
        else:
            meas['info'] = self.dataset.info

        sample = session.experiment.sample
        meas['sample']['comment'] = sample.comment
        meas['sample']['timefactor'] = sample.timefactor
        meas['sample']['thickness'] = sample.thickness / 1000  # in m
        meas['sample']['detoffset'] = sample.detoffset / 1000

        det1 = self._dict()
        det1['type'] = 'position_sensitive_detector'
        det1['mode'] = self.dataset.metainfo['det_img', 'mode'][0]
        # the first entry in "slices" is always 0 in the TOF modes
        slices = self.dataset.metainfo['det_img', 'slices'][0][1:]
        det1['time_channels'] = len(slices) or 1
        det1['time_slices_us'] = self._flowlist(slices)
        det1['pixels_x'] = image.shape[-1]
        det1['pixels_y'] = image.shape[-2]
        self._set_detector_resolution(det1)
        values = det1['results'] = self._dict()
        for (info, val) in zip(self.dataset.detvalueinfo,
                               self.dataset.detvaluelist):
            values[info.name] = val
        det1['data'] = '<see .array file>'
        det1['dataformat'] = '32-bit integer'

        meas['detectors'] = [det1]

        # store device information
        deventries = {}

        for ((dev, key), meta) in sorted(self.dataset.metainfo.items()):
            if dev in ('Exp', 'Sample') or dev.startswith('KWS'):
                continue
            if meta[3] == 'limits':
                continue
            if dev not in deventries:
                deventry = deventries[dev] = self._dict()
                deventry['name'] = dev
            else:
                deventry = deventries[dev]
            if key == 'status':
                if meta[0][0] == status.OK:
                    continue
                deventry['status'] = formatStatus(meta[0])
                continue
            deventry[key] = meta[0]
            if key == 'value' and meta[2]:
                deventry['unit'] = meta[2]

        meas['devices'] = [
            entry for (_, entry) in sorted(deventries.items())
            if len(entry) > 1
        ]


NAME_TEMPLATE = (
    '%(pointcounter)08d_%(pointnumber)04d_'
    '%(proposal)s_'
    '%(session.experiment.sample.filename)s_'
    'C%(coll_guides)dm_'
    'D%(detector)s_'
    'L%(selector)s_'
    'P%(polarizer)s_'
    '%(det_img.mode)s.'
    '%(session.instrument.name)s'
)


class YAMLFileSink(ImageSink):
    """Saves DNS image data and header in yaml format"""

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=[NAME_TEMPLATE + '.yaml'],
                                     ),
    }

    handlerclass = YAMLFileSinkHandler

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) in (2, 3)


class BinarySinkHandler(SingleFileSinkHandler):
    """Numpy text format filesaver using `numpy.savetxt`"""

    filetype = 'arraygz'
    fileclass = GzipFile

    def writeData(self, fp, image):
        fp.write(byteBuffer(image.astype('<u4', 'C')))


class BinaryArraySink(ImageSink):
    handlerclass = BinarySinkHandler

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=[NAME_TEMPLATE + '.array.gz'],
                                     ),
    }
