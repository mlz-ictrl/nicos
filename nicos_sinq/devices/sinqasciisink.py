#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#
# *****************************************************************************
from __future__ import absolute_import, division, print_function

import re
import time

from nicos import session
from nicos.core import Override, Param, listof, nicosdev, tupleof
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos.core.data import DataSinkHandler
from nicos.devices.datasinks import FileSink


class SINQAsciiSinkHandler(DataSinkHandler):
    """
    The implementation is as such:
    - In appendResults() I collect all the scan data which is needed in the
      scanvalues dictionary. At the first point, the header is generated.
      This is the first point where enough data is there to do this.
    - In end(), the file is actually written
    This has the disadvantage that no data is written when NICOS dies on the
    way. But it simplifies the implementation by a lot.
    """
    header = None
    scanvalues = {}

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        self.manager.getFilenames(self.dataset, self.sink.filenametemplate,
                                  self.sink.subdir)

    def _findValue(self, dev, par):
        if (dev, par) in self.dataset.metainfo:
            value = self.dataset.metainfo[(dev, par)][1]
        else:
            value = 'UNKNOWN'
        return value

    def _initHeader(self):
        with open(self.sink.templatefile, 'r') as fin:
            template = fin.read()

        template = template.replace('!!FILE!!', self.dataset.filepaths[0])

        time_str = time.strftime('%Y-%m-%d %H:%M:%S',
                                 time.localtime(time.time()))
        template = template.replace('!!DATE!!', time_str)

        segments = re.split('!!.*?(.*?)!!', template)
        template = ''
        for morsel in segments:
            if morsel.startswith('VAR'):
                dev = morsel[4:-1]
                lsp = dev.split(',')
                if len(lsp) > 1:
                    dev = lsp[0]
                    par = lsp[1]
                else:
                    dev = lsp[0]
                    par = 'value'
                template += self._findValue(dev, par)
            elif morsel.startswith('ZERO'):
                dev = morsel[5:-1]
                template += self._findValue(dev, 'offset')
            elif morsel.startswith('DRIV'):
                dev = morsel[5:-1]
                template += self._findValue(dev, 'value')
            elif morsel.startswith('SCANZERO'):
                sc = ''
                for dev in self.dataset.devices:
                    off = self._findValue(dev.name, 'offset')
                    sc += dev.name + ' zero = ' + str(off) + ','
                template += sc.rstrip(',')
            elif morsel.startswith('SCRIPT'):
                script = morsel[7:-1]
                try:
                    # This is because of some auto quoting done by python
                    val = eval(script[1:-1])
                except Exception as e:
                    val = str(e)
                template += val
            else:
                template += morsel

        self.header = template

        for dev in self.dataset.devices:
            self.scanvalues[dev.name] = []

        for _, det in self.sink.scaninfo:
            self.scanvalues[det] = []

    def addSubset(self, point):
        if point.settype != POINT:
            return

        if point.number == 1:
            self._initHeader()

        for i in range(len(self.dataset.devices)):
            self.scanvalues[self.dataset.devices[i].name].append(
                point.devvaluelist[i])

        for _, det in self.sink.scaninfo:
            if det in point.values:
                self.scanvalues[det].append(point.values[det])
            else:
                session.log.warning('Detector %s not found when saving scan '
                                    'data', det)

    def end(self):
        with open(self.dataset.filepaths[0], 'w') as out:
            out.write(self.header)

            # Do the scan variable and steps line
            steps = []
            out.write('Scanning Variables: ')
            for dev in self.dataset.devices:
                out.write(dev.name + ',')
                vals = self.scanvalues[dev.name]
                if len(vals) > 1:
                    steps.append(str(vals[1] - vals[0]))
                else:
                    steps.append(str(.0))
            out.write(' Steps: ')
            out.write(', '.join(steps))
            out.write('\n')

            # Do the scan parameter line
            out.write('%d Points, ' % (self.dataset.npoints))
            m = list(self.dataset.preset.keys())[0]
            if m == 't':
                mode = 'Timer'
            else:
                mode = 'Monitor'
            out.write('Mode: ' + mode + ',')
            mp = self.dataset.preset.values()
            preset = list(mp)[0]
            out.write('Preset %f\n' % (preset))

            # Scan data header
            out.write('%-4s' % 'NP')
            for dev in self.dataset.devices:
                out.write('%-9s' % dev.name)
            for cter, _ in self.sink.scaninfo:
                out.write('%-11s' % cter)
            out.write('\n')

            # The actual scan data...
            name = self.dataset.devices[0].name
            for np in range(len(self.scanvalues[name])):
                out.write('%-4d' % np)
                for dev in self.dataset.devices:
                    val = self.scanvalues[dev.name][np]
                    out.write('%-9.4f' % val)
                for _, cter in self.sink.scaninfo:
                    val = self.scanvalues[cter][np]
                    if isinstance(val, int):
                        out.write('%-11d' % val)
                    else:
                        out.write('%-8.3f   ' % val)
                out.write('\n')

            out.write('END-OF-DATA\n')


class SINQAsciiSink(FileSink):
    """
    This is a filesink which writes scan data files in the SINQ ASCII format.
    The implementation strives to be as compatible as possible to the old
    format as written by SICS. SINQ ASCII files are constructed from a
    template file. This template file contains ASCII text which is copied
    verbatim to the output intermixed with place holder strings. These are
    replaced with data from NICOS. In addition, the actual data from the
    scan is collected and written too. The special placeholders recognized
    are:
    - !!VAR(dev,par)!! is replaced with the value of the parameter par of
                        device dev. Par can be missing and is then value.
    - !!DRIV(dev)!! replaced by the value of dev
    - !!ZERO(dev)!! replaced by the offset of dev. Dev must be a motor
    - !!SCRIPT(txt)!! replaced by the output of running script txt
    - !!DATE!!  replaced by the current date and time
    - !!FILE!! replaced by the original file path of the scan file
    - !!SCANZERO!! replaced by a list of zero points of the scanned devices
    There is some redundancy here but as the goal is to reuse the SICS template
    files as far as possible, this has to be accepted.

    One file per scan is written. This format is designed with single
    counters in mind, this is not for area detetcor data. Use the
    NexusFileSink for such data.

    """
    parameters = {
        'templatefile': Param('Path to SICS style template file', type=str,
                              mandatory=True),
        'scaninfo': Param('Header text and nicos device for each scan point',
                          type=listof(tupleof(str, nicosdev)),
                          mandatory=True),
    }

    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
    }

    handlerclass = SINQAsciiSinkHandler
