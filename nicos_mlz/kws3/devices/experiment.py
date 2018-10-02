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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""NICOS experiment class for KWS3."""

from __future__ import absolute_import

from nicos_mlz.kws1.devices.experiment import KWSExperiment


class KWS3Experiment(KWSExperiment):
    """Experiment object customization for KWS."""

    DATA_SUFFIX = '.yaml'
    PROTO_HEADERS = ['Run', 'Pnt', 'Sel', 'Reso', 'SamPos', 'Det', 'Sample',
                     'Time', 'Cts', 'Rate']
    RUNNO_INDEX = 0
    IGNORE_SENV = ()

    def _read_data_file(self, runno, senv, fname):
        return read_det_file(runno, senv, fname)


def unquote(line):
    val = line.split(None, 1)[1].strip()
    if val.endswith('"'):
        return val[1:-1]
    return val


def read_det_file(runno, senv, fname):
    data = {'#': runno, 'Run': str(runno)}
    data['Pnt'] = fname.split('_')[1].lstrip('0')
    it = iter(open(fname))
    devname = envname = None
    for line in it:
        if line.startswith('        started:'):
            day, timeofday = unquote(line).split('T')
            data['Started'] = timeofday
            data['Day'] = day
        elif line.startswith('        environment:'):
            break
    for line in it:
        if line.startswith('        -   name:'):
            envname = line.split()[-1]
            if envname != 'etime':
                senv.add(envname)
        elif line.startswith('            value:'):
            if envname and envname != 'etime':
                data[envname] = unquote(line)
        elif line.startswith('    devices:'):
            break
    for line in it:
        if line.startswith('    -   name:'):
            devname = line.split()[-1]
        elif line.startswith('        value:'):
            if devname == 'resolution':
                data['Reso'] = unquote(line)
            elif devname == 'selector':
                data['Sel'] = unquote(line)
            elif devname == 'sample_pos':
                data['SamPos'] = unquote(line)
            elif devname == 'detector':
                data['Det'] = unquote(line)
            elif devname == 'Sample':
                data['Sample'] = unquote(line)
            elif devname == 'det_img':
                data['Cts'] = '%.2g' % float(next(it).split()[-1])
                data['Rate'] = '%.0f' % float(next(it).split()[-1])
            elif devname == 'timer':
                data['Time'] = '%.1fs' % float(next(it).split()[-1])
    return data
