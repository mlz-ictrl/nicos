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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

name = 'test_data setup'

includes = ['stdsystem', 'scanning']

sinklist = [
    'testsink1',
    'testsink2',
    'asciisink',
    'consolesink',
    'daemonsink',
    'livesink',
    'rawsink',
    'srawsink',
    'bersanssink',
    'serialsink',
]

# These sinks cannot be created if the modules are not present.
# Omit them from the datasinks list in that case.

try:
    import PIL  # pylint: disable=unused-import
    sinklist.append('tiffsink')
except Exception:
    pass

try:
    import astropy.io.fits  # pylint: disable=unused-import
    sinklist.append('fitssink')
except Exception:
    try:
        import pyfits  # pylint: disable=unused-import
        sinklist.append('fitssink')
    except Exception:
        pass

try:
    import quickyaml  # pylint: disable=unused-import
    sinklist.append('yamlsink')
except Exception:
    pass

sysconfig = dict(datasinks = sinklist,)

devices = dict(
    testsink1 = device('test.utils.TestSink',
        settypes = ['scan'],
    ),
    testsink2 = device('test.utils.TestSink',
        settypes = ['point'],
        detectors = ['det'],
    ),
    serialsink = device('devices.datasinks.SerializedSink'),
    asciisink = device('devices.datasinks.AsciiScanfileSink'),
    consolesink = device('devices.datasinks.ConsoleScanSink'),
    daemonsink = device('devices.datasinks.DaemonSink'),
    livesink = device('devices.datasinks.LiveViewSink'),
    rawsink = device('devices.datasinks.RawImageSink',
        filenametemplate = [
            '%(proposal)s_%(pointpropcounter)s.raw', '%(pointcounter)08d.raw'
        ]
    ),
    srawsink = device('devices.datasinks.SingleRawImageSink',
        subdir = 'single',
        filenametemplate = [
            '%(scancounter)s_%(pointcounter)s.raw', '/%(pointcounter)08d.raw'
        ]
    ),
    bersanssink = device('nicos_mlz.sans1.devices.bersans.BerSANSImageSink'),
    # note: these four will only be created if their prerequisite modules
    # are installed (and they are present in *sinklist*) because device auto
    # creation is off for test sessions
    fitssink = device('devices.datasinks.FITSImageSink'),
    tiffsink = device('devices.datasinks.TIFFImageSink'),
    yamlsink = device('nicos_mlz.dns.devices.yamlformat.YAMLFileSink',
        filenametemplate = ['%(pointcounter)08d.yaml'],
    ),
)
