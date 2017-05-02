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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""CARESS histogram file format."""

from time import strftime, time as currenttime

from nicos.core import Override
from nicos.core.constants import POINT
from nicos.devices.datasinks.image import ImageSink, SingleFileSinkHandler
from nicos.pycompat import iteritems, to_utf8


class CaressHistogramHandler(SingleFileSinkHandler):
    """Handler for the CaressHistogram data sink."""

    filetype = 'caresshistogram'

    def __init__(self, sink, dataset, detector):
        SingleFileSinkHandler.__init__(self, sink, dataset, detector)

    def writeHeader(self, fp, metainfo, image):
        pass

    def writeData(self, fp, image):
        _metainfo = self.dataset.metainfo
        bycategory = {}
        detectors = self.sink.detectors
        for (dev, key), (_, v, _, cat) in iteritems(_metainfo):
            if dev in detectors + ['UBahn', 'Space', 'tths'] and \
               cat == 'general':
                continue
            if cat:
                bycategory.setdefault(cat, []).append((dev, key, v,))
        detector = detectors[0] if detectors else 'adet'
        _comment = 'monrate = %.1f ' % _metainfo[detector, 'rates'][0][0]
        if 'general' in bycategory:
            for device, _key, value in bycategory['general']:
                if _key == 'value':
                    _comment += '%s = %s ' % (device, value)
        _resosteps = _metainfo[detector, 'resosteps'][0]
        _range = _metainfo[detector, 'range'][0]
        _stepsize = _range / _resosteps
        _startpos = _metainfo[detector, '_startpos'][0]
        _start = _startpos - (_resosteps - 1) * _stepsize
        _acqtime = (self.dataset.finished or currenttime()) - \
            self.dataset.started
        _total_counts = image.sum()

        # for d, k in _metainfo.keys():
        #     self.log.debug('writeData: %s.%s', d, k)
        #     if d == detector:
        #         self.log.info(' %s.%s %r', d, k, _metainfo[d, k])

        header = []
        date = strftime('%d.%m.%Y')
        time = strftime('%H:%M:%S')
        header.append('QMesyDAQ CARESS Histogram File  %s  %s' % (date, time))
        header.append('')
        header.append('Run:\t%d' % self.dataset.counter)
        header.append('Resosteps:\t%d' % _resosteps)
        header.append('2Theta start:\t%.2f' % _start)
        header.append('2Theta range:\t%.2f' % _range)
        header.append('')
        header.append('Comment:\t%s' % _comment)
        header.append('')
        header.append('Acquisition Time\t%d' % _acqtime)
        header.append('Total Counts\t%d' % _total_counts)
        if _metainfo[detector, 'mode'][0] == 'time':
            header.append('Preset timer seconds:\t%.0f' %
                          _metainfo[detector, 'preset'][0])
        else:
            header.append('Preset monitor_1 counts:\t%d' %
                          _metainfo[detector, 'preset'][0])
        header.append('')
        header.append('CARESS XY data: 1 row title (position numbers), then '
                      '(resosteps x 80) position data in columns')
        header.append('\t' + '\t'.join(['%d' % x for x in range(1, 255)]))

        # write Header
        for line in header:
            fp.write(to_utf8('%s\n' % line))

        for i, v in enumerate(image):
            _pos = _start + i * _stepsize
            fp.write(to_utf8('%.2f\t%s\n' %
                             (_pos, '\t'.join(['%d' % x for x in v]))))
        fp.write(b'\n')

        fp.write(b'total sum\n')
        for i, v in enumerate(image):
            _pos = _start + i * _stepsize
            fp.write(to_utf8('%.2f\t%d\n' % (_pos, v.sum())))

        fp.flush()


class CaressHistogram(ImageSink):
    """Data sink for the CARESS histogram file format.

    The CARESS histogram file is a derivation of the QMesyDAQ histogram file
    format. It writes a simple header then the histogram data in a table where
    the number are substituted by the angle position. At the end the sum of the
    neutrons in each tube will be written in respect to the angle of the tube
    at measurement time.
    """

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['run%(pointcounter)07d.ctxt']),
        'settypes': Override(default=[POINT]),
    }

    handlerclass = CaressHistogramHandler

    def isActiveForArray(self, arraydesc):
        return len(arraydesc.shape) == 2
