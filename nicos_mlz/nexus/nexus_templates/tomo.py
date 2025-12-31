# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""Nexus data template for Antares."""

from nicos.nexus.elements import DeviceDataset, ImageDataset, NXLink

from nicos_mlz.nexus import MLZTemplateProvider, axis1, signal


class TomoTemplateProvider(MLZTemplateProvider):

    definition = 'NXtomo'

    def init(self, **kwargs):
        self.stx = kwargs.get('stx', 'stx')
        self.sty = kwargs.get('sty', 'sty')
        self.sry = kwargs.get('sry', 'sry')

    def updateInstrument(self):
        pass

    def updateDetector(self):
        self._det.update({
            'data': ImageDataset(0, 0, dtype=int, signal=signal),
            'image_key': DeviceDataset('image_key'),
        })

    def updateSample(self):
        self._sample.update({
            'rotation_angle': DeviceDataset(self.sry, axis=axis1),
            'x_translation': DeviceDataset(self.stx),
            'y_translation': DeviceDataset(self.sty),
        })

    def updateData(self):
        self._entry['data:NXdata'].update({
            'rotation_angle': NXLink(f'/{self.entry}/sample/rotation_angle'),
            'image_key': NXLink(
                f'/{self.entry}/{self.instrument}/{self.detector}/image_key'),
        })
