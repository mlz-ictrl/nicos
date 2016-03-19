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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

name = 'test_data setup'

includes = ['stdsystem', 'scanning']

sinklist = ['testsink', 'asciisink', 'consolesink', 'daemonsink',
            'livesink', 'rawsink', 'srawsink', 'bersanssink']

# These sinks cannot be created if the modules are not present.
# Omit them from the datasinks list in that case.

try:
    import PIL  # pylint: disable=unused-import
    sinklist.append('tiffsink')
except Exception:
    pass

try:
    import pyfits  # pylint: disable=unused-import
    sinklist.append('fitssink')
except Exception:
    pass

sysconfig = dict(
    datasinks = sinklist,
)

devices = dict(
    asciisink   = device('nicos.devices.datasinks.AsciiScanfileSink'),
    consolesink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink  = device('nicos.devices.datasinks.DaemonSink'),
    livesink    = device('nicos.devices.datasinks.LiveViewSink'),
    rawsink     = device('nicos.devices.datasinks.RawImageSink'),
    srawsink    = device('nicos.devices.datasinks.SingleRawImageSink',
                         subdir = 'single',
                         filenametemplate = ['%(scancounter)s_%(pointcounter)s.raw',
                                             '/%(pointcounter)08d.raw']),
    bersanssink = device('nicos.sans1.bersans.BerSANSImageSink',
                         flipimage = 'none'),
    fitssink    = device('nicos.devices.datasinks.FITSImageSink'),
    tiffsink    = device('nicos.devices.datasinks.TIFFImageSink'),
)
