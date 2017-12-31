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
#   Klaudia Hradil <klaudia.hradil@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Routines for determining potential spurious peaks."""

from math import asin, pi


def check_acc_bragg(instr, h, k, l, ny, sc=None, verbose=False):
    """Calculate accidental Bragg scattering conditions for type A or type M."""
    ret = []
    res = instr._calpos([h, k, l, ny, sc, None], printout=False)
    if res is None:
        return []
    hkl = tuple(instr._calhkl([res[1], res[1], res[2], res[3]]))
    if verbose:
        ret.append('calculated lattice vector for type M spurion condition: '
                   '[%.3f, %.3f, %.3f]' % hkl)
    elif (abs(hkl[0]) % 1) + (abs(hkl[1]) % 1) + (abs(hkl[2]) % 1) < 0.01:
        ret.append('possible type M spurion with scattering vector '
                   '[%.3f, %.3f, %.3f]' % hkl)
    # type A spurion given if falls on lattice vector
    hkl = tuple(instr._calhkl([res[0], res[0], res[2], res[3]]))
    if verbose:
        ret.append('calculated lattice vector for type A spurion condition: '
                   '[%.3f, %.3f, %.3f]' % hkl)
    elif (abs(hkl[0]) % 1) + (abs(hkl[1]) % 1) + (abs(hkl[2]) % 1) < 0.01:
        ret.append('possible type A spurion with scattering vector '
                   '[%.3f, %.3f, %.3f]' % hkl)
    if verbose:
        ret.append('if one of the two above lattice vectors correspond to a '
                   'Bragg peak, accidental Bragg scattering may occur')
    return ret

def check_ho_spurions(kf, dEmin=0, dEmax=20):
    ret = []
    spurlist = []
    for nA in range(1, 6):
        for nM in range(1, 6):
            if nA != nM:
                dE = (nA**2/float(nM)**2 - 1) * 2.0725 * kf**2
                spurlist.append((dE, nM, nA, nA**2-nM**2, nM**2))
    spurlist.sort()
    for item in spurlist:
        if dEmin <= item[0] <= dEmax:
            ret.append('potential spurion at energy transfer %6.3f meV for '
                       '%d ki = %d kf (E = %d/%d Ef)' % item)
    return ret


alu_hkl = {
    'Al 1,1,1': 2.3375,
    'Al 2,0,0': 2.0242,
    'Al 2,2,0': 1.4316,
    'Al 3,1,1': 1.2207,
    'Al 2,2,2': 1.1687,
    'Al 4,0,0': 1.0123,
}

copper_hkl = {
    'Cu 1,1,1': 2.0874,
    'Cu 2,0,0': 1.8076,
    'Cu 2,2,0': 1.2781,
    'Cu 3,1,1': 1.0899,
    'Cu 2,2,2': 1.0435,
    'Cu 4,0,0': 0.9038,
}


def check_powderrays(ki, dlist, phi=None):
    lines1_list = {}
    lines2_list = {}

    for reflex, dvalue in dlist.items():
        try:
            twotheta = 2 * asin(pi / ki / dvalue) * 180 / pi
            if twotheta < 135:
                lines1_list[reflex] = twotheta
        except ValueError:
            pass
        try:
            twotheta = 2 * asin(pi / ki / 2 / dvalue) * 180 / pi
            if twotheta < 135:
                lines2_list[reflex] = twotheta
        except ValueError:
            pass

    ret = []

    if phi is not None:
        for my_line in lines1_list:
            if abs(lines1_list[my_line] - phi) < 2:
                ret.append('powder line: %s at %6.3f deg' %
                           (my_line, lines1_list[my_line]))
        for my_line in lines2_list:
            if abs(lines2_list[my_line] - phi) < 2:
                ret.append('powder line from 2ki: %s at %6.3f deg' %
                           (my_line, lines2_list[my_line]))
    else:
        ret.append('found powder lines for ki = %5.3f A-1:' % ki)
        for my_line, angle in lines1_list.items():
            ret.append(' %s at %7.3f deg' % (my_line, angle))
        ret.append('found powder lines for 2ki = %5.3f A-1:' % (2 * ki))
        for my_line, angle in lines2_list.items():
            ret.append(' %s at %7.3f deg' % (my_line, angle))
    return ret
