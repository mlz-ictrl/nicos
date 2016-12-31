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
#   Björn Pedersen <bjoern.pedersen@frm2.tum.de>
#
# *****************************************************************************

# line to long
# pylint: disable=C0301
"""Writes esmeralda compatible hbin images.

The header looks like::

   !!---- Example of header written in a binary file, the first item is the total length of the header string
   !!---- ===================================================================================================
   !!---- Header_Length:   1264
   !!---- Title: sucrose at RTD19 SCC   SCC 01-Sep-11 16:39:15 Summed Omega-range: [ -33.000 -26.000]
   !!---- N_Frames:      1
   !!---- Nbits:   16
   !!---- Nrow-Ncol:    256   640
   !!---- Detector_Type: CYLINDRICAL
   !!---- ColRow_Order: Column_Order
   !!---- Pixel_size_h:      2.50000
   !!---- Pixel_size_v:      1.56350
   !!---- Scan_Type: Summed-Omega
   !!---- Scan Values:    -33.00000     0.07000   -26.00000
   !!---- N_vector_Items:      3
   !!---- Vector item #  1 (hkl-min):     5.37751   -12.52532    -0.18949
   !!---- Vector item #  2 (hkl-max):     0.00000     0.00000     0.00000
   !!---- Vector item #  3 (delta-hkl):     0.00000     0.00000     0.00000
   !!---- N_matrix_Items:      1
   !!---- Matrix item #  1 (UB-matrix):  -0.021241  -0.011520  -0.033343   0.001907   0.037429  -0.014147   0.020302  -0.005238  -0.011123
   !!---- Time   :   2997.00000
   !!---- Monitor:      6000.00
   !!---- Counts : 210666.00000
   !!---- N_environment:      4
   !!---- Environment item #  1 (Temp-set):    15.00000~Kelvin
   !!---- Environment item #  2 (Temp-regul):    15.00700~Kelvin
   !!---- Environment item #  3 (Temp-sample):  9999.99023~Kelvin
   !!---- Environment item #  4 (Magnetic Field):     0.00000~Tesla
   !!---- N_motors:      5
   !!---- Motor item #  1 (Gamma):    62.00300~Degrees
   !!---- Motor item #  2 (Omega):     8.00000~Degrees
   !!---- Motor item #  3 (Chi):   179.00999~Degrees
   !!---- Motor item #  4 (Phi):     0.01000~Degrees
   !!---- Motor item #  5 (Psi):     0.00000~Degrees
   !!---- ..... binary data follows the line above


.. note::
   the binary data starts with:
   4*(3 + nmots + nenv) 4-byte binary data (time, monitor, counts + motor vals + env vals)
   followed by the image data
"""

import numpy
import struct

from nicos.core import ImageSink
from nicos.core.utils import DeviceValueDict


HEADER = \
'''Image_Offset:  %(imageoffset)s bytes
Header_Length:   %(headerlen)s bytes
Title: %(title)s
Instrument_Name: MLZ nLaue
N_Frames:      1
Nbits:   16
Nrow-Ncol:    %(rows)s   %(cols)s
Detector_Type: FLAT
ColRow_Order: Column_Order
Pixel_size_h(mm): 0.128
Pixel_size_v(mm): 0.128
Sample_Detector_Dist(mm): %(detdist)s
Lambda range(angstroms):  0.5 4.0
Scan_Type: Omega
Scan Values:    %(start)s     %(step)s   %(end)s
Sigma_Factor:      1.00000
Normalization_Tim:      0.00000
Normalization_Mon:      0.00000
Time   :   %(exposuretime)s
Monitor:      %(mon)s
Counts : %(sumcounts)s
'''


# TODO: port to new data API
class HBINLaueFileFormat(ImageSink):

    fileFormat = 'HBIN'

    def acceptImageType(self, imageType):
        # Note: FITS would be capable of saving multiple images in one file
        # (as 3. dimension). May be implemented if necessary. For now, only
        # 2D data is supported.
        return (len(imageType.shape) == 2)

    def prepareImage(self, imageinfo, subdir=''):
        """should prepare an Imagefile in the given subdir"""
        ImageSink.prepareImage(self, imageinfo, subdir)
        imageinfo.data = DeviceValueDict()

    def saveImage(self, info, data):
        # ensure numpy type, with float values for PIL
        npData = numpy.asarray(data, dtype='<u2')
        self.log.info('shape: %s', npData.shape)
        info.data['cols'] = npData.shape[0]
        info.data['rows'] = npData.shape[1]

        info.data['sumcounts']= 1 # npData.sum() is overflowing the INT needed.
        header = self._buildHeader(info)

        info.file.write(header + npData.tostring())

    def _buildHeader(self, imageinfo):
        header = ''
        prevheaderlen = -1
        # map items
        imageinfo.data['exposuretime'] = imageinfo.dataset.preset.get('t',0)
        imageinfo.data['mon'] = 1 #TODO: adapt once a real monitor is in place
        # TODO: adapt if we change the setup for detz in the HUBER controller
        imageinfo.data['detdist'] = 300- float(imageinfo.data['detz'])

        # pre-generate environment and motor parts
        binhead = self._buildBinHeaderPart(imageinfo)
        epart = self._buildEnvHeaderPart(imageinfo)
        mpart = self._buildMotorHeaderPart(imageinfo)
        while len(header) != prevheaderlen:
            imageinfo.data['headerlen'] = prevheaderlen = len(header)
            imageinfo.data['imageoffset'] = len(header) + len(binhead)
            header = HEADER % (imageinfo.data)
            # can not  be addaed via the DeviceValueDict, newline in strings get escaped
            header += epart
            header += mpart

        header += binhead
        return header

    def _buildBinHeaderPart(self, imageinfo):
        headerpart = ''

        etime = int(imageinfo.data['exposuretime'])
        counts = int(imageinfo.data['sumcounts'])
        monitor = int(imageinfo.data['mon'])

        headerpart += struct.pack('<3I', etime, counts, monitor)
        headerpart += self._buildMotorHeaderPart(imageinfo, True)
        headerpart += self._buildEnvHeaderPart(imageinfo, True)
        return headerpart

    def hbinDeviceIter(self, imageinfo, getbin, strformat, binformat, devs):
        headerpart = ''
        for i, dev in enumerate(devs):
            key = '%s' % dev
            ukey = '%s.unit' % dev
            data = dict(i=i, name=dev, value=imageinfo.data[key], unit=imageinfo.data[ukey])
            if getbin:
                try:
                    value = float(data['value'] or 0)
                except ValueError:
                    value = 0.
                headerpart += struct.pack(binformat, value)
            else:
                headerpart += strformat % data
        return headerpart

    def _buildEnvHeaderPart(self, imageinfo, getbin=False):
        FORMAT = 'Environment item #  %(i)s (%(name)s):    %(value)s~%(unit)s\n'
        BINFORMAT = '<f'
        ENVIRONS = ['Ts', 'T']
        if getbin:
            headerpart = ''
        else:
            headerpart = 'N_environment:      %d\n' % len(ENVIRONS)
        headerpart += self.hbinDeviceIter(imageinfo, getbin, FORMAT, BINFORMAT, ENVIRONS)
        return headerpart

    def _buildMotorHeaderPart(self, imageinfo, getbin=False):
        FORMAT = 'Motor item #  %(i)d (%(name)s):    %(value)s~%(unit)s\n'
        BINFORMAT = '<f'
        MOTORS = ['twotheta', 'omega', 'kappa', 'phi', 'detz']
        if getbin:
            headerpart = ''
        else:
            headerpart = 'N_motors:      %d\n' % len(MOTORS)
        headerpart += self.hbinDeviceIter(imageinfo, getbin, FORMAT, BINFORMAT, MOTORS)
        return headerpart
