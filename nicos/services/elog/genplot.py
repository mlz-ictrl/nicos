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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Generate quick overview plots of scans, using Gnuplot."""

from nicos.pycompat import to_utf8

import subprocess


def plotDataset(dataset, fn, fmt):
    if not dataset.xresults:
        raise ValueError('no points in dataset')

    gpProcess = subprocess.Popen('gnuplot', shell=True, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def write(s):
        gpProcess.stdin.write(to_utf8(s))

    write('set terminal %s size 600,400 dashed\n' % fmt)
    write('set xlabel "%s (%s)"\n' % (dataset.xnames[dataset.xindex],
                                      dataset.xunits[dataset.xindex]))
    write('set title "Scan %s - %s"\n' %
          (dataset.counter, dataset.scaninfo))
    write('set grid lt 3 lc 8\n')
    write('set style increment user\n')
    for ls, pt in enumerate([7, 5, 9, 11, 13, 2, 1, 3]):
        write('set style line %d lt 1 lc %d pt %d\n' % (ls+1, ls+1, pt))

    data = []
    for xv, yv in zip(dataset.xresults, dataset.yresults):
        data.append('%s %s' % (xv[dataset.xindex], ' '.join(map(str, yv))))
    data = '\n'.join(data) + '\ne\n'

    plotterms = []
    ylabels = []
    yunits = set()
    for i, (name, info) in enumerate(zip(dataset.ynames, dataset.yvalueinfo)):
        if info.type in ('info', 'error', 'time', 'monitor'):
            continue
        term = '"-"'
        if info.errors == 'sqrt':
            term += ' using 1:%d:(sqrt($%d))' % (i+2, i+2)
        elif info.errors == 'next':
            term += ' using 1:%d:%d' % (i+2, i+3)
        else:
            term += ' using 1:%d' % (i+2)
        term += ' title "%s (%s)"' % (name, info.unit)
        if info.type == 'other':
            term += ' axes x1y2'
        term += ' with errorlines'
        plotterms.append(term)
        ylabels.append('%s (%s)' % (name, info.unit))
        yunits.add(info.unit)

    if len(ylabels) == 1:
        write('set ylabel "%s"\n' % ylabels[0])
        write('set key off\n')
    else:
        if len(yunits) == 1:
            write('set ylabel "%s"\n' % yunits.pop())
        write('set key outside below\n')

    write('set output "%s-lin.%s"\n' % (fn, fmt))
    write('plot %s\n' % ', '.join(plotterms))
    for i in range(len(plotterms)):
        write(data)

    write('set output "%s-log.%s"\n' % (fn, fmt))
    write('set logscale y\n')
    write('plot %s\n' % ', '.join(plotterms))
    for i in range(len(plotterms)):
        write(data)
    write('exit')
    gpProcess.communicate()
