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
#   Tobias Weber <tobias.weber@frm2.tum.de>
#
# *****************************************************************************

import subprocess


def txtplot(x, y, xlab, ylab, xterm_mode=False):
    """Plot data with gnuplot's dumb ASCII terminal."""
    if len(x) == 0:
        raise ValueError('Empty plot')
    if len(x) != len(y):
        raise ValueError('Unequal lengths of X and Y values')

    try:
        gnuplot = subprocess.Popen(['gnuplot', '--persist'], shell=False,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        if xterm_mode:
            cmd = ['set term xterm']
        else:
            cmd = ['set term dumb']
        cmd.append('set xlabel "' + xlab + '"')
        cmd.append('set ylabel "' + ylab + '"')
        cmd.append('plot "-" with points notitle')
        for xy in zip(x, y):
            cmd.append('%s %s' % xy)
        cmd.append('e\n')

        out = gnuplot.communicate('\n'.join(cmd))[0]
        lines = [line for line in out.splitlines() if line]
        if xterm_mode:
            lines += ['Plotting in xterm Tektronix window.',
                      '\x1b_If you can only see a lot of incomprehensible '
                      'text, use xterm instead of your current terminal '
                      'emulator.\x1b\\']
        return lines

    except OSError:
        raise RuntimeError('Could execute gnuplot for text plot')
