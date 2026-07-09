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

"""Nexus data template for tomography applications."""

from nicos.nexus.elements import DeviceDataset, ImageDataset, \
    NexusElementBase, NXAttribute, NXLink

from nicos_mlz.nexus import MLZTemplateProvider, axis0, axis1, axis2, signal


class TomoImageDataset(ImageDataset):

    def testAppend(self, sinkhandler):
        self.doAppend = True


class DetectorSize(NexusElementBase):

    def __init__(self, detectorIDX, imageIDX, ax, **attrs):
        NexusElementBase.__init__(self)
        self.detectorIDX = detectorIDX
        self.imageIDX = imageIDX
        self.attrs = attrs
        self.doAppend = False
        self._axis = ax

    def create(self, name, h5parent, sinkhandler):
        det = sinkhandler.dataset.detectors[self.detectorIDX]
        arinfo = det.arrayInfo()
        myDesc = arinfo[self.imageIDX]
        rawshape = myDesc.shape[self._axis]
        dset = h5parent.create_dataset(name, (rawshape,), dtype=int)
        dset[:] = list(range(rawshape))
        self.createAttributes(dset, sinkhandler)


class TomoTemplateProvider(MLZTemplateProvider):

    definition = 'NXtomo'

    def init(self, **kwargs):
        MLZTemplateProvider.init(self, **kwargs)
        self.stx = kwargs.get('stx', 'stx')
        self.sty = kwargs.get('sty', 'sty')
        self.sry = kwargs.get('sry', 'sry')

    def updateDetector(self):
        self._det.update({
            'data': TomoImageDataset(0, 0, signal=signal, units='counts'),
            'image_key': DeviceDataset('image_key', defaultval=0),
            'x': DetectorSize(0, 0, 0, axis=axis1),
            'y': DetectorSize(0, 0, 1, axis=axis2),
        })

    def updateSample(self):
        self._sample.update({
            'rotation_angle': DeviceDataset(self.sry, axis=axis0),
            'x_translation': DeviceDataset(self.stx),
            'y_translation': DeviceDataset(self.sty),
        })
        MLZTemplateProvider.updateSample(self)

    def updateData(self):
        MLZTemplateProvider.updateData(self)
        self._entry['data:NXdata'].update({
            'rotation_angle': NXLink(f'/{self.entry}/sample/rotation_angle'),
            'x': NXLink(f'/{self.entry}/{self.instrument}/{self.detector}/x'),
            'y': NXLink(f'/{self.entry}/{self.instrument}/{self.detector}/y'),
            'image_key': NXLink(
                f'/{self.entry}/{self.instrument}/{self.detector}/image_key'),
            'axes': NXAttribute(['rotation_angle', 'y', 'x'], dtype='string'),
            'rotation_angle_indices': axis0,
            'y_indices': axis1,
            'x_indices': axis2,
        })
