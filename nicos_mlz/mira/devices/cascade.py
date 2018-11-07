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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Class for CASCADE detector measurement and readout."""

from __future__ import absolute_import, division, print_function

import numpy as np

from nicos.core import Attach, Override, Readable
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.devices.generic.detector import ActiveChannel
from nicos.devices.tas.mono import Monochromator, from_k, to_k


class MiraXmlHandler(SingleFileSinkHandler):
    filetype = 'xml'
    accept_final_images_only = True

    def writeData(self, fp, image):
        mon = self.sink._attached_monitor
        timer = self.sink._attached_timer
        mono = self.sink._attached_mono
        write = fp.write
        write('''\
<measurement_file>

<instrument_name>MIRA</instrument_name>
<location>Forschungsreaktor Muenchen II - FRM2</location>

<measurement_data>
<Sample_Detector>%d</Sample_Detector>
<wavelength>%.2f</wavelength>
<lifetime>%.3f</lifetime>
<beam_monitor>%d</beam_monitor>
<resolution>1024</resolution>

<detector_value>\n''' % (self.sink._attached_sampledet.read(),
                         from_k(to_k(mono.read(), mono.unit), 'A'),
                         timer.read()[0],
                         mon.read()[0]))

        h, w = image.shape
        if self.sink._format is None or self.sink._format[0] != image.shape:
            p = []
            for _x in range(w):
                for fx in range(1024 // w):
                    for _y in range(h):
                        for fy in range(1024 // h):
                            if fx % 4 == 0 and fy % 4 == 0:
                                p.append('%f ')
                            else:
                                p.append('0 ')
                    p.append('\n')
            self.sink._format = (image.shape, ''.join(p))

        filled = np.repeat(np.repeat(image, 256 // w, 0), 256 // h, 1)
        if filled.shape == (256, 256):
            write(self.sink._format[1] % tuple(filled.ravel() / 4.))

        write('''\
</detector_value>

</measurement_data>

</measurement_file>
''')


class MiraXmlSink(ImageSink):

    handlerclass = MiraXmlHandler

    attached_devices = {
        'timer':     Attach('Timer readout', ActiveChannel),
        'monitor':   Attach('Monitor readout', ActiveChannel),
        'mono':      Attach('Monochromator device to read out', Monochromator),
        'sampledet': Attach('Sample-detector distance readout', Readable),
    }

    parameter_overrides = {
        'filenametemplate': Override(default=['mira_cas_%(pointcounter)08d.xml'],
                                     settable=False),
    }

    _format = None

    def isActiveForArray(self, arraydesc):
        # only for 2-D data
        return len(arraydesc.shape) == 2
