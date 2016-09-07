#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

from time import sleep

import numpy as np

from nicos.core import Param, Override, Value, Attach, ArrayDesc, Readable, \
    SIMULATION, tupleof, oneof
from nicos.core.data import GzipFile
from nicos.devices.datasinks.raw import SingleRawImageSink
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.devices.generic.detector import ActiveChannel
from nicos.devices.tas.mono import Monochromator, to_k, from_k
from nicos.devices.tango import ImageChannel


class CascadeDetector(ImageChannel):
    """Detector channel for the CASCADE-MIEZE detector.

    Controls the detector via a connection to a Tango server.
    """

    parameters = {
        'roi':      Param('Region of interest, given as (x1, y1, x2, y2)',
                          type=tupleof(int, int, int, int),
                          default=(-1, -1, -1, -1), settable=True),
        'mode':     Param('Data acquisition mode (tof or image)',
                          type=oneof('tof', 'image'), settable=True,
                          volatile=True),
        'fitfoil':  Param('Foil for contrast fitting', type=int, default=0,
                          settable=True),
    }

    parameter_overrides = {
        'fmtstr':   Override(default='roi %s, total %s, file %s'),
    }

    #
    # parameter handlers
    #

    def doReadMode(self):
        if self._dev.timeChannels == 1:
            return 'image'
        return 'tof'

    def doWriteMode(self, value):
        self._dev.timeChannels = 128 if value == 'tof' else 1

    def doUpdateMode(self, value):
        self._dataprefix = (value == 'image') and 'IMAG' or 'DATA'
        self._datashape = (value == 'image') and (128, 128) or (128, 128, 128)
        self._tres = (value == 'image') and 1 or 128

    #
    # Device interface
    #

    def doPreinit(self, mode):
        ImageChannel.doPreinit(self, mode)
        if mode != SIMULATION:
            self.doReset()

    def doInit(self, mode):
        # self._tres is set by doUpdateMode
        self._xres, self._yres = (128, 128)

    def doReset(self):
        oldmode = self.mode
        self._dev.Reset()
        # reset parameters in case the server forgot them
        self.log.info('re-setting to %s mode' % oldmode.upper())
        self.doWriteMode(oldmode)
        self.doWritePreselection(self.preselection)

    #
    # Channel interface
    #

    def doStart(self):
        if self.mode == 'image':
            self.readresult = [0, 0]
        else:
            self.readresult = [0, 0, 0., 0., 0., 0.]
        sleep(0.005)
        self._dev.Start()

    def doFinish(self):
        self._dev.Stop()

    def doStop(self):
        self.doFinish()

    def valueInfo(self):
        cvals = (Value(self.name + '.roi', unit='cts', type='counter',
                       errors='sqrt', active=self.roi != (-1, -1, -1, -1),
                       fmtstr='%d'),
                 Value(self.name + '.total', unit='cts', type='counter',
                       errors='sqrt', fmtstr='%d'))
        if self.mode == 'tof':
            cvals = cvals + (Value(self.name + '.c_roi', unit='',
                                   type='counter', errors='next',
                                   fmtstr='%.4f'),
                             Value(self.name + '.dc_roi', unit='',
                                   type='error', fmtstr='%.4f'),
                             Value(self.name + '.c_tot', unit='',
                                   type='counter', errors='next',
                                   fmtstr='%.4f'),
                             Value(self.name + '.dc_tot', unit='',
                                   type='error', fmtstr='%.4f'))
        return cvals

    @property
    def arraydesc(self):
        if self.mode == 'image':
            return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y'])
        return ArrayDesc('data', self._datashape, '<u4', ['X', 'Y', 'T'])

    def doReadArray(self, quality):
        # get current data array from detector
        data = self._dev.value.reshape(self._datashape)
        # determine total and roi counts
        total = data.sum()
        ctotal, dctotal = 0., 0.
        # XXX implement for MIEZE
        # if self.mode == 'tof':
        #     ctotal =
        #     dctotal =
        if self.roi != (-1, -1, -1, -1):
            x1, y1, x2, y2 = self.roi
            roi = data[x1:x2, y1:y2].sum()
            croi, dcroi = 0., 0.
            # XXX implement for MIEZE
            # if self.mode == 'tof':
            #     croi =
            #     dcroi =
        else:
            roi = total
            croi, dcroi = ctotal, dctotal
        if self.mode == 'tof':
            self.readresult = [roi, total, croi, dcroi, ctotal, dctotal]
        else:
            self.readresult = [roi, total]
        # make a numpy array and reshape it correctly
        return data


class CascadePadSink(SingleRawImageSink):

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.pad'],
                                     settable=False),
    }

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2


class CascadeTofSink(SingleRawImageSink):

    parameter_overrides = {
        'filenametemplate': Override(default=['%(pointcounter)08d.tof'],
                                     settable=False),
    }

    fileclass = GzipFile

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 3


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

        w, h = image.shape
        if self.sink._format is None or self.sink._format[0] != image.shape:
            p = []
            for _x in range(w):
                for fx in range(1024 / w):
                    for _y in range(h):
                        for fy in range(1024 / h):
                            if fx % 4 == 0 and fy % 4 == 0:
                                p.append('%f ')
                            else:
                                p.append('0 ')
                    p.append('\n')
            self.sink._format = (image.shape, ''.join(p))

        filled = np.repeat(np.repeat(image, 256 / w, 0), 256 / h, 1)
        write(self.sink._format[1] % tuple(filled.ravel() / 4))

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
