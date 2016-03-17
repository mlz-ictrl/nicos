#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Base data sink classes (new API) for TOFTOF."""

from nicos.core import Override, Param
from nicos.core.data import DataSinkHandler
from nicos.devices.datasinks.image import ImageSink


class TofSinkHandler(DataSinkHandler):

    def __init__(self, sink, dataset, detector):
        DataSinkHandler.__init__(self, sink, dataset, detector)
        self._datafile = None
        self._subdir = sink.subdir
        self._template = sink.filenametemplate
        arrayinfo = self.detector.arrayInfo()
        if len(arrayinfo) > 1:
            self.log.warning('image sink only supports one array per detector')
        self._arrayinfo = arrayinfo[0]


class TofSink(ImageSink):

    parameters = {
        'detinfofile': Param('Path to the detector-info file',
                             type=str, settable=False,
                             default='custom/toftof/detinfo.dat',
                             # mandatory=True,
                             ),
    }

    parameter_overrides = {
        'filenametemplate': Override(mandatory=False, settable=False,
                                     userparam=False,
                                     default=['%(pointcounter)s_0000.raw',
                                              '%(proposal)s_%(scancounter)s'
                                              '_%(pointnumber)s.raw']),
    }

    def doInit(self, mode):
        self._import_detinfo()

    def _import_detinfo(self):
        with open(self.detinfofile, 'U') as fp:
            self._detinfo = list(fp)
        for line in self._detinfo:
            if not line.startswith('#'):
                break
        dmap = {}  # maps "Total" (ElNr) to 2theta
        dinfo = [None]  # dinfo[EntryNr]
        for line in self._detinfo:
            if not line.startswith('#'):
                ls = line.split()
                if 'None' not in ls[13]:
                    dmap[int(ls[12])] = float(ls[5])
                dinfo.append(
                    list(map(int, ls[:5])) + [float(ls[5])] +
                    list(map(int, ls[6:8])) + [float(ls[8])] +
                    list(map(int, ls[9:13])) +
                    [' '.join(ls[13:-2]).strip("'")] +
                    list(map(int, ls[-2:]))
                )
        self._detinfolength = len(dinfo)
        self._detinfo_parsed = dinfo
        self.log.debug(self._detinfo_parsed)
        self._anglemap = tuple((i - 1) for i in sorted(dmap,
                                                       key=dmap.__getitem__))
